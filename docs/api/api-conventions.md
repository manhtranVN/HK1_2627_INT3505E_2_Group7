# Quy ước thiết kế API — MNP (Movie Navigator Promax)

## 1. Versioning & Quy tắc đặt tên Resource

- **URI Versioning:** Mọi endpoint đều nằm dưới tiền tố `/api/v1` (khai báo trong `servers[].url` của `openapi/openapi.yaml`). Khi có breaking change ở các phiên bản sau mới nâng lên `/api/v2`.
- **Định danh tài nguyên (UUID v4):** Sử dụng UUID v4 do server sinh ra (`format: uuid`) làm khóa định danh trên đường dẫn (`/movies/{movieId}`), tách biệt khỏi thuộc tính nghiệp vụ có thể thay đổi hoặc trùng lặp (`slug`, `email`, `tmdbId`).
- **Quy tắc đặt tên URL:**
  - Dùng danh từ số nhiều dạng `kebab-case`: `/movies`, `/genres`, `/me/favorites`, `/me/watch-progress`.
  - Không đặt động từ trong URL (`/getMovies`, `/deleteMovie` bị cấm), trừ các thao tác đặc thù của auth như `/auth/register`, `/auth/login`.
  - Dùng `/me/*` cho tài nguyên cá nhân để danh tính người dùng luôn lấy trực tiếp từ claim `sub` trong JWT, tránh giả mạo `userId` qua path/query.

---

## 2. Phân trang, Tìm kiếm, Lọc & Sắp xếp

Áp dụng thống nhất cho các collection endpoint có dữ liệu lớn (`GET /movies`, và tái sử dụng `PageMeta` nếu `/me/favorites` phân trang):

| Tham số | Kiểu | Mặc định | Ràng buộc / Giá trị hợp lệ | Ý nghĩa |
|---|---|---|---|---|
| `page` | integer | `1` | `>= 1` | Trang cần lấy (1-indexed) |
| `limit` | integer | `20` | `1 .. 100` | Số bản ghi tối đa trên 1 trang |
| `q` | string | — | `1 .. 100` ký tự | Tìm kiếm theo tên phim, diễn viên, đạo diễn |
| `genre` | string | — | `slug` hoặc UUID thể loại | Lọc theo thể loại |
| `year` | integer | — | `1900 .. 2100` | Lọc theo năm phát hành |
| `sortBy` | enum | `createdAt` | `createdAt`, `releaseYear`, `averageRating`, `title`, `popularity` | Trường sắp xếp |
| `sortOrder` | enum | `desc` | `asc`, `desc` | Chiều sắp xếp |
| `includeHidden` | boolean | `false` | Chỉ hiệu lực với `role=admin` | Bao gồm phim `hidden` |

**Cấu trúc phản hồi phân trang chuẩn (`MoviePageResponse`):**

```json
{
  "items": [ ... ],
  "meta": {
    "page": 1,
    "limit": 20,
    "totalItems": 540,
    "totalPages": 27,
    "hasNext": true,
    "hasPrev": false
  }
}
```

---

## 3. Tính Idempotency (Gọi lặp an toàn)

| HTTP Method | Tính chất | Quy ước áp dụng trong MNP |
|---|---|---|
| `GET` | Safe & Idempotent | Không thay đổi trạng thái hệ thống; gọi lặp trả cùng trạng thái tài nguyên. |
| `PUT` | **Idempotent bắt buộc** | Dùng cho các thao tác tương tác `/me/*` của Quốc Phong:<br>- `PUT /me/favorites/{movieId}`: upsert trạng thái yêu thích (gọi 1 lần hay 5 lần đều chỉ tồn tại đúng 1 bản ghi `(user_id, movie_id)`, không tạo trùng, trả `200`/`201`).<br>- `PUT /me/ratings/{movieId}`: ghi đè điểm đánh giá (1–5 sao) của user cho phim đó.<br>- `PUT /me/watch-progress/{movieId}`: cập nhật vị trí giây hiện tại (`positionSeconds`), an toàn khi player đồng bộ định kỳ hoặc mạng retry. |
| `PATCH` | Không mặc định idempotent (nhưng set-field ở MNP an toàn) | `PATCH /movies/{movieId}` chỉ cập nhật các trường gửi lên, yêu cầu tối thiểu 1 trường (`minProperties: 1`). |
| `DELETE` | **Idempotent về mặt trạng thái** | `DELETE /movies/{movieId}` ẩn/xóa mềm phim (`204 No Content`); `DELETE /me/favorites/{movieId}` bỏ yêu thích. |
| `POST` | Không idempotent | Dùng cho tạo mới tài nguyên (`POST /movies`, `POST /genres`, `POST /auth/register`) hoặc hành động cấp token (`POST /auth/login`). |

