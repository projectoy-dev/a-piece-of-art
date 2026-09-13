# server

FastAPI: `/api/v1` JSON API + `/cms` 관리자 화면. 계층은 `api` · `cms` → `services` → `repositories` → `models`입니다.
명령은 저장소 루트에서 `make help`로 확인합니다.

## DB 작업

테이블 · 컬럼을 추가 · 변경하거나 새 데이터를 어디에 저장할지 정할 때는 항상 아래 순서를 따릅니다. 목적은 비슷한 테이블을 또 만들어 같은 데이터를 여러 곳에 중복으로 쌓지 않는 것입니다.

1. **스키마 문서 확인** — [`docs/db-schema.md`](docs/db-schema.md)를 읽습니다. `컬럼 색인`에서 저장하려는 값과 이름 · 의미가 같거나 비슷한 컬럼을 찾습니다 (예: 이미지면 `image_key`, `profile_image_key`).
2. **재사용 먼저** — 아래 순서로 검토하고, 앞 단계에서 해결되면 거기서 멈춥니다.
   1. 기존 컬럼을 그대로 사용
   2. 기존 테이블에 컬럼 추가
   3. 기존 테이블과 FK로 연결되는 새 테이블

   다른 테이블에서 조인 · 계산으로 얻을 수 있는 값은 복사해서 저장하지 않습니다.
3. **설명 필수** — 새 테이블(`__table_args__ = {"comment": "..."}`)과 모든 컬럼(`comment="..."`)에 설명을 답니다. 설명은 DB `COMMENT`로도 들어가고, 없으면 테스트가 실패합니다.
4. **문서 · 마이그레이션** — 모델을 고친 뒤:

   ```bash
   make db-schema                  # docs/db-schema.md 재생성 (Claude Code에서는 훅이 자동 실행)
   make migration m="<변경 설명>"   # 생성된 파일을 반드시 검토
   ```

   모델 · 마이그레이션 · 스키마 문서는 같은 커밋에 넣습니다. 문서가 모델과 다르면 server CI가 실패합니다.
5. **PR 기록** — PR 본문에 `## DB 변경` 섹션을 넣습니다: 바뀐 테이블 · 컬럼, 확인한 비슷한 테이블 · 컬럼, (새로 만들었다면) 재사용하지 않은 이유.

### 모델 규칙

- 테이블 이름은 복수형 snake_case (`artworks`), FK 컬럼은 `<단수형>_id` + `ondelete` 명시
- 파일은 URL이 아니라 저장소 키를 `*_key` 컬럼에 저장하고, URL은 `app.utils.media.media_url()`로 만듭니다.
- 불리언은 `is_*`, 생성 · 수정 시각은 직접 만들지 말고 `TimestampMixin`을 씁니다.
- 관계는 `lazy="raise"` 또는 `lazy="selectin"` — 비동기 환경이라 암묵적 지연 로딩을 쓰지 않습니다.
- 새 모델은 `app/models/__init__.py`에서 import합니다 (alembic autogenerate와 스키마 문서가 같은 메타데이터를 봅니다).

### Claude Code 훅

`.claude/hooks/db-schema-guard.sh` (`.claude/settings.json`에 등록)가 server DB 파일에만 동작합니다.

- 세션에서 `docs/db-schema.md`를 읽기 전에는 `app/models/`, `alembic/versions/` 수정이 막힙니다.
- 모델을 고치면 `docs/db-schema.md`를 자동으로 다시 만듭니다.
- 자동 생성 문서인 `docs/db-schema.md`를 직접 고치는 것은 막힙니다.
