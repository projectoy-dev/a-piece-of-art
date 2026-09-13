# git 규칙 (스킬 공통)

`/create-issue`, `/ship-issue` 등 git · GitHub 작업을 하는 스킬은 이 규칙을 따릅니다.

## 타입 (type)

| 타입 | 용도 |
|---|---|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `refactor` | 동작 변화 없는 구조 개선 |
| `test` | 테스트만 추가 · 수정 |
| `docs` | 문서 |
| `chore` | 설정 · 의존성 · 기타 잡무 |
| `ci` | GitHub Actions 등 CI/CD |

## 영역 (area)

| 영역 | 경로 |
|---|---|
| `server` | `server/` (API · CMS 포함) |
| `front` | `front/` |
| `infra` | `infra/`, `scripts/`, `docker-compose.yml`, `amplify.yml` |
| `ci` | `.github/` |
| `docs` | `docs/`, `README.md` |
| `claude` | `.claude/`, `CLAUDE.md` |

여러 영역에 걸치면 가장 주된 영역 하나를 씁니다.

## 라벨

이슈에는 타입 라벨 1개 + 영역 라벨 1개 이상을 붙입니다. 저장소에 라벨이 없으면 아래 색으로 만듭니다.

| 라벨 | 색 | 설명 |
|---|---|---|
| `feat` | `0E8A16` | 새 기능 |
| `fix` | `D73A4A` | 버그 수정 |
| `refactor` | `C5DEF5` | 구조 개선 |
| `test` | `BFD4F2` | 테스트 |
| `docs` | `0075CA` | 문서 |
| `chore` | `EDEDED` | 설정 · 잡무 |
| `ci` | `5319E7` | CI/CD |
| `server` | `1D76DB` | server/ |
| `front` | `FBCA04` | front/ |
| `infra` | `B60205` | infra/ |
| `claude` | `D97757` | .claude/, CLAUDE.md |

## 이슈 제목

```
<type>(<area>): <요약>
```

예: `feat(server): 게시물 목록 조회 API 추가` — 요약은 한국어, 명사형 또는 "~ 추가/수정/제거"로 끝냅니다.

## 브랜치

```
<type>/<이슈번호>-<영문-kebab-요약>
```

예: `feat/12-post-list-api` — 요약은 영문 소문자 · 숫자 · `-`만, 40자 이내.

## 기준 브랜치

- `develop` → dev 배포, `main` → prod 배포
- 작업 브랜치는 `origin/develop`이 있으면 `develop`에서, 없으면 `main`에서 따고 같은 곳으로 PR을 보냅니다.
- `develop`을 `main`에 반영할 때는 [배포](#배포-develop--main) 절차를 따릅니다.

## 커밋

```
<type>(<area>): <요약> (#<이슈번호>)

<필요하면 본문 — 무엇을 왜 바꿨는지>
```

- 한 커밋 = 한 가지 논리적 변경
- `Co-Authored-By`, `Claude-Session` 등 Claude 표기 줄을 넣지 않습니다.
- `.env` 등 비밀값 파일은 절대 커밋하지 않습니다.

## PR

**이슈 없이 PR을 만들지 않습니다.** 스킬을 쓰든 안 쓰든, PR을 만들기 전에 항상:

1. 연결할 이슈가 있는지 확인합니다 — 브랜치 이름의 번호, 대화에서 나온 번호, `gh issue list --state open --search "<키워드>"`
2. 없으면 `/create-issue` 절차로 이슈부터 만듭니다.
3. 이슈 번호 없이 시작한 브랜치라면 PR 전에 `git branch -m <type>/<N>-<요약>`으로 이름을 맞춥니다 (이미 푸시했다면 새 이름으로 푸시하고 옛 원격 브랜치는 삭제).

- 제목: 이슈 제목과 같게
- 본문: `Closes #<이슈번호>` + 변경 요약 + 확인 방법 (Claude 표기 줄 없음)
- 머지: squash 머지, 머지 후 원격 브랜치 삭제
- `Closes #N`은 저장소의 **기본 브랜치**로 머지될 때만 이슈를 자동으로 닫습니다. 기본 브랜치가 아닌 곳으로 머지했다면 이슈를 직접 닫습니다.
  기본 브랜치 확인: `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`

## 배포 (develop → main)

`main`은 PR이나 머지 커밋 없이 **fast-forward**로만 올립니다. `main`은 항상 `develop`의 과거 커밋 중 하나가 되고, 두 브랜치 히스토리가 똑같이 유지됩니다. PR을 만들지 않으므로 이슈도 따로 만들지 않습니다.

1. 사전 확인 — Claude가 실행해서 결과를 보여줘도 됩니다.

   ```bash
   git fetch origin --prune
   git merge-base --is-ancestor origin/main origin/develop && echo ok   # ok가 안 나오면 fast-forward 불가 — 멈추고 원인 확인
   git log --oneline origin/main..origin/develop                         # main에 반영될 커밋
   git diff --name-only origin/main origin/develop                       # 바뀌는 파일
   ```

   바뀌는 파일에 아래 경로가 있으면 푸시하는 순간 prod 배포 워크플로가 실행됩니다.

   | 워크플로 | 트리거 경로 |
   |---|---|
   | `server-deploy` | `server/**`, `infra/ecs/**`, `scripts/ecs-migrate.sh`, `.github/workflows/server-*.yml` |
   | `front-deploy` | `front/**`, `amplify.yml`, `.github/workflows/front-*.yml` |

2. 푸시 — **사람이 직접 실행합니다.** Claude는 1번 결과와 아래 명령만 안내하고 직접 푸시하지 않습니다 (Claude Code에서는 앞에 `!`를 붙여 실행).

   ```bash
   git push origin origin/develop:refs/heads/main
   ```

   성공하면 `<이전 커밋>..<새 커밋>  origin/develop -> main` 줄이 출력됩니다.

3. 푸시 후

   ```bash
   git fetch origin main:main            # 로컬 main 동기화 (main을 체크아웃 중이면: git merge --ff-only origin/main)
   gh run list --branch main --limit 5   # 배포 워크플로 결과 확인
   ```

- `main`에 직접 커밋하거나 PR을 머지하지 않습니다. 긴급 수정도 `develop`에 머지한 뒤 같은 방법으로 올립니다. `main`이 `develop`보다 앞서면 fast-forward가 불가능해집니다.
