# Resource Model và Database Schema

[Resource Model](resource-model.drawio) mô tả tài nguyên và JSON phía consumer; [ERD](erd.drawio) mô tả lưu trữ, khóa và quan hệ. [OpenAPI](../../openapi/openapi.yaml) là hợp đồng HTTP; tên trường JSON theo core dùng camelCase, cột PostgreSQL dùng snake_case.

Resource Model giữ hai trang: **01 - Resource URI Hierarchy** và **02 - API Representations**. Trang 01 nối theo phân cấp URL, không phải trình tự gọi API. Trang 02 dùng nét liền cho object/array nhúng, nét đứt cho UUID reference hoặc ngữ cảnh chủ sở hữu. Các khối AI được ghi rõ là dự kiến của Nguyên, chưa có operation trong contract nhánh QPhong.

ERD giữ bố cục gọn, 8 bảng và 10 FK; PK vàng, FK xanh, PK/FK tím. Khóa chính ghép bảo đảm duy nhất theo cặp ở bảng nối/tương tác. Có bổ sung trường lưu trữ cần cho Catalog core, không thêm bảng mới.

| Nghiệp vụ | Lưu trữ DB | JSON API |
|---|---|---|
| Tài khoản | users.password_hash | UserProfile ẩn hash; password chỉ nằm trong request |
| Phim và thể loại | movies + movie_genres + genres | MovieSummary nhúng genres[] gồm id, name, slug; không lộ bảng nối |
| Video | movies.video_path | hasVideo và streamUrl theo core; không lộ storage key |
| Tên trường | movie_id, created_at, updated_at | movieId, createdAt, updatedAt |
| Yêu thích | favorites PK (user_id, movie_id) | User lấy từ JWT sub, Favorite nhúng MovieSummary |
| Rating | ratings.score numeric(2,1), CHECK 1..5 bước 0.5 | Rating.score; averageRating và ratingCount là tổng hợp |
| Thời lượng | duration_seconds nguyên dương | Catalog durationMinutes = ceil(duration_seconds / 60) |
| Tiến độ | watch_progress.position_seconds | positionSeconds, completed; kiểm cận trên bằng giây |
| Hiển thị phim | movies.is_published | status published/hidden |
| Ngày phát hành | movies.release_date | releaseYear lấy phần năm; phim published phải có năm hợp lệ |
| Chọn thể loại | user_genre_preferences nhiều dòng | genreIds[] thay toàn bộ tập; GET nhúng thêm genres[] |
| AI | Không có bảng recommendations trong ERD | Ngữ cảnh dự kiến trên sơ đồ, contract AI do Nguyên bổ sung |

MovieSummary có genres[] nhúng là ví dụ API khác DB: consumer không cần biết movie_genres hoặc thực hiện JOIN. Thuộc tính slug được lưu riêng, không dùng thay UUID định danh tài nguyên. director/cast phục vụ MovieDetail được lưu trong movies.

## Giải thích khi bảo vệ

- Không tạo endpoint CRUD chỉ vì có một bảng; thiết kế resource theo nhu cầu consumer.
- PK ghép chặn bản ghi trùng. PUT biểu đạt trạng thái mong muốn; service và transaction phải thực thi idempotency thực tế.
- Schema kiểm được positionSeconds nguyên >=0; service phải đọc thời lượng để kiểm cận trên. durationMinutes của API phải đổi sang giây trước khi so.
- watch_progress chỉ giữ trạng thái hiện tại; lịch sử sự kiện xem là mở rộng riêng, chưa thêm vào ERD 8 bảng.
- DTO che tên cột và storage key, cho phép đổi cách lưu trữ mà giữ hợp đồng API.

Các quyết định cần chốt và kịch bản bàn giao nằm trong [handoff QPhong](../handoff/qphong-week12.md).

<!-- BEGIN GENERATED DATA -->

## Chi tiết thuộc tính dữ liệu

Thiết kế PostgreSQL; chưa phải migration. PK ghép đồng thời bảo đảm UNIQUE theo cặp. Tất cả FK đều NOT NULL. UUID do server sinh; timestamp theo UTC.

### `users`

| Trường | PostgreSQL | Khóa / tham chiếu | NULL | Mặc định | Ý nghĩa |
|---|---|---|---|---|---|
| `id` | `uuid` | PK | Không | `-` | Internal account ID. |
| `email` | `varchar(254)` | UQ | Không | `-` | Normalized lowercase email; unique. |
| `password_hash` | `text` | - | Không | `-` | Password hash; never serialized. |
| `display_name` | `varchar(100)` | - | Không | `-` | Public display name. |
| `role` | `varchar(16)` | - | Không | `user` | user or admin. |
| `status` | `varchar(16)` | - | Không | `active` | active or disabled. |
| `created_at` | `timestamptz` | - | Không | `now()` | UTC creation time. |

