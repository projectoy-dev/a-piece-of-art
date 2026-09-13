# Claude Code 스킬

이 폴더의 스킬은 저장소에 커밋되어 팀 전체가 같이 씁니다. Claude Code에서 `/스킬이름`으로 실행합니다.

## 구조

```
.claude/
└── skills/
    ├── README.md          # 이 문서 — 스킬 목록 · 추가 방법
    ├── CONVENTIONS.md     # 스킬들이 공통으로 따르는 git 규칙 (이슈 · 브랜치 · 커밋 · PR)
    └── <스킬이름>/
        ├── SKILL.md       # 필수 — frontmatter + 실행 지침
        └── ...            # 선택 — 템플릿, 스크립트 등 SKILL.md에서 참조하는 파일
```

## 스킬 목록

| 스킬 | 하는 일 |
|---|---|
| `/create-issue <설명>` | 설명을 GitHub 이슈로 정리해서 생성 (라벨 · 템플릿 적용) |
| `/ship-issue [이슈번호 \| 작업 설명] [--no-merge]` | 이슈 번호로 브랜치 생성 → 구현 → 검사 → 커밋 → PR → CI 대기 → 머지. 번호 없이 실행하면 이슈부터 생성 |

## 준비

- GitHub CLI 로그인: `gh auth login` (Claude Code 안에서는 `! gh auth login`)
- server 검사용: `make setup`, 테스트에 DB가 필요하면 `make db-up`

## 스킬 추가하기

1. `.claude/skills/<스킬이름>/SKILL.md` 생성 (폴더 이름 = 명령어 이름, 영문 kebab-case)
2. frontmatter 작성

   ```yaml
   ---
   name: 스킬이름
   description: 언제 쓰는 스킬인지 한 줄 — Claude가 자동 실행 여부를 판단할 때 읽습니다
   argument-hint: "<인자 설명>"          # 선택 — 자동완성에 표시
   disable-model-invocation: true        # 선택 — 사용자가 직접 입력할 때만 실행 (머지 · 배포처럼 되돌리기 어려운 작업)
   allowed-tools: Bash(gh issue:*)       # 선택 — 스킬 실행 중 확인 없이 허용할 도구
   ---
   ```

3. 본문에 단계별 지침 작성. 인자는 `$ARGUMENTS`로 받습니다.
4. git 관련 스킬이면 [`CONVENTIONS.md`](CONVENTIONS.md) 규칙을 따르도록 참조합니다.
5. 위 스킬 목록 표에 추가합니다.
