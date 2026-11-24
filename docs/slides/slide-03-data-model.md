# Slide 3 - Resource Model và ERD

Người phụ trách: **QPhong**. Nội dung để Nguyên ghép deck Design Review; chưa phải slide trình chiếu hoàn chỉnh.

## Nội dung đưa lên slide

- [Resource Model](../design/resource-model.drawio): trang 01 là cây URI, trang 02 là API representations. UUID định danh tài nguyên; URL dùng danh từ số nhiều.
- [ERD](../design/erd.drawio): 8 bảng, 10 FK. PK vàng, FK xanh, PK/FK tím; PK ghép chặn trùng theo cặp ở bảng nối/tương tác.
- API khác schema lưu trữ: Movie nhúng `genres[]`, ẩn `password_hash` và `video_path`; `/me/*` suy ra user từ JWT `sub`.
- `watch_progress` giữ trạng thái xem hiện tại theo user/phim. Lịch sử sự kiện xem là khả năng mở rộng, chưa thêm bảng vào ERD 8 bảng.

Bố trí khi ghép: dùng ERD SVG và cây URI SVG; phần giải thích DB/API chỉ giữ một ví dụ `Movie.genres[]`. Mở trang representation nếu cần trả lời sâu hơn.

## Ghi chú và Q&A

1. Vì sao không biến mỗi bảng thành một endpoint? Consumer làm việc với resource/representation; bảng nối phục vụ lưu trữ và ràng buộc dữ liệu.
2. Vì sao cần khóa ghép? Mỗi cặp user/phim chỉ có một favorite, một rating và một trạng thái progress; gọi lại PUT không tạo thêm bản ghi.
3. Vì sao không trả `userId` để client tự gửi? Chủ sở hữu được xác định từ token; backend vẫn phải xác minh JWT và quyền sở hữu.

Đọc chi tiết tại [Resource vs DB](../design/resource-vs-db.md) (gồm chi tiết thuộc tính). JSON camelCase theo core; DB dùng snake_case. Chi tiết tích hợp và quyết định còn mở nằm trong [handoff](../handoff/qphong-week12.md).
