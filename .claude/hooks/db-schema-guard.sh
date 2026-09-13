#!/usr/bin/env bash
# server DB 작업 하네스 — .claude/settings.json 의 hooks 에서 호출합니다.
#
#   pre  (PreToolUse,  Edit|Write|MultiEdit)
#     - 이번 세션에서 server/docs/db-schema.md 를 읽기 전에는 모델 · 마이그레이션 수정을 막음
#     - 자동 생성 문서인 db-schema.md 직접 수정을 막음
#   post (PostToolUse, Read|Edit|Write|MultiEdit)
#     - db-schema.md 를 읽으면 세션별로 기록
#     - 모델을 고치면 db-schema.md 를 다시 만들고 결과를 Claude에게 전달
#
# server/app/models/, server/alembic/versions/, server/docs/db-schema.md 외의 파일에는 아무것도 하지 않습니다.
set -uo pipefail

mode="${1:-}"
input="$(cat)"
file="$(jq -r '.tool_input.file_path // empty' <<<"$input")"
[ -z "$file" ] && exit 0

case "$file" in
  */server/app/models/*.py) target=model ;;
  */server/alembic/versions/*.py) target=migration ;;
  */server/docs/db-schema.md) target=doc ;;
  *) exit 0 ;;
esac

tool="$(jq -r '.tool_name // empty' <<<"$input")"
session="$(jq -r '.session_id // "unknown"' <<<"$input")"
root="${CLAUDE_PROJECT_DIR:-${file%%/server/*}}"
doc="$root/server/docs/db-schema.md"
marker="${TMPDIR:-/tmp}/claude-db-schema-read/$session"

context() {
  jq -n --arg ctx "$1" '{hookSpecificOutput: {hookEventName: "PostToolUse", additionalContext: $ctx}}'
}

if [ "$mode" = pre ]; then
  if [ "$target" = doc ]; then
    echo "server/docs/db-schema.md 는 자동 생성 문서라 직접 고치지 않습니다. 모델(server/app/models/)의 comment= 를 고친 뒤 make db-schema 로 다시 만드세요." >&2
    exit 2
  fi
  # 문서가 아직 없으면(첫 생성 전) 막지 않음
  if [ -f "$doc" ] && [ ! -f "$marker" ]; then
    echo "DB 작업 전에 server/docs/db-schema.md 를 먼저 읽고, 만들거나 바꾸려는 테이블 · 컬럼과 같거나 비슷한 것이 이미 있는지 확인하세요 (server/CLAUDE.md 'DB 작업' 절차). 문서를 읽으면 이 수정이 허용됩니다." >&2
    exit 2
  fi
  exit 0
fi

if [ "$mode" = post ]; then
  if [ "$tool" = Read ] && [ "$target" = doc ]; then
    mkdir -p "$(dirname "$marker")" && touch "$marker"
    exit 0
  fi
  if [ "$tool" != Read ] && [ "$target" = model ]; then
    if out="$(cd "$root/server" && uv run --quiet python -m app.utils.schema_doc 2>&1)"; then
      context "모델이 바뀌어 server/docs/db-schema.md 를 다시 만들었습니다 ($out). 모델 · 마이그레이션(make migration m=\"...\") · 스키마 문서를 같은 커밋에 넣으세요."
    else
      context "server/docs/db-schema.md 재생성에 실패했습니다. 모델 수정을 마친 뒤 make db-schema 를 실행하세요: $out"
    fi
  fi
  exit 0
fi
