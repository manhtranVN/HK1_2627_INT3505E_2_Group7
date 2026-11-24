# Slide 5 — API Contract, Chuẩn REST & Bảo mật (`/api/v1`)

> **Người phụ trách:** Mạnh (TV1 — API Contract Lead)  
> **Vị trí trong deck Design Review (8 slide):** Slide 5 (gửi **Nguyên / TV4** ghép vào deck chính)

---

## 1. Nội dung hiển thị trên Slide 5

**Tiêu đề slide:** Thiết kế API Contract (`/api/v1`), Lỗi RFC 7807 & Auth/RBAC  
**Thông điệp chính:** Hợp đồng OpenAPI 3.0.3 là điểm tích hợp duy nhất giữa React, Flask và Mock Server — rõ resource, đúng ngữ nghĩa HTTP và nhất quán lỗi.

### Khối 1 — Quy ước REST & Versioning (`/api/v1`)
- **URI Versioning:** Mọi endpoint đặt dưới `/api/v1`; dùng danh từ số nhiều (`/movies`, `/genres`, `/me/*`).
- **UUID v4:** Định danh tài nguyên độc lập với thuộc tính nghiệp vụ (`slug`, `email`, `tmdbId`).
- **Tách representation khỏi DB:** API trả `genres[]` nhúng trong `Movie`, ẩn `passwordHash` và đường dẫn lưu trữ nội bộ.

### Khối 2 — Phân trang, Lọc, Sắp xếp & Idempotency
- **`GET /movies`:** `page`, `limit` (`1..100`), `q`, `genre`, `year`, `sortBy`, `sortOrder`, trả `{ items, meta }`.
- **Idempotency trên `PUT`:** `PUT /me/favorites/{id}`, `PUT /me/ratings/{id}`, `PUT /me/watch-progress/{id}` gọi lặp không tạo trùng bản ghi.
- **Ẩn phim an toàn:** `DELETE /movies/{id}` trả `204` (soft delete/ẩn); `PATCH /movies/{id}` yêu cầu tối thiểu 1 trường.

### Khối 3 — Lỗi thống nhất RFC 7807 (`application/problem+json`)
- Mọi lỗi `4xx/5xx` trả cùng cấu trúc `ProblemDetails`: `type`, `title`, `status`, `detail`, `instance`, `traceId`, `errorCode`.
- Phân tách mã lỗi rõ ràng: `400` (sai cú pháp/UUID) vs `422` (sai ràng buộc nghiệp vụ kèm `errors[]`) vs `409` (trùng `email`/`slug`).

### Khối 4 — Xác thực (JWT) & Phân quyền (RBAC + Ownership)
- **Authentication (`401`):** `POST /auth/register`, `POST /auth/login` cấp JWT (`sub`, `role`, `exp`).
- **Authorization (`403`):** Kiểm tra tại backend cho 3 vai trò (`Guest`, `user`, `admin`); quyền Admin chỉ mở ở `POST/PATCH/DELETE`.
- **Object-level Ownership:** Nhóm `/me/*` lấy `user_id` trực tiếp từ `sub` trong token; phim `hidden` trả `404` cho non-admin.

### Bảng tóm tắt Trade-offs thiết kế (cho phần ghi chú / hỏi đáp nhanh)

| Quyết định | Lựa chọn | Đánh đổi (Trade-off) |
|---|---|---|
| Định danh `UUID v4` vs `auto-increment ID` | **UUID v4** | Dài hơn trong URL nhưng tránh lộ số lượng bản ghi và tách khỏi khóa nghiệp vụ. |
| Lỗi `400` vs `422` | **Tách `400` (cú pháp) và `422` (validation)** | Backend phải phân loại rõ validator, bù lại Frontend hiển thị lỗi theo từng field chính xác. |
| Phim ẩn trả `404` vs `403` cho Guest/User | **Trả `404 Not Found`** | Không xác nhận sự tồn tại của tài nguyên bị ẩn với người không có quyền quản trị. |

---

## 2. Bộ câu hỏi Q&A bảo vệ phần của Mạnh

1. **Vì sao tách `400 Bad Request` và `422 Unprocessable Entity`?**
   - `400` dùng khi request hỏng ở tầng giao thức/cú pháp (JSON sai cú pháp, `movieId` không phải UUID, sai kiểu query). `422` dùng khi JSON hợp lệ nhưng vi phạm ràng buộc nghiệp vụ (`releaseYear < 1900`, password `< 8` ký tự) và trả kèm mảng `errors[{field, message}]` để UI gắn vào đúng ô nhập.
2. **Phân biệt `401 Unauthorized` và `403 Forbidden` trong MNP?**
   - `401` là lỗi **xác thực** (chưa gửi token, token hết hạn/sai chữ ký, hoặc login sai mật khẩu). `403` là lỗi **phân quyền** (đã có token hợp lệ nhưng `role=user` gọi API quản trị của `admin`).
3. **Tại sao phim đang ở trạng thái `hidden` lại trả `404` thay vì `403` cho Guest/User?**
   - Để không làm lộ thông tin rằng một `movieId` bị ẩn có tồn tại trong hệ thống; chỉ `admin` mới thấy được khi truyền `includeHidden=true`.
4. **Vì sao dùng `/api/v1` trong URL thay vì đặt version trong HTTP Header?**
   - URI versioning trực quan trên Swagger UI, browser, log truy cập và Postman/Newman, dễ cấu hình mock server và phù hợp cho bài toán web app consumer.
5. **Tại sao dùng `/me/favorites/{movieId}` thay vì `/users/{userId}/favorites/{movieId}`?**
   - Lấy danh tính trực tiếp từ claim `sub` trong JWT giúp loại bỏ nguy cơ user A đổi `userId` trên URL để đọc/sửa dữ liệu của user B (IDOR), đồng thời rút gọn contract cho frontend.
6. **Vì sao giữ cả `PATCH /movies/{movieId}` (đổi `status: hidden`) và `DELETE /movies/{movieId}`?**
   - `PATCH` dùng cho quản trị viên chỉnh sửa bất kỳ thông tin phim hoặc bật/tắt `published`/`hidden`. `DELETE` tuân thủ ngữ nghĩa REST chuẩn (`204 No Content`) khi thao tác xóa khỏi danh mục, cài đặt bên dưới dưới dạng soft delete để không làm gãy khóa ngoại ở bảng `favorites`, `ratings`, `watch_progress`.
