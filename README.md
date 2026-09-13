# a-piece-of-art

사용자용 웹(front)과 API + CMS 서버(server)로 구성된 프로젝트입니다.

| 폴더 | 내용 | 배포 |
|---|---|---|
| `front/` | 사용자용 웹 (Next.js) — 별도 담당자 구성 | GitHub Actions → AWS Amplify |
| `server/` | FastAPI: `/api/v1` JSON API + `/cms` 관리자 화면 | GitHub Actions → ECR → ECS Fargate |
| `infra/` | ECS 태스크 정의, IAM 정책, AWS 리소스 목록 | — |
| `docs/` | 설계 문서 | — |

전체 구조와 결정 배경: [`docs/directory-structure.html`](docs/directory-structure.html) (브라우저로 열기)

## 로컬 개발 (server)

필요 도구: [uv](https://docs.astral.sh/uv/), Docker

```bash
make setup      # 의존성 설치 + .env 파일 생성
make db-up      # PostgreSQL 실행 (docker compose)
make migrate    # 마이그레이션 적용
make admin email=admin@example.com password=원하는비밀번호   # CMS 관리자 생성
make dev        # http://localhost:8000
```

| 주소 | 내용 |
|---|---|
| http://localhost:8000/api/v1/health | API 상태 확인 |
| http://localhost:8000/docs | API 문서 (OpenAPI) |
| http://localhost:8000/cms/ | CMS 관리자 화면 |

그 밖의 명령은 `make help`로 확인합니다.

## DB 스키마

테이블 · 컬럼 · 설명은 [`server/docs/db-schema.md`](server/docs/db-schema.md) 한 곳에서 봅니다. 모델(`server/app/models/`)에서 자동으로 만드는 문서라 직접 고치지 않습니다.

```bash
make db-schema  # 모델을 고친 뒤 문서 다시 만들기 — 문서가 모델과 다르면 server CI가 실패
```

DB 작업 절차(비슷한 테이블 · 컬럼 확인 → 재사용 검토 → 설명 필수)는 [`server/CLAUDE.md`](server/CLAUDE.md)를 봅니다.

## 배포

- `develop` 브랜치 → dev, `main` 브랜치 → prod
- 비밀값은 AWS Parameter Store에만 둡니다. 저장소에는 `.env.example`(키 목록)만 커밋합니다.
- AWS 리소스 준비 절차: [`infra/README.md`](infra/README.md)
