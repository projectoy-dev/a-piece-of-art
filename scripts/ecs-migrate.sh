#!/usr/bin/env bash
# 배포 전 DB 마이그레이션을 ECS 일회성 태스크로 실행합니다.
#
# 사용법: ./scripts/ecs-migrate.sh <렌더링된 task-definition.json 경로>
# 필요한 환경변수:
#   ECS_CLUSTER          ECS 클러스터 이름
#   ECS_SUBNETS          태스크를 띄울 프라이빗 서브넷 ID (쉼표 구분)
#   ECS_SECURITY_GROUPS  태스크 보안 그룹 ID (쉼표 구분, RDS 접근 허용된 그룹)
set -euo pipefail

TD_FILE="${1:?task definition 파일 경로가 필요합니다}"
: "${ECS_CLUSTER:?ECS_CLUSTER 환경변수가 필요합니다}"
: "${ECS_SUBNETS:?ECS_SUBNETS 환경변수가 필요합니다}"
: "${ECS_SECURITY_GROUPS:?ECS_SECURITY_GROUPS 환경변수가 필요합니다}"

echo "▶ 태스크 정의 등록"
TD_ARN=$(aws ecs register-task-definition \
  --cli-input-json "file://${TD_FILE}" \
  --query 'taskDefinition.taskDefinitionArn' --output text)
echo "  ${TD_ARN}"

echo "▶ 마이그레이션 태스크 실행 (alembic upgrade head)"
TASK_ARN=$(aws ecs run-task \
  --cluster "${ECS_CLUSTER}" \
  --task-definition "${TD_ARN}" \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[${ECS_SUBNETS}],securityGroups=[${ECS_SECURITY_GROUPS}],assignPublicIp=DISABLED}" \
  --overrides '{"containerOverrides":[{"name":"server","command":["alembic","upgrade","head"]}]}' \
  --query 'tasks[0].taskArn' --output text)
echo "  ${TASK_ARN}"

echo "▶ 태스크 종료 대기"
aws ecs wait tasks-stopped --cluster "${ECS_CLUSTER}" --tasks "${TASK_ARN}"

EXIT_CODE=$(aws ecs describe-tasks \
  --cluster "${ECS_CLUSTER}" --tasks "${TASK_ARN}" \
  --query 'tasks[0].containers[?name==`server`].exitCode | [0]' --output text)

if [ "${EXIT_CODE}" != "0" ]; then
  echo "✖ 마이그레이션 실패 (exit code: ${EXIT_CODE}) — CloudWatch Logs에서 원인을 확인하세요."
  exit 1
fi
echo "✔ 마이그레이션 완료"
