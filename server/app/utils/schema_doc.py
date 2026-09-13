"""DB 스키마 문서 생성.

모델(app/models)의 메타데이터를 읽어 docs/db-schema.md 를 만듭니다. DB 접속 없이 동작합니다.

사용법:
    uv run python -m app.utils.schema_doc          # 문서 생성
    uv run python -m app.utils.schema_doc --check  # 문서가 모델과 다르면 종료 코드 1
"""

import argparse
import sys
from pathlib import Path

from sqlalchemy import Column, MetaData, Table, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase

from app.models import Base

SERVER_DIR = Path(__file__).resolve().parents[2]
DOC_PATH = SERVER_DIR / "docs" / "db-schema.md"
_DIALECT = postgresql.dialect()


def _sql(value: object) -> str:
    if hasattr(value, "compile"):
        return str(value.compile(dialect=_DIALECT))
    return str(value)


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _default(column: Column) -> str:
    parts = []
    if column.server_default is not None:
        parts.append(f"DB `{_sql(column.server_default.arg)}`")
    if column.default is not None:
        default = column.default
        if default.is_callable:
            parts.append("앱 (Python 함수)")
        elif default.is_scalar:
            parts.append(f"앱 `{default.arg!r}`")
        else:
            parts.append(f"앱 `{_sql(default.arg)}`")
    if column.onupdate is not None:
        parts.append(f"수정 시 앱 `{_sql(column.onupdate.arg)}`")
    return "<br>".join(parts)


def _keys(table: Table, column: Column) -> str:
    keys = []
    if column.primary_key:
        keys.append("PK")
    keys += [f"FK → `{fk.target_fullname}`" for fk in sorted(column.foreign_keys, key=str)]
    for constraint in table.constraints:
        if isinstance(constraint, UniqueConstraint) and column.name in constraint.columns:
            keys.append("UQ")
    for index in table.indexes:
        if column.name in index.columns:
            keys += ["UQ", "IX"] if index.unique else ["IX"]
    return ", ".join(dict.fromkeys(keys))


def _models(base: type[DeclarativeBase]) -> dict[str, type]:
    return {mapper.local_table.name: mapper.class_ for mapper in base.registry.mappers}


def _model_ref(model: type | None) -> str:
    if model is None:
        return "-"
    path = model.__module__.replace(".", "/") + ".py"
    return f"`{model.__name__}` (`{path}`)"


def _table_section(table: Table, metadata: MetaData, model: type | None) -> list[str]:
    lines = [
        f"### `{table.name}`",
        "",
        _cell(table.comment or "(설명 없음)"),
        "",
        f"모델: {_model_ref(model)}",
        "",
        "| 컬럼 | 타입 | NULL | 기본값 | 키 | 설명 |",
        "|---|---|---|---|---|---|",
    ]
    for column in table.columns:
        lines.append(
            f"| `{column.name}` | {column.type.compile(dialect=_DIALECT)} "
            f"| {'Y' if column.nullable else 'N'} | {_default(column)} "
            f"| {_keys(table, column)} | {_cell(column.comment or '')} |"
        )

    if table.indexes:
        lines += ["", "**인덱스**", ""]
        for index in sorted(table.indexes, key=lambda i: str(i.name)):
            columns = ", ".join(index.columns.keys())
            unique = " UNIQUE" if index.unique else ""
            lines.append(f"- `{index.name}` ({columns}){unique}")

    uniques = [c for c in table.constraints if isinstance(c, UniqueConstraint)]
    if uniques:
        lines += ["", "**UNIQUE 제약**", ""]
        for constraint in sorted(uniques, key=lambda c: str(c.name)):
            lines.append(f"- `{constraint.name}` ({', '.join(constraint.columns.keys())})")

    if table.foreign_key_constraints:
        lines += ["", "**외래키**", ""]
        for fk in sorted(table.foreign_key_constraints, key=lambda c: str(c.name)):
            columns = ", ".join(fk.column_keys)
            target = ", ".join(e.target_fullname for e in fk.elements)
            ondelete = f" ON DELETE {fk.ondelete}" if fk.ondelete else ""
            lines.append(f"- `{columns}` → `{target}`{ondelete}")

    referenced_by = sorted(
        f"{other.name}.{', '.join(fk.column_keys)}"
        for other in metadata.tables.values()
        for fk in other.foreign_key_constraints
        if fk.referred_table is table
    )
    if referenced_by:
        lines += ["", "**참조하는 곳**", ""]
        lines += [f"- `{ref}`" for ref in referenced_by]

    return lines


