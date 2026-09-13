---
name: ship-issue
description: GitHub 이슈 번호를 받아 브랜치 생성 → 구현 → lint/test → 커밋 → PR → CI 대기 → squash 머지까지 한 번에 진행한다. 번호 없이 실행하면 이슈부터 만든다.
argument-hint: "[이슈번호 | 작업 설명] [--no-merge]"
disable-model-invocation: true
allowed-tools: Bash(gh auth status:*), Bash(gh repo view:*), Bash(gh issue view:*), Bash(gh issue edit:*), Bash(gh issue close:*), Bash(gh issue list:*), Bash(gh issue create:*), Bash(gh label list:*), Bash(gh label create:*), Bash(gh pr create:*), Bash(gh pr view:*), Bash(gh pr checks:*), Bash(gh pr merge:*), Bash(gh run view:*), Bash(gh run list:*), Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git fetch:*), Bash(git switch:*), Bash(git pull:*), Bash(git branch:*), Bash(git ls-remote:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(make lint:*), Bash(make format:*), Bash(make test:*)
---

# 이슈 → 머지까지 한 번에

인자: $ARGUMENTS

- 첫 번째 숫자 = 이슈 번호 (`#12`, `12` 모두 허용).
- 번호가 없으면 나머지 텍스트(비어 있으면 지금까지의 대화)를 작업 설명으로 보고 2단계에서 이슈부터 만든다. 설명도 없으면 무엇을 할지 묻는다.
- `--no-merge`가 있으면 PR 생성 + CI 통과까지만 하고 머지하지 않는다.

규칙은 [`.claude/skills/CONVENTIONS.md`](../CONVENTIONS.md)를 따른다 (브랜치 이름 · 기준 브랜치 · 커밋 · PR · 머지 방식).

아래 단계는 순서대로 진행하고, 각 단계가 끝날 때마다 한 줄로 진행 상황을 알린다.

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
2. 없으면 [`create-issue`](../create-issue/SKILL.md) 절차(내용 정리 → 라벨 준비 → 생성)대로 이슈를 만들고 그 번호로 계속한다.

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

이 이슈의 브랜치가 이미 있는지 먼저 확인한다 (중단된 작업 이어하기).

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
- server 모델을 바꿨으면 마이그레이션을 만든다: `make migration m="<설명>"` 후 생성된 파일을 검토.
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

## 7. 푸시 · PR

```bash
git push -u origin <브랜치>
```

PR 본문은 스크래치패드 디렉터리의 임시 파일에 쓰고 `--body-file`로 넘긴다.

```markdown
Closes #<N>

## 변경 사항
- <무엇을 바꿨는지>

## 확인 방법
- <로컬에서 돌린 검사와 결과, 수동 확인 방법>

## 참고
- <구현 중 내린 결정, 범위 밖이라 남겨둔 것 — 없으면 섹션 삭제>
```

```bash
gh pr create --base <기준> --head <브랜치> --title "<이슈 제목>" --body-file <본문 파일>
```

Claude 표기 줄은 PR 본문에도 넣지 않는다. PR URL을 사용자에게 알린다.

## 8. CI 대기

```bash
gh pr checks <PR번호> --watch --fail-fast
```

- 체크가 하나도 없으면(경로 필터로 CI가 안 도는 변경) 바로 다음 단계로.
- 실패하면 `gh run view <run-id> --log-failed`로 원인을 보고 고친 뒤 커밋 · 푸시하고 다시 기다린다.
- 같은 실패를 3번 고쳐도 안 되면 멈추고 원인과 시도한 내용을 보고한다.

## 9. 머지

`--no-merge`면 이 단계를 건너뛰고 10으로.

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

## 10. 결과 보고

- 이슈 `#N` · 브랜치 · PR URL
- 커밋 목록, 검사 결과 (로컬 · CI)
- 머지 여부와 머지 커밋 (또는 머지하지 않은 이유)
- 범위 밖이라 남겨둔 것, 후속으로 이슈를 만들 만한 것 (있으면 `/create-issue` 제안)
