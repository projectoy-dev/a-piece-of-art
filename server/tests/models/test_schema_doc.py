"""DB 스키마 규칙 — 모든 테이블 · 컬럼에 설명이 있고, docs/db-schema.md 가 모델과 같아야 합니다."""

import pytest

from app.utils.schema_doc import DOC_PATH, missing_comments, render


def test_all_tables_and_columns_have_comment():
    if missing := missing_comments():
        pytest.fail(f"설명(comment=)이 없는 테이블 · 컬럼: {', '.join(missing)}")


def test_schema_doc_is_up_to_date():
    current = DOC_PATH.read_text(encoding="utf-8") if DOC_PATH.exists() else ""
    if current != render():
        pytest.fail("docs/db-schema.md 가 모델과 다릅니다. `make db-schema` 로 다시 만드세요.")
