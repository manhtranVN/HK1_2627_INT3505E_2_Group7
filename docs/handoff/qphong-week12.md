# QPhong - Bàn giao Tuần 12 (Design Review)

Phạm vi theo mục 3.2 phân công Tuần 12: Resource Model, ERD 8 bảng, giải thích Resource vs DB và OpenAPI tương tác cá nhân. Nhánh bàn giao: `feat/data-model-me-api`, tạo từ `feat/openapi-core` tại commit `7bf99e6`.

## Hồ sơ bàn giao

| Sản phẩm | File | Trạng thái |
|---|---|---|
| ERD | [erd.drawio](../design/erd.drawio), [SVG](../design/erd.svg) | 8 bảng, 10 FK, PK/FK nổi bật, khóa ghép theo cặp |
| Resource Model | [resource-model.drawio](../design/resource-model.drawio) | Hai trang: URI hierarchy và API representations |
| Bản xem nhanh Resource Model | [Cây URI](../design/resource-model.svg), [representations](../design/resource-representations.svg) | AI được đánh dấu dự kiến, do Nguyên phụ trách |
| Resource vs DB | [resource-vs-db.md](../design/resource-vs-db.md) | Giải thích, chi tiết thuộc tính và ánh xạ API–DB |
| OpenAPI | [openapi.yaml](../../openapi/openapi.yaml) | Thêm 8 operations của QPhong; 6 bắt buộc và 2 GET hỗ trợ |
| Nội dung trình bày | [Slide 3](../slides/slide-03-data-model.md), [phần Slide 6](../slides/slide-06-me-api.md) | Markdown để Nguyên ghép deck |
| Bằng chứng | [qphong-validation-report.txt](../evidence/qphong-validation-report.txt) | Validate thiết kế; chưa chạy backend/mock |

