# DB 스키마

> 자동 생성 문서입니다. 직접 고치지 말고 모델(`server/app/models/`)의 `comment=`를 고친 뒤
> `make db-schema`로 다시 만드세요.
>
> DB 작업 전에 비슷한 테이블 · 컬럼이 이미 있는지 이 문서에서 먼저 확인합니다 — [`server/CLAUDE.md`](../CLAUDE.md)

- 기본값: `DB` = DB 서버 기본값 (SQL로 넣어도 적용), `앱` = SQLAlchemy 기본값 (앱을 거칠 때만 적용)
- 키: PK 기본키, FK 외래키, UQ 유일, IX 인덱스

## 테이블 목록

| 테이블 | 모델 | 설명 |
|---|---|---|
| [`artists`](#artists) | `Artist` | 작가 |
| [`artworks`](#artworks) | `Artwork` | 작품 |
| [`users`](#users) | `User` | 로그인 계정 (API 로그인 · CMS 관리자) |

## 컬럼 색인

저장하려는 값과 이름 · 의미가 같거나 비슷한 컬럼이 이미 있는지 여기서 찾습니다.

| 컬럼 | 테이블 | 타입 | 설명 |
|---|---|---|---|
| `artist_id` | [`artworks`](#artworks) | INTEGER | 작가 ID — 작가 삭제 시 NULL |
| `bio` | [`artists`](#artists) | TEXT | 작가 소개 |
| `created_at` | [`artists`](#artists) | TIMESTAMP WITH TIME ZONE | 생성 시각 |
| `created_at` | [`artworks`](#artworks) | TIMESTAMP WITH TIME ZONE | 생성 시각 |
| `created_at` | [`users`](#users) | TIMESTAMP WITH TIME ZONE | 생성 시각 |
| `description` | [`artworks`](#artworks) | TEXT | 작품 설명 |
| `email` | [`users`](#users) | VARCHAR(255) | 로그인 이메일 (고유) |
| `hashed_password` | [`users`](#users) | VARCHAR(255) | 비밀번호 해시 (pwdlib 권장 알고리즘) |
| `id` | [`artists`](#artists) | INTEGER | 작가 ID |
| `id` | [`artworks`](#artworks) | INTEGER | 작품 ID |
| `id` | [`users`](#users) | INTEGER | 사용자 ID |
| `image_key` | [`artworks`](#artworks) | VARCHAR(500) | 작품 이미지 저장소 키 (URL 아님 — media_url()로 변환) |
| `is_active` | [`users`](#users) | BOOLEAN | 로그인 허용 여부 — false면 로그인 · 토큰 인증 거부 |
| `is_admin` | [`users`](#users) | BOOLEAN | CMS 접근 권한 |
| `is_published` | [`artworks`](#artworks) | BOOLEAN | 공개 여부 — true인 작품만 사용자 API에 노출 |
| `name` | [`artists`](#artists) | VARCHAR(100) | 작가 이름 |
| `name` | [`users`](#users) | VARCHAR(100) | 표시 이름 |
| `profile_image_key` | [`artists`](#artists) | VARCHAR(500) | 프로필 이미지 저장소 키 (URL 아님 — media_url()로 변환) |
| `title` | [`artworks`](#artworks) | VARCHAR(200) | 작품 제목 |
| `updated_at` | [`artists`](#artists) | TIMESTAMP WITH TIME ZONE | 마지막 수정 시각 |
| `updated_at` | [`artworks`](#artworks) | TIMESTAMP WITH TIME ZONE | 마지막 수정 시각 |
| `updated_at` | [`users`](#users) | TIMESTAMP WITH TIME ZONE | 마지막 수정 시각 |
| `year` | [`artworks`](#artworks) | INTEGER | 제작 연도 |

## 테이블 상세

### `artists`

작가

모델: `Artist` (`app/models/artist.py`)

| 컬럼 | 타입 | NULL | 기본값 | 키 | 설명 |
|---|---|---|---|---|---|
| `id` | INTEGER | N |  | PK | 작가 ID |
| `name` | VARCHAR(100) | N |  |  | 작가 이름 |
| `bio` | TEXT | Y |  |  | 작가 소개 |
| `profile_image_key` | VARCHAR(500) | Y |  |  | 프로필 이미지 저장소 키 (URL 아님 — media_url()로 변환) |
| `created_at` | TIMESTAMP WITH TIME ZONE | N | DB `now()` |  | 생성 시각 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | N | DB `now()`<br>수정 시 앱 `now()` |  | 마지막 수정 시각 |

**참조하는 곳**

- `artworks.artist_id`

### `artworks`

작품

모델: `Artwork` (`app/models/artwork.py`)

| 컬럼 | 타입 | NULL | 기본값 | 키 | 설명 |
|---|---|---|---|---|---|
| `id` | INTEGER | N |  | PK | 작품 ID |
| `title` | VARCHAR(200) | N |  |  | 작품 제목 |
| `description` | TEXT | Y |  |  | 작품 설명 |
| `year` | INTEGER | Y |  |  | 제작 연도 |
| `image_key` | VARCHAR(500) | Y |  |  | 작품 이미지 저장소 키 (URL 아님 — media_url()로 변환) |
| `is_published` | BOOLEAN | N | 앱 `False` | IX | 공개 여부 — true인 작품만 사용자 API에 노출 |
| `artist_id` | INTEGER | Y |  | FK → `artists.id`, IX | 작가 ID — 작가 삭제 시 NULL |
| `created_at` | TIMESTAMP WITH TIME ZONE | N | DB `now()` |  | 생성 시각 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | N | DB `now()`<br>수정 시 앱 `now()` |  | 마지막 수정 시각 |

**인덱스**

- `ix_artworks_artist_id` (artist_id)
- `ix_artworks_is_published` (is_published)

**외래키**

- `artist_id` → `artists.id` ON DELETE SET NULL

### `users`

로그인 계정 (API 로그인 · CMS 관리자)

모델: `User` (`app/models/user.py`)

| 컬럼 | 타입 | NULL | 기본값 | 키 | 설명 |
|---|---|---|---|---|---|
| `id` | INTEGER | N |  | PK | 사용자 ID |
| `email` | VARCHAR(255) | N |  | UQ, IX | 로그인 이메일 (고유) |
| `hashed_password` | VARCHAR(255) | N |  |  | 비밀번호 해시 (pwdlib 권장 알고리즘) |
| `name` | VARCHAR(100) | N | 앱 `''` |  | 표시 이름 |
| `is_active` | BOOLEAN | N | 앱 `True` |  | 로그인 허용 여부 — false면 로그인 · 토큰 인증 거부 |
| `is_admin` | BOOLEAN | N | 앱 `False` |  | CMS 접근 권한 |
| `created_at` | TIMESTAMP WITH TIME ZONE | N | DB `now()` |  | 생성 시각 |
| `updated_at` | TIMESTAMP WITH TIME ZONE | N | DB `now()`<br>수정 시 앱 `now()` |  | 마지막 수정 시각 |

**인덱스**

- `ix_users_email` (email) UNIQUE
