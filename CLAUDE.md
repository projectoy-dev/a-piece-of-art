# a-piece-of-art

프로젝트 구성 · 로컬 개발 방법은 [`README.md`](README.md)를 봅니다.

## git · GitHub 작업

- 이슈 · 브랜치 · 커밋 · PR 형식은 [`.claude/skills/CONVENTIONS.md`](.claude/skills/CONVENTIONS.md)를 따릅니다.
- **이슈 없이 PR을 만들지 않습니다.** PR을 만들기 전에 연결할 이슈가 있는지 확인하고, 없으면 `/create-issue` 절차로 이슈부터 만든 뒤 PR에 `Closes #<번호>`로 연결합니다.
- `develop` → `main` 반영은 PR 없이 fast-forward로 합니다. `main` 푸시는 사람이 직접 실행하고, Claude는 사전 확인 결과와 명령만 안내합니다 — [배포 절차](.claude/skills/CONVENTIONS.md#배포-develop--main)
- 커밋 메시지 · PR 본문에 Claude 표기 줄(`Co-Authored-By`, `Claude-Session`, "Generated with Claude Code")을 넣지 않습니다.
- 스킬: `/create-issue`(이슈 생성), `/ship-issue`(이슈 → 머지) — 목록은 [`.claude/skills/README.md`](.claude/skills/README.md)