Báo cáo trực tuyến: [Google Docs QPhong](https://docs.google.com/document/d/15tqfuMntmDdF1iwRtxC6LmtJFKy79xvUe1bfkoWovNs/edit).

Gói upload chỉ gồm các file bàn giao đang dùng. `tools/`, `requirements-dev.txt`, README mới, references và archive chỉ giữ cục bộ, đã được Git bỏ qua. Bài tập cũ nằm trong `old_exercise/`; bản README có chỉnh sửa trước đó được giữ nguyên tại đây.

## API của QPhong

Prefix `/api/v1`; tag `Me`, `x-owner: QPhong`. Mọi operation lấy user hiện tại từ JWT `sub`, không nhận `userId` hoặc `user_id` từ client.

| Method | Path | Thành công | Phạm vi |
|---|---|---|---|
| GET | `/me/favorites` | 200 FavoritePage | Bắt buộc |
| PUT | `/me/favorites/{movieId}` | 201 khi tạo, 200 khi đã có | Bắt buộc |
| DELETE | `/me/favorites/{movieId}` | 204 | Bắt buộc |
| PUT | `/me/ratings/{movieId}` | 200 Rating | Bắt buộc |
| PUT | `/me/watch-progress/{movieId}` | 200 WatchProgress | Bắt buộc |
| PUT | `/me/preferences/genres` | 200 GenrePreferences | Bắt buộc |
| GET | `/me/watch-progress` | 200 ContinueWatchingPage | Hỗ trợ luồng xem tiếp |
| GET | `/me/preferences/genres` | 200 GenrePreferences | Hỗ trợ tải lại lựa chọn UI |

## Tích hợp với core

- Giữ nguyên toàn bộ 11 operations và các components sẵn có của core; chỉ thêm paths/schemas và metadata thiết kế phần QPhong. Validator đối chiếu cấu trúc với bản core gốc.
- Tái sử dụng `MovieIdPath`, `PageParam`, `LimitParam`, `PageMeta`, `MovieSummary`, `Genre`, `bearerAuth` và các response lỗi dùng chung.
- JSON camelCase: `movieId`, `createdAt`, `updatedAt`, `positionSeconds`, `genreIds`; collection trả `items` và `meta` gồm `hasNext`/`hasPrev`. Cột DB vẫn snake_case.
- Lỗi dùng `application/problem+json`, `traceId`, `errorCode` và `ErrorCode` của core; chỉ khai báo các status phù hợp từng operation.
- Contract nhánh này là `0.3.0`, chưa phải bản tích hợp v1.0 của cả nhóm. Không đưa các API Auth/Catalog/AI nháp cũ vào thay phần chính thức.
- `/me/recommendations` và `/movies/{movieId}/similar` do Nguyên bổ sung sau. Chúng chỉ xuất hiện như ngữ cảnh dự kiến trên Resource Model; chưa có operation AI trong OpenAPI nhánh này.

## Quyết định thiết kế cần review

Các lựa chọn dưới đây là thiết kế đề nghị, chưa suy diễn thành xác nhận của nhóm hoặc giảng viên.

| Hạng mục | Thiết kế hiện tại |
|---|---|
| ID và khóa | UUID nội bộ; PK ghép ở bảng nối/tương tác chống trùng cặp |
| PUT favorite | Không body request; tạo trả 201 kèm Location, đã có trả 200 cùng Favorite, giữ createdAt; không sinh bản ghi thứ hai |
| DELETE favorite | 204 kể cả quan hệ không còn hoặc phim bị ẩn; không lộ trạng thái phim |
| Rating | Theo core: 1..5, bước 0.5; PUT tạo/thay thế trả 200; cùng điểm giữ updatedAt |
| Progress | `positionSeconds` nguyên >=0, `completed` boolean bắt buộc; giá trị tuyệt đối, không cộng dồn; không vượt thời lượng phim |
| Đơn vị | API Catalog dùng `durationMinutes`; DB lưu `duration_seconds`; so progress bằng giây, không so trực tiếp với số phút |
| Cập nhật đồng thời | Last committed write wins; cho phép tua lùi. Có thể bổ sung ETag/revision khi cần |
| Preferences | Thay toàn bộ tập trong transaction; `genreIds: []` xóa hết; không ghi một phần nếu có genre không tồn tại |
| Timestamp | UTC; cùng trạng thái/tập thể loại là no-op, giữ timestamp |
| Phim ẩn | Không xuất hiện trong favorites/continue-watching và tổng phân trang; các thao tác ghi cần phim công khai |
| Video | DB giữ storage key, API trả URL được cấp quyền. Không trả `video_path`; không lưu video binary trong PostgreSQL |
| Mở rộng | watch_progress là trạng thái hiện tại; chưa thêm bảng thứ 9 watch_events hoặc bảng recommendations |

### Điều chỉnh để phù hợp core

Bản nháp trước đây dùng snake_case cho JSON, favorite 204 và rating từ 0.5. Khi tích hợp đã chuyển sang camelCase, favorite 200/201 và rating từ 1 theo quy ước core. Đề xuất ban đầu và tài liệu kiến trúc có thang 0.5..5; nhóm cần xác nhận lại thang điểm trước triển khai, sau đó sửa đồng bộ YAML, DB CHECK, slide và examples nếu thay đổi.

ERD giữ bố cục gọn, ký hiệu và 8 bảng. Thêm `slug` cho movies/genres, `director` và `cast` cho movies để lưu các trường bắt buộc của Catalog core. `status` API ánh xạ sang `is_published`; `releaseYear` lấy năm từ `release_date`; `averageRating` trả 0 khi chưa có đánh giá theo schema core. Cần thực thi các phép ánh xạ này ở service khi triển khai.

## Checklist và việc tiếp theo

- [x] Chuẩn bị ERD, Resource Model hai trang và Resource vs DB.
- [x] Bổ sung đủ 6 operations bắt buộc; có 2 GET hỗ trợ UI.
- [x] Căn chỉnh contract trên core, giữ nguyên paths/components hiện có.
- [x] Chuẩn bị nội dung Markdown Slide 3 và phần /me/* ở Slide 6.
- [x] Chạy validate schema/examples/ca biên, sơ đồ, ánh xạ và liên kết tài liệu; lưu log.
- [ ] Mở PR và Mạnh review phần QPhong; chốt các quyết định nghiệp vụ còn mở.
- [ ] Mạnh tích hợp với phần AI của Nguyên, validate bản chung v1.0.
- [ ] TPhong chạy Swagger/mock và lưu response/ảnh; Nguyên ghép deck/báo cáo.

## Người nhận và kịch bản demo đề nghị

- **Mạnh:** review paths/schemas `Me`, dữ liệu và quyết định; giữ các thành phần dùng chung của core.
- **TPhong:** dùng contract sau review để dựng demo; ví dụ ở YAML là dữ liệu giả, chưa chứng minh backend có trạng thái.
- **Nguyên:** nhận nội dung Slide 3/6, mô tả đóng góp, link nhánh/commit/PR và log để ghép báo cáo.

1. Login nhận token mock, GET movies lấy UUID phim công khai.
2. PUT favorite lần đầu trả 201; lặp lại trả 200 cùng Favorite, GET favorites chỉ có một quan hệ ở stub có trạng thái.
3. PUT rating `{"score":4.5}` trả 200.
4. PUT progress `{"positionSeconds":630,"completed":false}` trả 200; GET watch-progress để minh họa xem tiếp.
5. Gửi `score=4.7` để minh họa 422, bỏ token để minh họa 401, lưu request/response và ảnh.

Đây là kịch bản đề nghị, chưa chạy demo thật. Kiểm tra thiết kế chưa chứng minh JWT, quyền user A/B, transaction, idempotency hoặc AI runtime.
