# Project Brief — Movie Navigator Promax

**Môn học** INT3505E · **Nhóm** 7 · **Mốc** Design Review Tuần 12

## Bài toán và giá trị

Khi danh mục có nhiều phim, người xem mất thời gian lọc để tìm phim hợp sở thích và khó quay lại đúng vị trí của phim đang xem dở. Movie Navigator Promax (MNP) gom việc khám phá phim, lưu sở thích và xem tiếp vào cùng một luồng. Phần gợi ý giúp người xem chọn nhanh hơn bằng danh sách có lý do cụ thể, kể cả khi tài khoản mới chưa có lịch sử tương tác.

## Các bên sử dụng API

| Consumer | Nhu cầu |
| --- | --- |
| React Web | Khách xem danh mục, chi tiết và phim tương tự. Người đã đăng nhập lưu sở thích, tương tác với phim và nhận gợi ý cá nhân. |
| Admin UI | Quản trị viên thêm, sửa, ẩn phim và thêm thể loại qua API Catalog. |
| Batch AI | Tác vụ nội bộ xử lý metadata phim theo lô, tạo vector nội dung để mô-đun gợi ý sử dụng khi xếp hạng. |

## Use case chính

| Người dùng | Mục tiêu |
| --- | --- |
| Khách truy cập | Tìm, lọc phim theo từ khóa và thể loại, mở chi tiết và xem danh sách phim tương tự. |
| Người dùng có tài khoản | Đăng ký hoặc đăng nhập, sau đó lưu thể loại yêu thích. |
| Người dùng đã đăng nhập | Thêm phim yêu thích, chấm điểm và lưu tiến độ để xem tiếp video mẫu. |
| Người dùng đã đăng nhập | Xem gợi ý cá nhân theo thứ hạng, có điểm và lý do để quyết định mở phim nào. |
| Quản trị viên | Thêm, sửa hoặc ẩn phim trong danh mục và bổ sung thể loại. |

## Luồng trọng tâm — nhận gợi ý cho tài khoản mới

1. Người xem đăng nhập qua `POST /auth/login`. React Web dùng JWT nhận được để gọi các API cá nhân.
2. Người xem chọn thể loại yêu thích. React Web gửi danh sách thể loại qua `PUT /me/preferences/genres`.
3. React Web gọi `GET /me/recommendations?limit=10`. Khi chưa có đủ lịch sử tương tác, API ưu tiên phim công khai khớp thể loại đã chọn. Khi thiếu thể loại phù hợp, API dùng danh sách phim phổ biến. Phản hồi có `reason`, `score`, `strategy` và `modelVersion`. `modelVersion` là `null` khi dùng phương án dự phòng.
4. Người xem chọn một gợi ý. React Web mở chi tiết qua `GET /movies/{movieId}`.

Các đường dẫn trên dùng tiền tố `/api/v1` trên Flask. Trong Design Review, nhóm minh họa luồng bằng OpenAPI và các phản hồi mẫu từ mock.

## Phạm vi MVP

**Trong phạm vi.** Danh mục phim có tìm kiếm, lọc và phân trang. Khách dùng các API công khai. JWT xác thực người dùng và phân biệt quyền người dùng với quyền quản trị. Người dùng có thể lưu thể loại yêu thích, đánh dấu phim yêu thích, chấm điểm và lưu tiến độ xem. Phần gợi ý dùng TF-IDF và cosine similarity cho mô hình dựa trên nội dung, có phương án dự phòng khi thiếu dữ liệu. Tính năng phát giới hạn ở 2–3 video mẫu có quyền sử dụng.

**Ngoài phạm vi.** Chuyển mã video, phân chất lượng 720p/4K theo vai trò, mở rộng thành dịch vụ phát trực tuyến quy mô lớn, và gợi ý bằng collaborative filtering hoặc deep learning.

[Xem hợp đồng OpenAPI](../openapi/openapi.yaml) · [Kiến trúc hệ thống](design/architecture.md) · [Mô hình tài nguyên và dữ liệu](design/resource-vs-db.md)
