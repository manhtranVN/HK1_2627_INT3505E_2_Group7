# Slide 6 - Phần API tương tác /me/*

Người phụ trách: **QPhong**; phần AI trên cùng slide do Nguyên phụ trách. Nội dung Markdown để ghép deck, chưa phải kết quả demo đã chạy.

## Nội dung đưa lên slide

Contract: [openapi/openapi.yaml](../../openapi/openapi.yaml), prefix `/api/v1`, JWT `sub` xác định user hiện tại.

| Method | Resource | Ý nghĩa |
|---|---|---|
| GET | `/me/favorites` | Đọc danh sách yêu thích |
| PUT / DELETE | `/me/favorites/{movieId}` | Bảo đảm có / bỏ quan hệ yêu thích |
| PUT | `/me/ratings/{movieId}` | Tạo hoặc thay thế điểm đánh giá |
| PUT | `/me/watch-progress/{movieId}` | Thay thế vị trí xem tuyệt đối và trạng thái hoàn tất |
| PUT | `/me/preferences/genres` | Thay thế toàn bộ tập thể loại |

**Idempotency:** gửi cùng PUT nhiều lần vẫn cho cùng trạng thái lưu trữ. Favorites chỉ có một quan hệ; rating thay điểm cũ; progress gửi vị trí tuyệt đối, không cộng thêm số giây; preferences thay cả tập trong transaction.

## Ví dụ trình bày từ bản thiết kế hiện tại

- PUT favorite lần đầu `201`, lần lặp `200` cùng resource; không tạo trùng quan hệ.
- PUT rating `{"score":4.5}` trả `200`; `score=4.7` vi phạm bước 0.5, trả `422`.
- PUT progress `{"positionSeconds":630,"completed":false}` trả `200`.
- Thiếu bearer token trả `401`; phim không tồn tại/không được phép xem trả `404` theo operation.

Tên trường/status đã căn chỉnh theo core; các quyết định nghiệp vụ còn cần [review trong handoff](../handoff/qphong-week12.md) trước khi ghép deck. Kịch bản và người nhận nằm trong [bàn giao QPhong](../handoff/qphong-week12.md).

## Q&A

PUT là thay thế trạng thái tài nguyên, không phải thêm một bản ghi mỗi lần gọi. DELETE idempotent về trạng thái cuối; không bắt buộc mọi lần gọi phải có body hoặc status khác nhau. Mock trả example tĩnh chưa chứng minh DB, ownership hoặc idempotency thực tế.