---

## 4. Bảng mã trạng thái HTTP

| Mã HTTP | Ý nghĩa | Khi nào trả về |
|---|---|---|
| `200 OK` | Thành công (có body) | `GET` thành công, `POST /auth/login`, `PATCH /movies/{movieId}`, `PUT /me/*` cập nhật bản ghi có sẵn. |
| `201 Created` | Tạo mới thành công | `POST /auth/register`, `POST /movies`, `POST /genres` (kèm header `Location`). |
| `204 No Content` | Thành công (không có body) | `DELETE /movies/{movieId}`, `DELETE /me/favorites/{movieId}`. |
| `400 Bad Request` | Sai cú pháp request | JSON lỗi cú pháp, thiếu body bắt buộc, `movieId` không đúng định dạng UUID v4, query sai kiểu dữ liệu. |
| `401 Unauthorized` | Chưa xác thực / Token lỗi | Thiếu header `Authorization: Bearer ...`, token hết hạn, chữ ký sai, hoặc sai email/mật khẩu khi login. |
| `403 Forbidden` | Không đủ quyền | Token hợp lệ (`role=user`) nhưng gọi endpoint của `admin`, hoặc sửa tài nguyên không thuộc quyền sở hữu. |
| `404 Not Found` | Không tìm thấy | UUID phim không tồn tại, hoặc phim đang ở trạng thái `hidden` khi caller không phải `admin`. |
| `409 Conflict` | Xung đột dữ liệu duy nhất | Đăng ký trùng `email`, tạo/cập nhật trùng `slug` phim hoặc `slug`/`name` thể loại. |
| `422 Unprocessable Entity` | Sai ràng buộc nghiệp vụ | JSON đúng cú pháp nhưng vi phạm rule (năm `< 1900`, mật khẩu `< 8` ký tự, `limit > 100`, điểm rating ngoài `1..5`). |
| `500 Internal Server Error` | Lỗi máy chủ nội bộ | Lỗi không mong muốn; ẩn stack trace nội bộ, luôn trả `traceId` để đối soát log. |

---

## 5. Chuẩn phản hồi lỗi RFC 7807 (`application/problem+json`)

Mọi phản hồi `4xx` và `5xx` **bắt buộc** dùng `Content-Type: application/problem+json` theo schema `ProblemDetails`:

- `type` (uri): định danh loại lỗi (`https://api.mnp.local/errors/...`)
- `title` (string): tên ngắn gọn loại lỗi
- `status` (integer): mã HTTP tương ứng
- `detail` (string): mô tả nguyên nhân cụ thể cho request hiện tại
- `instance` (string): đường dẫn URI của request phát sinh lỗi
- `traceId` (uuid): mã truy vết log ở backend
- `errorCode` (enum `ErrorCode`): `BAD_REQUEST`, `VALIDATION_ERROR`, `UNAUTHORIZED`, `TOKEN_EXPIRED`, `FORBIDDEN`, `NOT_FOUND`, `CONFLICT`, `EMAIL_ALREADY_EXISTS`, `SLUG_ALREADY_EXISTS`, `INTERNAL_SERVER_ERROR`
- `errors` (tùy chọn, array `{ field, message }`): danh sách lỗi từng trường khi trả `422`.

### Ví dụ mẫu lỗi 401 / 403 / 404 / 422

```json
// 401 Unauthorized
{
  "type": "https://api.mnp.local/errors/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Yêu cầu cung cấp JWT Bearer token hợp lệ để thực hiện thao tác này.",
  "instance": "/api/v1/auth/me",
  "traceId": "22222222-3333-4444-8555-666666666666",
  "errorCode": "UNAUTHORIZED"
}
```

```json
// 403 Forbidden
{
  "type": "https://api.mnp.local/errors/forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "Thao tác này yêu cầu vai trò quản trị viên (admin).",
  "instance": "/api/v1/movies",
  "traceId": "33333333-4444-4555-8666-777777777777",
  "errorCode": "FORBIDDEN"
}
```

