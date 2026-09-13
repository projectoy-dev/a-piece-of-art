---
name: create-issue
description: 작업 · 버그 설명을 이 저장소(projectoy-dev/a-piece-of-art)의 GitHub 이슈로 정리해 생성하고, 그 이슈의 작업 브랜치로 전환한다. "이슈 만들어줘", "이슈로 등록해줘" 같은 요청에 사용.
argument-hint: "<만들 이슈 설명>"
allowed-tools: Bash(gh auth status:*), Bash(gh repo view:*), Bash(gh issue list:*), Bash(gh issue create:*), Bash(gh issue edit:*), Bash(gh label list:*), Bash(gh label create:*), Bash(git status:*), Bash(git fetch:*), Bash(git ls-remote:*), Bash(git switch:*), Bash(git pull:*), Bash(git branch:*)
---

# GitHub 이슈 만들기

요청: $ARGUMENTS

규칙은 [`.claude/skills/CONVENTIONS.md`](../CONVENTIONS.md)를 따른다 (타입 · 영역 · 라벨 · 제목 형식).

## 1. 준비 확인

```bash
gh auth status
```

로그인이 안 되어 있으면 멈추고 사용자에게 `! gh auth login` 실행을 안내한다.

## 2. 내용 정리

- 요청(위 `$ARGUMENTS`, 비어 있으면 지금까지의 대화)에서 **무엇을 · 왜**를 뽑는다.
- 관련 코드가 있으면 직접 읽어서 파일 경로 · 현재 동작을 확인하고 본문에 적는다. 추측으로 채우지 않는다.
- 타입 1개와 영역(1개 이상)을 정한다.
- 요청에 서로 독립적인 작업이 여러 개 섞여 있으면 이슈를 나눈다. 한 이슈는 PR 하나로 끝낼 수 있는 크기로.
- 무엇을 만들어야 하는지 자체가 불분명하면 그때만 사용자에게 질문한다. 세부 사항은 합리적으로 정하고 본문에 적는다.

## 3. 중복 확인

핵심 키워드로 열린 · 닫힌 이슈를 검색한다.

```bash
gh issue list --state all --search "<키워드>" --limit 10
```

거의 같은 이슈가 열려 있으면 새로 만들지 말고 그 이슈 번호를 알려준다.

## 4. 라벨 준비

```bash
gh label list --limit 100 --json name --jq '.[].name'
```

붙일 라벨이 없으면 CONVENTIONS.md의 색 · 설명으로 만든다.

```bash
gh label create <라벨> --color <색> --description "<설명>"
```

## 5. 이슈 생성

- 제목: `<type>(<area>): <요약>`
- 본문: [`template.md`](template.md)에서 타입에 맞는 템플릿을 골라 채운다. 해당 없는 섹션은 지운다.
- 본문은 임시 파일에 쓰고 `--body-file`로 넘긴다 (따옴표 · 줄바꿈 깨짐 방지). 임시 파일은 스크래치패드 디렉터리에 둔다.

```bash
gh issue create --title "<제목>" --body-file <본문 파일> --label <타입> --label <영역>
```

## 6. 이슈 브랜치로 전환

만든 이슈에서 바로 작업을 시작할 수 있도록 그 이슈의 브랜치로 전환한다. 브랜치 이름 · 기준 브랜치는 CONVENTIONS.md를 따른다 (`/ship-issue` 3단계와 같은 동작).

- 작업 트리에 커밋 안 된 변경이 있으면(`git status --porcelain`) 전환하지 않고 사용자에게 어떻게 할지 묻는다. 임의로 stash · 삭제하지 않는다.
- 이슈를 여러 개로 나눠 만들었으면 어느 이슈로 전환할지 묻는다.
- 그 이슈의 브랜치가 이미 있으면(`git branch -a --list "*/<N>-*"`) 새로 만들지 않고 그 브랜치로 전환한다.

```bash
git fetch origin --prune
git ls-remote --exit-code --heads origin develop   # 성공하면 기준 = develop, 아니면 main
git switch <기준> && git pull --ff-only
git switch -c <type>/<N>-<영문-kebab-요약>
gh issue edit <N> --add-assignee @me
```

브랜치는 푸시하지 않는다 — 커밋이 생긴 뒤 `/ship-issue`가 푸시한다.

## 7. 결과 보고

- 이슈 번호 · 제목 · URL
- 전환한 브랜치 이름 (전환하지 않았으면 그 이유)
- 이어서 구현부터 머지까지 진행하려면 `/ship-issue <번호>`를 쓰면 된다고 한 줄 안내