- DB CHECK: `role IN ('user','admin')`.
- DB CHECK: `status IN ('active','disabled')`.

### `movies`

| Trường | PostgreSQL | Khóa / tham chiếu | NULL | Mặc định | Ý nghĩa |
|---|---|---|---|---|---|
| `id` | `uuid` | PK | Không | `-` | Internal movie ID. |
| `tmdb_id` | `bigint` | UQ | Có | `-` | Optional external TMDB ID. |
| `slug` | `varchar(255)` | UQ | Không | `-` | Stable URL slug required by the shared Catalog contract. |
| `title` | `varchar(255)` | - | Không | `-` | Movie title. |
| `description` | `text` | - | Không | `` | Movie synopsis. |
| `release_date` | `date` | - | Có | `-` | Release date. |
| `duration_seconds` | `integer` | - | Không | `-` | Duration in seconds. |
| `poster_url` | `text` | - | Có | `-` | Public poster URI. |
| `video_path` | `text` | - | Có | `-` | Internal storage key; not public. |
| `is_published` | `boolean` | - | Không | `false` | Visibility flag. |
| `created_at` | `timestamptz` | - | Không | `now()` | UTC creation time. |
| `updated_at` | `timestamptz` | - | Không | `now()` | UTC time of actual state change. |
| `director` | `varchar(255)` | - | Không | `` | Director displayed by the shared MovieDetail schema. |
| `cast` | `jsonb` | - | Không | `[]` | Ordered actor names returned as a JSON array. |

- DB CHECK: `duration_seconds > 0`.
- DB CHECK: `tmdb_id IS NULL OR tmdb_id > 0`.
- Service: API durationMinutes = ceil(duration_seconds / 60); positionSeconds always uses seconds.
- Service: Published movie must provide a valid release year and poster URL required by core MovieSummary.
- Service: status maps published/hidden to is_published; averageRating is 0 when no ratings exist.

### `genres`

| Trường | PostgreSQL | Khóa / tham chiếu | NULL | Mặc định | Ý nghĩa |
|---|---|---|---|---|---|
| `id` | `uuid` | PK | Không | `-` | Internal genre ID. |
| `name` | `varchar(80)` | UQ | Không | `-` | Canonical genre label; unique. |
| `slug` | `varchar(64)` | UQ | Không | `-` | Stable URL slug required by the shared Catalog contract. |

- DB CHECK: `length(trim(name)) > 0`.

### `movie_genres`

| Trường | PostgreSQL | Khóa / tham chiếu | NULL | Mặc định | Ý nghĩa |
|---|---|---|---|---|---|
| `movie_id` | `uuid` | PK; FK → movies.id | Không | `-` | Movie FK. |
| `genre_id` | `uuid` | PK; FK → genres.id | Không | `-` | Genre FK. |


### `user_genre_preferences`

| Trường | PostgreSQL | Khóa / tham chiếu | NULL | Mặc định | Ý nghĩa |
|---|---|---|---|---|---|
| `user_id` | `uuid` | PK; FK → users.id | Không | `-` | Owner FK. |
| `genre_id` | `uuid` | PK; FK → genres.id | Không | `-` | Selected genre FK. |


### `favorites`

| Trường | PostgreSQL | Khóa / tham chiếu | NULL | Mặc định | Ý nghĩa |
|---|---|---|---|---|---|
| `user_id` | `uuid` | PK; FK → users.id | Không | `-` | Owner FK. |
| `movie_id` | `uuid` | PK; FK → movies.id | Không | `-` | Movie FK. |
| `created_at` | `timestamptz` | - | Không | `now()` | Time first added; unchanged on repeated PUT. |


### `ratings`

| Trường | PostgreSQL | Khóa / tham chiếu | NULL | Mặc định | Ý nghĩa |
|---|---|---|---|---|---|
| `user_id` | `uuid` | PK; FK → users.id | Không | `-` | Owner FK. |
| `movie_id` | `uuid` | PK; FK → movies.id | Không | `-` | Movie FK. |
| `score` | `numeric(2,1)` | - | Không | `-` | Star rating, steps of 0.5. |
| `updated_at` | `timestamptz` | - | Không | `now()` | Actual state-change time. |

- DB CHECK: `score >= 1.0 AND score <= 5.0`.
- DB CHECK: `mod(score, 0.5) = 0`.

### `watch_progress`

| Trường | PostgreSQL | Khóa / tham chiếu | NULL | Mặc định | Ý nghĩa |
|---|---|---|---|---|---|
| `user_id` | `uuid` | PK; FK → users.id | Không | `-` | Owner FK. |
| `movie_id` | `uuid` | PK; FK → movies.id | Không | `-` | Movie FK. |
| `position_seconds` | `integer` | - | Không | `0` | Current absolute position. |
| `completed` | `boolean` | - | Không | `false` | Explicit completion state. |
| `updated_at` | `timestamptz` | - | Không | `now()` | Actual state-change time. |