```json
// 404 Not Found
{
  "type": "https://api.mnp.local/errors/not-found",
  "title": "Resource Not Found",
  "status": 404,
  "detail": "Không tìm thấy phim với ID '9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d'.",
  "instance": "/api/v1/movies/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "traceId": "44444444-5555-4666-8777-888888888888",
  "errorCode": "NOT_FOUND"
}
```

```json
// 422 Unprocessable Entity
{
  "type": "https://api.mnp.local/errors/validation-error",
  "title": "Unprocessable Entity",
  "status": 422,
  "detail": "Dữ liệu gửi lên không thỏa mãn ràng buộc kiểm tra hợp lệ.",
  "instance": "/api/v1/movies",
  "traceId": "66666666-7777-4888-8999-aaaaaaaaaaaa",
  "errorCode": "VALIDATION_ERROR",
  "errors": [
    {
      "field": "releaseYear",
      "message": "Năm phát hành phải nằm trong khoảng từ 1900 đến 2100."
    }
  ]
}
```

---

## 6. Xác thực (Authentication) & Phân quyền (Authorization / RBAC)

1. **Tách biệt Authentication và Authorization:**
   - **Authentication:** Kiểm tra chữ ký, hạn dùng (`exp`) của JWT trong header `Authorization: Bearer <token>`. Thất bại -> `401 Unauthorized`.
   - **Authorization (RBAC + Ownership):** Kiểm tra claim `role` (`user` | `admin`) và quyền sở hữu bản ghi (`sub == record.user_id`). Thất bại -> `403 Forbidden`.
   - Mọi kiểm tra thực hiện tại **backend**, không phụ thuộc việc frontend ẩn nút.
2. **Ma trận quyền theo endpoint (Core + Nhóm mở rộng):**

| Endpoint | Guest (Không token) | Registered (`role=user`) | Admin (`role=admin`) |
|---|---|---|---|
| `GET /health`, `POST /auth/register`, `POST /auth/login` | Cho phép | Cho phép | Cho phép |
| `GET /auth/me` | `401` | Cho phép (chỉ bản thân) | Cho phép (chỉ bản thân) |
| `GET /genres` | Cho phép | Cho phép | Cho phép |
| `GET /movies`, `GET /movies/{movieId}` | Chỉ phim `published` (phim `hidden` -> `404`) | Chỉ phim `published` (phim `hidden` -> `404`) | Xem tất cả nếu `includeHidden=true` |
| `POST /movies`, `PATCH /movies/{movieId}`, `DELETE /movies/{movieId}`, `POST /genres` | `401` | `403` | Cho phép |
| Nhóm `/me/*` *(QPhong bổ sung)* | `401` | Chỉ thao tác dữ liệu của chính `sub` | Chỉ thao tác dữ liệu của chính `sub` |
| `GET /me/recommendations` *(Nguyên bổ sung)* | `401` | Cho phép (dựa trên `sub` + cold-start) | Cho phép |
| `GET /movies/{movieId}/similar` *(Nguyên bổ sung)* | Cho phép (`published`) | Cho phép (`published`) | Cho phép |

---

## 7. Hướng dẫn tích hợp PR cho QPhong (TV2) & Nguyên (TV4)

Khi mở PR bổ sung vào `openapi/openapi.yaml` để nâng từ `0.2.0` lên `1.0.0`, hãy tái sử dụng trực tiếp các thành phần dùng chung sau:

- **Security:** `security: [{ bearerAuth: [] }]` cho mọi endpoint `/me/*` và `/me/recommendations`.
- **Path parameter phim:** `$ref: '#/components/parameters/MovieIdPath'` cho các route `/me/*/{movieId}` và `/movies/{movieId}/similar`.
- **Pagination:** `$ref: '#/components/parameters/PageParam'`, `$ref: '#/components/parameters/LimitParam'` và `$ref: '#/components/schemas/PageMeta'`.
- **Responses lỗi:** dùng `$ref` tới `#/components/responses/BadRequest`, `Unauthorized`, `Forbidden`, `NotFound`, `ValidationError`, `InternalServerError`.
- **Tag:** bỏ comment `Me` và `Recommendations` trong mục `tags:` khi thêm paths tương ứng để giữ spec 0 lỗi/0 cảnh báo lint.
