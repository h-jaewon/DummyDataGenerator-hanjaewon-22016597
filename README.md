# DummyDataGenerator

> JSON 스키마 정의만으로 SQLite 더미 데이터를 즉시 생성하는 CLI 도구

한재원 (22016597)

---

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [프로젝트 구조](#프로젝트-구조)
3. [설치 방법](#설치-방법)
4. [사용 방법](#사용-방법)
5. [스키마 정의 방법](#스키마-정의-방법)
6. [지원 컬럼 타입](#지원-컬럼-타입)
7. [사용 예시](#사용-예시)

---

## 프로젝트 개요

**DummyDataGenerator**는 `schemas/` 폴더에 JSON 파일로 테이블 구조를 정의하면,
Faker 라이브러리를 이용해 한국어 더미 데이터를 자동 생성하고 SQLite DB에 삽입해주는 CLI 도구입니다.

- 별도의 코드 수정 없이 JSON 스키마만 추가하면 새 테이블 즉시 지원
- `click` 기반의 직관적인 CLI 인터페이스
- `rich` 라이브러리를 활용한 컬러풀한 터미널 출력
- `faker[ko_KR]` 로케일로 한국어 데이터 생성

---

## 프로젝트 구조

```
DummyDataGenerator/
├── main.py            # CLI 진입점 (click 그룹 및 명령어 정의)
├── generator.py       # Faker 기반 데이터 생성 로직
├── db.py              # SQLite 연결, 테이블 생성, 삽입, 조회
├── requirements.txt   # 의존 패키지 목록
├── schemas/           # 테이블 스키마 JSON 파일 디렉토리
│   ├── users.json     # 사용자 테이블 스키마
│   ├── products.json  # 상품 테이블 스키마
│   └── orders.json    # 주문 테이블 스키마
└── output/            # 생성된 SQLite DB 저장 위치 (자동 생성)
    └── dummy.db
```

### 각 파일 역할

| 파일 | 역할 |
|------|------|
| `main.py` | CLI 명령어 정의 (`generate`, `list`, `preview`, `reset`, `schemas`) |
| `generator.py` | JSON 스키마를 읽어 Faker로 데이터 생성 |
| `db.py` | SQLite 연결 관리, 테이블 자동 생성, 데이터 삽입/조회 |
| `schemas/*.json` | 테이블 구조 및 컬럼 타입 정의 |

---

## 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/h-jaewon/DummyDataGenerator-hanjaewon-22016597.git
cd DummyDataGenerator-hanjaewon-22016597
```

### 2. 가상환경 생성 및 활성화 (권장)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. 의존 패키지 설치

```bash
pip install -r requirements.txt
```

> **요구 사항:** Python 3.10 이상

---

## 사용 방법

### 전체 명령어 목록

```bash
python main.py --help
```

```
Usage: main.py [OPTIONS] COMMAND [ARGS]...

  Dummy Data Generator PoC — 스키마 기반 테스트 데이터를 DB에 삽입합니다.

Commands:
  generate  SCHEMA_NAME 스키마로 더미 데이터를 생성해 DB에 삽입합니다.
  list      DB에 있는 테이블 목록과 행 수를 출력합니다.
  preview   TABLE_NAME 테이블의 데이터를 미리 봅니다.
  reset     TABLE_NAME 테이블의 모든 데이터를 삭제합니다.
  schemas   사용 가능한 스키마 목록과 컬럼 정보를 출력합니다.
```

---

### `generate` — 더미 데이터 생성

```bash
python main.py generate <스키마명> [옵션]
```

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `-n`, `--count` | 10 | 생성할 행 수 |
| `--db` | `output/dummy.db` | SQLite DB 파일 경로 |
| `--preview` | False | 삽입 후 샘플 5건 출력 |

```bash
# users 테이블에 50건 생성 후 미리보기
python main.py generate users -n 50 --preview

# products 테이블에 20건 생성
python main.py generate products -n 20

# 커스텀 DB 경로에 저장
python main.py generate orders -n 100 --db ./my_data.db
```

---

### `list` — 테이블 현황 조회

DB에 존재하는 모든 테이블과 각 테이블의 행 수를 출력합니다.

```bash
python main.py list
```

---

### `preview` — 데이터 미리보기

특정 테이블의 데이터를 터미널에 출력합니다.

```bash
python main.py preview <테이블명> [옵션]
```

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `-n`, `--count` | 10 | 출력할 행 수 |
| `--db` | `output/dummy.db` | SQLite DB 파일 경로 |

```bash
# users 테이블 10건 미리보기
python main.py preview users

# orders 테이블 20건 미리보기
python main.py preview orders -n 20
```

---

### `reset` — 테이블 초기화

특정 테이블의 모든 데이터를 삭제합니다. 실행 전 확인 프롬프트가 표시됩니다.

```bash
python main.py reset <테이블명>
```

```bash
# users 테이블 초기화
python main.py reset users
# → "테이블의 모든 데이터를 삭제합니다. 계속할까요? [y/N]:"
```

---

### `schemas` — 스키마 정보 출력

`schemas/` 폴더에 있는 모든 JSON 스키마의 컬럼 정보를 출력합니다.

```bash
python main.py schemas
```

---

## 스키마 정의 방법

`schemas/` 폴더에 `<테이블명>.json` 파일을 생성하면 별도 코드 수정 없이 바로 사용할 수 있습니다.

### 스키마 파일 형식

```json
{
  "table": "테이블명",
  "columns": [
    {"name": "컬럼명", "type": "타입"},
    {"name": "컬럼명", "type": "타입", "args": {"옵션키": "옵션값"}}
  ]
}
```

### 예시: `schemas/users.json`

```json
{
  "table": "users",
  "columns": [
    {"name": "id",         "type": "autoincrement"},
    {"name": "name",       "type": "name"},
    {"name": "email",      "type": "email"},
    {"name": "phone",      "type": "phone_number"},
    {"name": "address",    "type": "address"},
    {"name": "birthday",   "type": "date_of_birth", "args": {"minimum_age": 18, "maximum_age": 80}},
    {"name": "created_at", "type": "date_time_this_year"}
  ]
}
```

---

## 지원 컬럼 타입

### 특수 타입 (내부 처리)

| 타입 | SQLite 타입 | 설명 | args 예시 |
|------|-------------|------|-----------|
| `autoincrement` | `INTEGER PRIMARY KEY AUTOINCREMENT` | 자동 증가 PK | 없음 |
| `random_int` | `INTEGER` | 범위 내 정수 | `{"min": 1, "max": 100}` |
| `random_element` | `TEXT` | 목록 중 하나 선택 | `{"elements": ["A", "B", "C"]}` |
| `date_of_birth` | `TEXT` | 생년월일 (ISO 형식) | `{"minimum_age": 18, "maximum_age": 80}` |
| `date_time_this_year` | `TEXT` | 올해 범위 내 날짜+시간 | 없음 |
| `sentence` | `TEXT` | 임의 문장 | `{"nb_words": 10}` |

### Faker 직접 타입

위 특수 타입 외에 [Faker 공식 문서](https://faker.readthedocs.io/en/master/providers.html)의 모든 메서드 이름을 `type` 값으로 사용할 수 있습니다.

| 타입 | 생성 데이터 예시 |
|------|------------------|
| `name` | 홍길동 |
| `email` | gildong@example.com |
| `phone_number` | 010-1234-5678 |
| `address` | 서울특별시 강남구 ... |
| `catch_phrase` | 혁신적인 클라우드 솔루션 |
| `company` | 테크놀로지 주식회사 |
| `url` | https://example.com |
| `uuid4` | 550e8400-e29b-... |

---

## 사용 예시

### 전체 워크플로우

```bash
# 1. 각 테이블에 더미 데이터 생성
python main.py generate users -n 50
python main.py generate products -n 20
python main.py generate orders -n 100

# 2. 테이블 현황 확인
python main.py list

# 3. 특정 테이블 데이터 미리보기
python main.py preview users -n 5
python main.py preview orders -n 10

# 4. 스키마 정보 확인
python main.py schemas

# 5. 특정 테이블 초기화
python main.py reset orders
```

### 새 스키마 추가 예시

`schemas/reviews.json` 파일을 생성하면 바로 사용 가능:

```json
{
  "table": "reviews",
  "columns": [
    {"name": "id",         "type": "autoincrement"},
    {"name": "user_id",   "type": "random_int",     "args": {"min": 1, "max": 50}},
    {"name": "product_id","type": "random_int",     "args": {"min": 1, "max": 20}},
    {"name": "rating",    "type": "random_int",     "args": {"min": 1, "max": 5}},
    {"name": "content",   "type": "sentence",       "args": {"nb_words": 15}},
    {"name": "created_at","type": "date_time_this_year"}
  ]
}
```

```bash
python main.py generate reviews -n 200 --preview
```

---

## 의존성

| 패키지 | 버전 | 역할 |
|--------|------|------|
| [faker](https://github.com/joke2k/faker) | 24.11.0 | 한국어 더미 데이터 생성 |
| [click](https://click.palletsprojects.com/) | 8.1.7 | CLI 프레임워크 |
| [rich](https://rich.readthedocs.io/) | 13.7.1 | 터미널 컬러 출력 및 테이블 |
