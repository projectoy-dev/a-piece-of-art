---
name: ship-issue
description: GitHub 이슈 번호를 받아 브랜치 생성 → 구현 → lint/test → 커밋 → 보안 체크 · 동작 확인 → PR → CI 대기 → squash 머지까지 한 번에 진행한다. 번호 없이 실행하면 이슈부터 만든다.
argument-hint: "[이슈번호 | 작업 설명] [--no-merge]"
disable-model-invocation: true
allowed-tools: Bash(gh auth status:*), Bash(gh repo view:*), Bash(gh issue view:*), Bash(gh issue edit:*), Bash(gh issue close:*), Bash(gh issue list:*), Bash(gh issue create:*), Bash(gh label list:*), Bash(gh label create:*), Bash(gh pr create:*), Bash(gh pr view:*), Bash(gh pr checks:*), Bash(gh pr merge:*), Bash(gh run view:*), Bash(gh run list:*), Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git fetch:*), Bash(git switch:*), Bash(git pull:*), Bash(git branch:*), Bash(git ls-remote:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(make lint:*), Bash(make format:*), Bash(make test:*), Bash(make db-up:*), Bash(make migrate:*), Bash(make db-schema:*), Bash(curl:*)
---

# 이슈 → 머지까지 한 번에

인자: $ARGUMENTS

- 첫 번째 숫자 = 이슈 번호 (`#12`, `12` 모두 허용).
- 번호가 없으면 나머지 텍스트(비어 있으면 지금까지의 대화)를 작업 설명으로 보고 2단계에서 이슈부터 만든다. 설명도 없으면 무엇을 할지 묻는다.
- `--no-merge`가 있으면 PR 생성 + CI 통과까지만 하고 머지하지 않는다.

규칙은 [`.claude/skills/CONVENTIONS.md`](../CONVENTIONS.md)를 따른다 (브랜치 이름 · 기준 브랜치 · 커밋 · PR · 머지 방식).

아래 단계는 순서대로 진행하고, 각 단계가 끝날 때마다 한 줄로 진행 상황을 알린다.
**7. 보안 체크와 8. 동작 확인은 필수다.** 둘 다 통과하기 전에는 푸시 · PR로 넘어가지 않는다.

## 1. 사전 확인

```bash
gh auth status
git status --porcelain
```

- gh 로그인이 안 되어 있으면 멈추고 `! gh auth login`을 안내한다.
- 작업 트리에 커밋 안 된 변경이 있으면 멈추고 사용자에게 어떻게 할지 묻는다 (이 이슈와 무관한 변경을 섞지 않기 위해). 임의로 stash · 삭제하지 않는다.

## 2. 이슈 확인 · 읽기

이슈 없이는 진행하지 않는다. 번호가 없으면 먼저:

1. `gh issue list --state open --search "<키워드>"`로 이미 있는 이슈인지 확인하고, 있으면 그 번호를 쓴다.
2. 없으면 [`create-issue`](../create-issue/SKILL.md) 절차(내용 정리 → 라벨 준비 → 생성 → 브랜치 전환)대로 이슈를 만들고 그 번호로 계속한다.

```bash
gh issue view <N> --json number,title,body,labels,state,comments
```

- `CLOSED`면 멈추고 알린다.
- 제목에서 타입 · 영역을 읽는다. 제목이 규칙 형식이 아니면 라벨과 본문으로 타입을 정한다.

## 3. 브랜치 준비

기준 브랜치: `origin/develop`이 있으면 `develop`, 없으면 `main`.

```bash
git fetch origin --prune
git ls-remote --exit-code --heads origin develop   # 성공하면 develop
```

이 이슈의 브랜치가 이미 있는지 먼저 확인한다 (`/create-issue`가 만든 브랜치, 중단된 작업 이어하기).

```bash
git branch -a --list "*/<N>-*"
```

- 있으면 그 브랜치로 `git switch` 하고, 이미 들어간 커밋(`git log <기준>..HEAD`)과 열린 PR(`gh pr view <브랜치>`)을 확인한 뒤 남은 단계부터 이어간다.
- 없으면 기준 브랜치를 최신으로 만들고 새 브랜치를 딴다.

```bash
git switch <기준> && git pull --ff-only
git switch -c <type>/<N>-<영문-kebab-요약>
gh issue edit <N> --add-assignee @me
```

## 4. 구현

- 이슈의 할 일 · 완료 조건을 기준으로 관련 코드를 먼저 읽고, 기존 구조 · 네이밍 · 패턴을 따라 구현한다.
- 이슈만으로 요구사항을 확정할 수 없는 **중요한** 결정(API 스펙, 데이터 모델 등)이 있으면 코드를 쓰기 전에 사용자에게 묻는다. 사소한 건 합리적으로 정하고 PR 본문에 적는다.
- 동작이 바뀌면 테스트를 추가 · 수정한다 (`server/tests/`).
- DB 작업(테이블 · 컬럼 추가 · 변경)이면 [`server/CLAUDE.md`](../../../server/CLAUDE.md)의 DB 작업 절차를 따른다: `server/docs/db-schema.md`에서 비슷한 테이블 · 컬럼 확인 → 재사용 검토 → 모든 테이블 · 컬럼에 `comment=` → `make db-schema` → `make migration m="<설명>"` 후 생성된 파일 검토. PR 본문에 `## DB 변경` 섹션을 넣는다.
- 이슈 범위 밖의 리팩터링 · 수정은 하지 않는다. 발견한 문제는 보고 때 따로 알린다.

## 5. 검사

바뀐 경로에 따라 CI와 같은 검사를 로컬에서 돌린다.

| 바뀐 곳 | 명령 |
|---|---|
| `server/` | `make format` → `make lint` → `make test` (DB가 필요하면 `make db-up` 먼저) |
| `front/` (`front/package.json`이 있을 때만) | `cd front && pnpm run lint && pnpm exec tsc --noEmit && pnpm run build` |

- 실패하면 원인을 고치고 다시 돌린다. 테스트를 건너뛰거나 지우거나 완화해서 통과시키지 않는다.
- 로컬 환경 문제(DB 미실행 등)로 돌릴 수 없으면 그 사실을 기록해 두고 CI 결과로 확인한다.

## 6. 커밋

```bash
git status
git diff
```

- 변경 파일을 확인하고 **파일을 지정해서** `git add` 한다 (`git add -A` 금지). `.env`, 로컬 산출물이 섞이지 않았는지 확인한다.
- 메시지: `<type>(<area>): <요약> (#<N>)`, 필요하면 본문. Claude 표기 줄(`Co-Authored-By`, `Claude-Session`)은 넣지 않는다.
- 논리적으로 다른 변경은 커밋을 나눈다.

## 7. 보안 체크 (필수)

푸시 전에, 기준 브랜치 대비 이 브랜치의 전체 변경분을 검토한다. 원격에 올라간 비밀값은 되돌릴 수 없으므로 반드시 푸시보다 먼저 한다.

```bash
git diff <기준>...HEAD --stat
git diff <기준>...HEAD
# 비밀값 흔적 — 결과가 나오면 한 줄씩 확인
git diff <기준>...HEAD | grep -niE '^\+.*(AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|(secret|password|passwd|token|api[_-]?key)["'\'']?\s*[:=]\s*["'\''][^"'\'' ]{8,})'
git diff <기준>...HEAD --name-only | grep -E '(^|/)\.env($|\.)|\.(pem|key|p12)$' | grep -v '\.env\.example$'
```

| 항목 | 확인 |
|---|---|
| 비밀값 | `.env` · 키 파일 · 토큰 · 비밀번호 · AWS 키가 커밋에 없는지 (`.env.example`에는 키 이름 · 로컬용 더미 값만) |
| 인증 · 권한 | 새 API · CMS 화면에 인증 · 권한 검사가 빠지지 않았는지, 응답에 비밀번호 해시 · 내부 정보가 섞이지 않는지 |
| 입력 검증 | 요청 · 폼 입력은 Pydantic으로 검증, 파일 업로드는 형식 · 용량 제한, SQL은 문자열 조합 없이 SQLAlchemy 바인딩 |
| 설정 | CORS, 쿠키(`https_only`, `same_site`), 세션 · JWT, IAM · 버킷 정책, GitHub Actions `permissions` 변경이 의도한 것인지 |
| 의존성 | `pyproject.toml` · `uv.lock` · `package.json`에 새 패키지가 있으면 이름 · 출처가 맞는지 (오타 패키지 주의), PR 본문에 기록 |

- 코드 변경이 있으면 위 표를 직접 확인한 뒤 `security-review` 스킬로 변경분을 한 번 더 검토한다.
- 문제를 찾으면 고치고 5. 검사부터 다시 한다.
- 비밀값이 커밋에 들어갔으면 커밋 이력에서도 지운다 (푸시 전이므로 해당 커밋을 고쳐 다시 커밋). **이미 푸시된 적이 있으면** 멈추고 사용자에게 알린다 — 그 비밀값은 폐기 · 교체해야 한다.

## 8. 동작 확인 (필수)

테스트 통과와 별개로, 실제로 앱을 띄워 변경한 기능이 동작하는지 확인한다.

| 바뀐 곳 | 확인 |
|---|---|
| `server/` | 서버를 띄우고 `/api/v1/health` 200, `/openapi.json` 로드, **변경한 API · CMS 화면을 실제로 호출**해 기대한 응답인지 |
| DB 변경 | `make db-up` → `make migrate`로 새 마이그레이션이 적용되는지, 서버를 띄워 그 테이블을 쓰는 기능을 호출 |
| `front/` (`front/package.json`이 있을 때만) | 빌드 후 띄워서 변경한 페이지 열람 |
| 스킬 · 훅 · 스크립트 | 바꾼 스크립트 · 명령을 샘플 입력으로 직접 실행 |
| 문서만 | 해당 없음 — 이유를 PR 본문에 기록 |

server 기동 예시 (`make dev`와 겹치지 않게 다른 포트, 백그라운드로 띄우고 끝나면 종료):

```bash
test -f server/.env || make setup
cd server && uv run uvicorn app.main:app --port 8765     # 백그라운드 실행
curl -fsS localhost:8765/api/v1/health
curl -fsS localhost:8765/openapi.json > /dev/null
curl -fsS localhost:8765/<변경한 경로>                   # 변경한 기능마다
```

- 기대와 다르게 동작하면 고치고 5. 검사부터 다시 한다.
- 확인할 수 없으면(예: Docker가 꺼져 DB를 띄울 수 없음) **건너뛰지 말고 멈추고** 사용자에게 무엇이 필요한지 알린다. 사용자가 명시적으로 건너뛰라고 한 경우에만 진행하고, PR 본문에 "미확인"과 이유를 적는다.

## 9. 푸시 · PR

```bash
git push -u origin <브랜치>
```

PR 본문은 스크래치패드 디렉터리의 임시 파일에 쓰고 `--body-file`로 넘긴다.

```markdown
Closes #<N>

## 변경 사항
- <무엇을 바꿨는지>

## 확인 방법
- <로컬에서 돌린 검사와 결과>

## 보안 체크
- <확인한 항목과 결과 — 문제 없음 / 발견 · 수정한 내용>

## 동작 확인
- <띄운 방법, 호출한 경로와 응답 — 확인하지 못한 것이 있으면 이유>

## 참고
- <구현 중 내린 결정, 범위 밖이라 남겨둔 것 — 없으면 섹션 삭제>
```

```bash
gh pr create --base <기준> --head <브랜치> --title "<이슈 제목>" --body-file <본문 파일>
```

Claude 표기 줄은 PR 본문에도 넣지 않는다. PR URL을 사용자에게 알린다.

## 10. CI 대기

```bash
gh pr checks <PR번호> --watch --fail-fast
```

- 체크가 하나도 없으면(경로 필터로 CI가 안 도는 변경) 바로 다음 단계로.
- 실패하면 `gh run view <run-id> --log-failed`로 원인을 보고 고친 뒤, 7. 보안 체크 · 8. 동작 확인을 다시 거쳐 커밋 · 푸시하고 다시 기다린다.
- 같은 실패를 3번 고쳐도 안 되면 멈추고 원인과 시도한 내용을 보고한다.

## 11. 머지

`--no-merge`면 이 단계를 건너뛰고 12로.

```bash
gh pr merge <PR번호> --squash --delete-branch --subject "<PR 제목> (#<PR번호>)"
```

- 리뷰 필수 등 브랜치 보호로 막히면 `--admin` 등으로 우회하지 않는다. 멈추고 PR URL과 막힌 이유를 보고한다.
- `Closes #N`은 기본 브랜치로 머지될 때만 이슈를 닫는다. 기준 브랜치가 저장소 기본 브랜치(`gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`)가 아니면 직접 닫고, 기본 브랜치면 `gh issue view <N> --json state`로 닫혔는지만 확인한다.

  ```bash
  gh issue close <N> --comment "#<PR번호> 로 <기준>에 머지됨"
  ```

- 로컬 정리:

  ```bash
  git switch <기준> && git pull --ff-only
  git branch -D <브랜치>   # squash 머지라 -d로는 안 지워짐 — 원격 머지 확인 후에만
  ```

## 12. 결과 보고

- 이슈 `#N` · 브랜치 · PR URL
- 커밋 목록, 검사 결과 (로컬 · CI)
- 보안 체크 · 동작 확인 결과
- 머지 여부와 머지 커밋 (또는 머지하지 않은 이유)
- 범위 밖이라 남겨둔 것, 후속으로 이슈를 만들 만한 것 (있으면 `/create-issue` 제안)
