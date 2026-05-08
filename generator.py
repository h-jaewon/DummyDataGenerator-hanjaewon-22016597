"""Dummy data generator: Faker 기반으로 스키마 정의에 따라 데이터를 생성한다."""

import json
from pathlib import Path
from faker import Faker

fake = Faker("ko_KR")

# Faker 메서드 중 args를 직접 전달하면 안 되는 타입은 별도 처리
_SPECIAL_HANDLERS = {
    "autoincrement": None,  # DB에서 처리
    "random_int": lambda args: fake.random_int(**args),
    "random_element": lambda args: fake.random_element(**args),
    "date_of_birth": lambda args: fake.date_of_birth(**args).isoformat(),
    "date_time_this_year": lambda _: fake.date_time_this_year().isoformat(sep=" "),
    "sentence": lambda args: fake.sentence(**args),
}


def _generate_value(col: dict) -> object:
    col_type = col["type"]
    args = col.get("args", {})

    if col_type == "autoincrement":
        return None

    if col_type in _SPECIAL_HANDLERS:
        return _SPECIAL_HANDLERS[col_type](args)

    method = getattr(fake, col_type, None)
    if method is None:
        raise ValueError(f"지원하지 않는 컬럼 타입: '{col_type}'")

    return method(**args) if args else method()


def generate_rows(schema: dict, count: int) -> list[dict]:
    """스키마 기준으로 count개의 행 데이터를 반환한다."""
    columns = schema["columns"]
    rows = []
    for _ in range(count):
        row = {}
        for col in columns:
            if col["type"] == "autoincrement":
                continue
            row[col["name"]] = _generate_value(col)
        rows.append(row)
    return rows


def load_schema(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)