def render(base: type[DeclarativeBase] = Base) -> str:
    """모델 메타데이터로 스키마 문서(Markdown)를 만듭니다."""
    metadata = base.metadata
    tables = sorted(metadata.tables.values(), key=lambda t: t.name)
    models = _models(base)

    lines = [
        "# DB 스키마",
        "",
        "> 자동 생성 문서입니다. 직접 고치지 말고"
        " 모델(`server/app/models/`)의 `comment=`를 고친 뒤",
        "> `make db-schema`로 다시 만드세요.",
        ">",
        "> DB 작업 전에 비슷한 테이블 · 컬럼이 이미 있는지 이 문서에서 먼저 확인합니다"
        " — [`server/CLAUDE.md`](../CLAUDE.md)",
        "",
        "- 기본값: `DB` = DB 서버 기본값 (SQL로 넣어도 적용),"
        " `앱` = SQLAlchemy 기본값 (앱을 거칠 때만 적용)",
        "- 키: PK 기본키, FK 외래키, UQ 유일, IX 인덱스",
        "",
        "## 테이블 목록",
        "",
        "| 테이블 | 모델 | 설명 |",
        "|---|---|---|",
    ]
    for table in tables:
        model = models.get(table.name)
        name = model.__name__ if model else "-"
        comment = _cell(table.comment or "")
        lines.append(f"| [`{table.name}`](#{table.name}) | `{name}` | {comment} |")

    lines += [
        "",
        "## 컬럼 색인",
        "",
        "저장하려는 값과 이름 · 의미가 같거나 비슷한 컬럼이 이미 있는지 여기서 찾습니다.",
        "",
        "| 컬럼 | 테이블 | 타입 | 설명 |",
        "|---|---|---|---|",
    ]
    columns = sorted(
        ((column, table) for table in tables for column in table.columns),
        key=lambda pair: (pair[0].name, pair[1].name),
    )
    for column, table in columns:
        lines.append(
            f"| `{column.name}` | [`{table.name}`](#{table.name}) "
            f"| {column.type.compile(dialect=_DIALECT)} | {_cell(column.comment or '')} |"
        )

    lines += ["", "## 테이블 상세"]
    for table in tables:
        lines += ["", *_table_section(table, metadata, models.get(table.name))]

    return "\n".join(lines) + "\n"


def missing_comments(metadata: MetaData = Base.metadata) -> list[str]:
    """설명(comment)이 없는 테이블 · 컬럼 목록."""
    missing = []
    for table in sorted(metadata.tables.values(), key=lambda t: t.name):
        if not table.comment:
            missing.append(table.name)
        missing += [f"{table.name}.{c.name}" for c in table.columns if not c.comment]
    return missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.utils.schema_doc", description="DB 스키마 문서 생성")
    parser.add_argument(
        "--check", action="store_true", help="문서가 모델과 다르면 실패 (파일을 쓰지 않음)"
    )
    args = parser.parse_args(argv)

    content = render()
    current = DOC_PATH.read_text(encoding="utf-8") if DOC_PATH.exists() else ""
    relative = DOC_PATH.relative_to(SERVER_DIR)

    if missing := missing_comments():
        print(f"설명(comment=)이 없는 테이블 · 컬럼: {', '.join(missing)}", file=sys.stderr)

    if args.check:
        if current != content:
            print(
                f"{relative} 가 모델과 다릅니다. `make db-schema` 로 다시 만드세요.",
                file=sys.stderr,
            )
            return 1
        return 0

    if current == content:
        print(f"{relative} 변경 없음")
    else:
        DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
        DOC_PATH.write_text(content, encoding="utf-8")
        print(f"{relative} 갱신")
    return 0


if __name__ == "__main__":
    sys.exit(main())
