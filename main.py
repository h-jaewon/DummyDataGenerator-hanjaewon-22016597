"""gen-dummy-poc CLI 진입점."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich import box

import db as database
import generator

SCHEMAS_DIR = Path(__file__).parent / "schemas"
DEFAULT_DB = Path(__file__).parent / "output" / "dummy.db"

console = Console()


def _available_schemas() -> list[str]:
    return [p.stem for p in SCHEMAS_DIR.glob("*.json")]


# ──────────────────────────────────────────────
# CLI 그룹
# ──────────────────────────────────────────────

@click.group()
def cli():
    """Dummy Data Generator PoC — 스키마 기반 테스트 데이터를 DB에 삽입합니다."""


# ──────────────────────────────────────────────
# generate 명령
# ──────────────────────────────────────────────

@cli.command()
@click.argument("schema_name")
@click.option("-n", "--count", default=10, show_default=True, help="생성할 행 수")
@click.option("--db", "db_path", default=str(DEFAULT_DB), show_default=True, help="SQLite DB 경로")
@click.option("--preview", is_flag=True, default=False, help="삽입 후 샘플 5건 출력")
def generate(schema_name: str, count: int, db_path: str, preview: bool):
    """SCHEMA_NAME 스키마로 더미 데이터를 생성해 DB에 삽입합니다.

    \b
    사용 가능한 스키마: users, products, orders
    예) python main.py generate users -n 50 --preview
    """
    schema_path = SCHEMAS_DIR / f"{schema_name}.json"
    if not schema_path.exists():
        console.print(f"[red]스키마 파일을 찾을 수 없습니다: {schema_path}[/red]")
        console.print(f"사용 가능한 스키마: {', '.join(_available_schemas())}")
        raise SystemExit(1)

    schema = generator.load_schema(schema_path)
    table = schema["table"]

    console.print(f"[bold cyan]● 스키마:[/bold cyan] {schema_name}  [bold cyan]● 테이블:[/bold cyan] {table}  [bold cyan]● 생성 수:[/bold cyan] {count}")

    rows = generator.generate_rows(schema, count)

    conn = database.open_db(Path(db_path))
    database.ensure_table(conn, schema)
    inserted = database.insert_rows(conn, table, rows)

    total = database.count_rows(conn, table)
    console.print(f"[green]✔ {inserted}건 삽입 완료[/green]  (테이블 누적: {total}건)")

    if preview:
        samples = database.preview_rows(conn, table, limit=5)
        _print_table(f"{table} — 최근 5건 미리보기", samples)

    conn.close()


# ──────────────────────────────────────────────
# list 명령
# ──────────────────────────────────────────────

@cli.command(name="list")
@click.option("--db", "db_path", default=str(DEFAULT_DB), show_default=True, help="SQLite DB 경로")
def list_tables(db_path: str):
    """DB에 있는 테이블 목록과 행 수를 출력합니다."""
    conn = database.open_db(Path(db_path))
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cur.fetchall()]

    if not tables:
        console.print("[yellow]DB에 테이블이 없습니다.[/yellow]")
        conn.close()
        return

    t = Table(title="DB 테이블 현황", box=box.ROUNDED)
    t.add_column("테이블", style="cyan")
    t.add_column("행 수", justify="right", style="green")
    for tbl in tables:
        count = database.count_rows(conn, tbl)
        t.add_row(tbl, str(count))
    console.print(t)
    conn.close()


# ──────────────────────────────────────────────
# preview 명령
# ──────────────────────────────────────────────

@cli.command()
@click.argument("table_name")
@click.option("-n", "--count", default=10, show_default=True, help="미리볼 행 수")
@click.option("--db", "db_path", default=str(DEFAULT_DB), show_default=True, help="SQLite DB 경로")
def preview(table_name: str, count: int, db_path: str):
    """TABLE_NAME 테이블의 데이터를 미리 봅니다."""
    conn = database.open_db(Path(db_path))
    rows = database.preview_rows(conn, table_name, limit=count)
    conn.close()

    if not rows:
        console.print(f"[yellow]{table_name} 테이블에 데이터가 없습니다.[/yellow]")
        return

    _print_table(f"{table_name} 미리보기 ({len(rows)}건)", rows)


# ──────────────────────────────────────────────
# reset 명령
# ──────────────────────────────────────────────

@cli.command()
@click.argument("table_name")
@click.option("--db", "db_path", default=str(DEFAULT_DB), show_default=True, help="SQLite DB 경로")
@click.confirmation_option(prompt="테이블의 모든 데이터를 삭제합니다. 계속할까요?")
def reset(table_name: str, db_path: str):
    """TABLE_NAME 테이블의 모든 데이터를 삭제합니다."""
    conn = database.open_db(Path(db_path))
    conn.execute(f"DELETE FROM {table_name}")
    conn.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
    conn.commit()
    conn.close()
    console.print(f"[green]✔ {table_name} 테이블 초기화 완료[/green]")


# ──────────────────────────────────────────────
# schemas 명령
# ──────────────────────────────────────────────

@cli.command()
def schemas():
    """사용 가능한 스키마 목록과 컬럼 정보를 출력합니다."""
    for name in _available_schemas():
        schema = generator.load_schema(SCHEMAS_DIR / f"{name}.json")
        t = Table(title=f"스키마: {name}  →  테이블: {schema['table']}", box=box.SIMPLE_HEAD)
        t.add_column("컬럼", style="cyan")
        t.add_column("타입", style="magenta")
        t.add_column("옵션", style="dim")
        for col in schema["columns"]:
            args_str = json.dumps(col.get("args", {}), ensure_ascii=False) if col.get("args") else ""
            t.add_row(col["name"], col["type"], args_str)
        console.print(t)


# ──────────────────────────────────────────────
# 내부 유틸
# ──────────────────────────────────────────────

def _print_table(title: str, rows: list[dict]) -> None:
    if not rows:
        return
    t = Table(title=title, box=box.ROUNDED)
    for col in rows[0].keys():
        t.add_column(col, style="cyan", overflow="fold", max_width=30)
    for row in rows:
        t.add_row(*[str(v) for v in row.values()])
    console.print(t)


if __name__ == "__main__":
    cli()
