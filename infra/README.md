# infra

AWS 배포 설정 중 코드로 관리하는 파일과, 콘솔에서 수동으로 만드는 리소스 목록입니다.
전체 구조와 배경은 [`docs/directory-structure.html`](../docs/directory-structure.html)의 "배포 · CI/CD", "이미지 저장 · 전송", "보안 정보 관리" 섹션을 참고하세요.

- 리전: `ap-northeast-2` (서울). CloudFront용 ACM 인증서만 `us-east-1`
- 환경: `dev` (`develop` 브랜치), `prod` (`main` 브랜치) — 환경마다 리소스 한 세트

## 파일

| 파일 | 용도 |
|---|---|
| `ecs/task-definition.{dev,prod}.json` | ECS 태스크 정의. `image`는 배포 시 GitHub Actions가 주입, 비밀값은 Parameter Store ARN으로 참조 |
| `iam/github-oidc-trust.json` | GitHub Actions 배포 역할의 신뢰 정책 (OIDC) |
| `iam/github-deploy-policy.json` | 배포 역할 권한: ECR push, ECS 배포 · 마이그레이션 태스크 실행, Amplify 빌드 요청 |
| `iam/ecs-execution-policy.json` | ECS 태스크 **실행** 역할 추가 권한: Parameter Store 읽기, KMS 복호화 |
| `iam/ecs-task-policy.json` | ECS **태스크** 역할 권한: 이미지 버킷 업로드 · 삭제 |

JSON 안의 `<ACCOUNT_ID>`, `<GITHUB_OWNER>`, `<GITHUB_REPO>`, `<AMPLIFY_APP_ID>`, `<ENV>`, `<KMS_KEY_ID>`, `<MEDIA_BUCKET>`은 실제 값으로 바꿔서 사용합니다.

> - 실행 역할에는 AWS 관리형 정책 `AmazonECSTaskExecutionRolePolicy`(ECR pull, CloudWatch Logs)도 함께 붙입니다.
> - SecureString을 기본 키(`aws/ssm`)로 암호화했다면 `ecs-execution-policy.json`의 KMS 문은 빼도 됩니다. 고객 관리형 키를 쓸 때만 필요합니다.

## 리소스 생성 순서 (dev 먼저, 안정되면 prod)

1. **IAM**
   - GitHub OIDC 공급자 등록 (`token.actions.githubusercontent.com`, audience `sts.amazonaws.com`)
   - 배포 역할 생성: 신뢰 정책 `github-oidc-trust.json` + 권한 `github-deploy-policy.json`
   - ECS 실행 역할 `a-piece-of-art-{env}-ecs-execution`, 태스크 역할 `a-piece-of-art-{env}-ecs-task`
2. **네트워크 · DB**
   - VPC (퍼블릭 서브넷: ALB / 프라이빗 서브넷: ECS, RDS)
   - RDS for PostgreSQL: 프라이빗 서브넷, ECS 보안 그룹에서만 5432 허용, 자동 백업 (prod는 Multi-AZ)
3. **컨테이너**
   - ECR 저장소 `a-piece-of-art-server` (수명 주기 정책으로 오래된 이미지 정리)
   - CloudWatch 로그 그룹 `/ecs/a-piece-of-art-{env}-server`
   - ECS 클러스터, ALB + 대상 그룹 (health check `/api/v1/health`, 포트 8000)
   - ALB 리스너 규칙: `/cms/*` 는 사무실 IP만 허용 (또는 AWS WAF IP 세트)
4. **이미지 저장소**
   - S3 버킷: 퍼블릭 액세스 전부 차단
   - CloudFront 배포: 원본 S3 + OAC, 대체 도메인 `img.example.com`, 인증서는 **us-east-1** ACM
   - 버킷 정책: 해당 CloudFront 배포(OAC)의 `s3:GetObject`만 허용
5. **Route 53**: `example.com` → Amplify, `api.example.com` → ALB, `img.example.com` → CloudFront
6. **Parameter Store** (아래 표) 값 등록
7. **ECS 서비스** 생성: 태스크 정의 등록 후 서비스 생성 (프라이빗 서브넷, 롤링 배포 + 배포 서킷 브레이커)
8. **Amplify**: 저장소 연결, 브랜치 `main`·`develop` 추가, **자동 빌드 OFF**, 환경변수 `AMPLIFY_MONOREPO_APP_ROOT=front`
9. **GitHub Variables** (아래 표) 등록 후 `develop`에 push해서 파이프라인 확인

## Parameter Store

경로 규칙: `/a-piece-of-art/{env}/server/{KEY}`

| 키 | 타입 | 예시 |
|---|---|---|
| `DATABASE_URL` | SecureString | `postgresql+asyncpg://user:pass@<rds-endpoint>:5432/app` |
| `SECRET_KEY` | SecureString | 32자 이상 랜덤 문자열 (JWT 서명) |
| `CMS_SESSION_SECRET` | SecureString | 32자 이상 랜덤 문자열 (CMS 세션 쿠키 서명) |
| `CORS_ORIGINS` | String | `["https://example.com"]` (JSON 배열) |
| `STORAGE_BACKEND` | String | `s3` |
| `S3_BUCKET` | String | 이미지 버킷명 |
| `MEDIA_BASE_URL` | String | `https://img.example.com` |

값을 바꾼 뒤에는 `aws ecs update-service --cluster <클러스터> --service <서비스> --force-new-deployment`로 태스크를 새로 띄워야 반영됩니다.

## GitHub Variables

AWS 액세스 키는 저장하지 않습니다 (OIDC 사용). 아래는 모두 비밀이 아닌 값입니다.

| 위치 | 이름 | 값 |
|---|---|---|
| Repository | `SERVER_DEPLOY_ENABLED` | `true` — AWS 준비가 끝나면 등록 (없으면 server 배포 건너뜀) |
| Repository | `FRONT_DEPLOY_ENABLED` | `true` — Amplify 준비가 끝나면 등록 (없으면 front 배포 건너뜀) |
| Repository | `AMPLIFY_APP_ID` | Amplify 앱 ID |
| Environment `dev` / `prod` | `AWS_DEPLOY_ROLE_ARN` | 배포 역할 ARN |
| Environment `dev` / `prod` | `APP_ENV` | `dev` / `prod` (태스크 정의 파일 선택) |
| Environment `dev` / `prod` | `ECS_CLUSTER`, `ECS_SERVICE` | 클러스터 · 서비스 이름 |
| Environment `dev` / `prod` | `ECS_SUBNETS`, `ECS_SECURITY_GROUPS` | 마이그레이션 태스크용 서브넷 · 보안 그룹 ID (쉼표 구분) |