- DB CHECK: `position_seconds >= 0`.
- Service: position_seconds <= movies.duration_seconds
- Service: Movie must be published and have video_path for a progress write.

### Xóa dữ liệu và chỉ mục

- API DELETE movie chỉ ẩn bằng `is_published=false`, giữ các tương tác.
- Khi triển khai physical delete: users → bảng cá nhân dùng CASCADE; movies/genres dùng RESTRICT khi còn tham chiếu.
- Chỉ mục đề xuất: favorites `(user_id, created_at DESC, movie_id)`; watch_progress `(user_id, completed, updated_at DESC, movie_id)`; movie_genres `(genre_id, movie_id)`; ratings `(movie_id)`; movies `(is_published, release_date, id)`.
- Ràng buộc tiến độ không vượt thời lượng là kiểm tra liên bảng ở service; không mô tả nhầm thành CHECK một bảng.


## Ánh xạ API với dữ liệu

> Sinh từ [OpenAPI](../../openapi/openapi.yaml). `x-db-tables` ghi bảng đọc/ghi; `x-db-table` ánh xạ DTO.

| Operation | operationId | Người phụ trách | Bảng liên quan |
|---|---|---|---|
| `GET /health` | `getHealthStatus` | Mạnh | Không lưu DB |
| `POST /auth/register` | `registerUser` | Mạnh | Không lưu DB |
| `POST /auth/login` | `loginUser` | Mạnh | Không lưu DB |
| `GET /auth/me` | `getCurrentUserProfile` | Mạnh | Không lưu DB |
| `GET /movies` | `listMovies` | Mạnh | Không lưu DB |
| `POST /movies` | `createMovie` | Mạnh | Không lưu DB |
| `GET /movies/{movieId}` | `getMovieById` | Mạnh | Không lưu DB |
| `PATCH /movies/{movieId}` | `updateMovie` | Mạnh | Không lưu DB |
| `DELETE /movies/{movieId}` | `deleteMovie` | Mạnh | Không lưu DB |
| `GET /genres` | `listGenres` | Mạnh | Không lưu DB |
| `POST /genres` | `createGenre` | Mạnh | Không lưu DB |
| `GET /me/favorites` | `listMyFavorites` | QPhong | `favorites`, `movies`, `genres`, `movie_genres`, `ratings` |
| `PUT /me/favorites/{movieId}` | `putMyFavorite` | QPhong | `favorites`, `movies` |
| `DELETE /me/favorites/{movieId}` | `deleteMyFavorite` | QPhong | `favorites` |
| `PUT /me/ratings/{movieId}` | `putMyRating` | QPhong | `ratings`, `movies` |
| `GET /me/watch-progress` | `listMyContinueWatching` | QPhong | `watch_progress`, `movies`, `genres`, `movie_genres`, `ratings` |
| `PUT /me/watch-progress/{movieId}` | `putMyWatchProgress` | QPhong | `watch_progress`, `movies` |
| `GET /me/preferences/genres` | `getMyGenrePreferences` | QPhong | `user_genre_preferences`, `genres` |
| `PUT /me/preferences/genres` | `putMyGenrePreferences` | QPhong | `user_genre_preferences`, `genres` |

### DTO không trùng nguyên dạng với bảng

| Schema | Bảng gốc | Trường tổng hợp / biểu diễn |
|---|---|---|
| `Favorite` | `favorites` | `movie` |
| `Rating` | `ratings` | - |
| `WatchProgress` | `watch_progress` | - |
| `ContinueWatchingItem` | `watch_progress` | `movie` |
| `GenrePreferences` | `user_genre_preferences` | `genreIds`, `genres` |
| `UserProfile` | `users` | displayName → display_name; createdAt → created_at |
| `Genre` | `genres` | Cùng tên thuộc tính |
| `MovieSummary` | `movies` | posterUrl → poster_url; ratingCount → ratings count; averageRating → ratings average or 0; durationMinutes → ceil(duration_seconds / 60); releaseYear → year(release_date); status → is_published → published/hidden |
| `MovieDetail` | `movies` | overview → description; streamUrl → authorized URL from video_path; tmdbId → tmdb_id; createdAt → created_at; updatedAt → updated_at |

Mọi thao tác `/me/*` lấy chủ sở hữu từ `JWT sub`, không nhận user_id trong request. Mặc định dùng `/api/v1`; `/health` thuộc core tại `/api/v1/health`. AI chỉ là ngữ cảnh dự kiến trong sơ đồ.

<!-- END GENERATED DATA -->
