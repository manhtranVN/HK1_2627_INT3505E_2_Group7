# Báo cáo tiến độ Tuần 12

**Movie Navigator Promax (MNP) · INT3505E · Nhóm 7**
**Mốc báo cáo** 25/11/2026 · **Tổng hợp** Nguyên

Mục tiêu của Design Review là chốt phạm vi MVP và đặc tả các API để đội React có thể thử tích hợp qua mock. Nhóm đã có Project Brief, sơ đồ thiết kế, OpenAPI cho các nhóm API chính, cấu hình Swagger UI/Prism và bộ slide Design Review.

## Việc đã làm và bằng chứng

| Thành viên | Kết quả Tuần 12 | Bằng chứng |
| --- | --- | --- |
| **Mạnh** | Chốt quy ước `/api/v1`, UUID, phân trang, JWT/RBAC và lỗi RFC 7807. Viết đặc tả Auth, Catalog và phần trình bày Slide 5. | [Core API](https://github.com/manhtranVN/HK1_2627_INT3505E_2_Group7/commit/569d3b1736abf5be3165b752ec869bdbb7581dc7), [quy ước và Slide 5](https://github.com/manhtranVN/HK1_2627_INT3505E_2_Group7/commit/db5dd0a7099571816cd199685ddadc338149ebfc), [log lint core](evidence/openapi-validation-report.txt). |
| **QPhong** | Bàn giao Resource Model, ERD 8 bảng và đặc tả 8 thao tác tương tác cá nhân. Chuẩn bị Slide 3 và phần `/me/*` của Slide 6. | [Thiết kế](https://github.com/manhtranVN/HK1_2627_INT3505E_2_Group7/commit/d2d03aebdaab43f9d522ad8e8e87ae7ce5bdc89d), [OpenAPI tương tác](https://github.com/manhtranVN/HK1_2627_INT3505E_2_Group7/commit/00c7dc27fc21eb8481b4078be90f42ef89e86987), [log kiểm tra thiết kế](evidence/qphong-validation-report.txt). |
| **TPhong** | Bàn giao sơ đồ kiến trúc, phân tích đánh đổi, cấu hình Swagger UI/Prism và các phản hồi JSON mẫu phục vụ demo. | [Kiến trúc](https://github.com/manhtranVN/HK1_2627_INT3505E_2_Group7/commit/5f38dd1102b85fc0c3a403bd420c3ec7a2f5fbf7), [cấu hình mock](https://github.com/manhtranVN/HK1_2627_INT3505E_2_Group7/commit/732e22fcc7f5836497fd69a06207adbaf775c663), [ví dụ demo](https://github.com/manhtranVN/HK1_2627_INT3505E_2_Group7/commit/f0e0ef7b577c6f30dd482b9948724fa3192826ce). |
| **Nguyên** | Viết Project Brief, README và hợp đồng cho gợi ý cá nhân, phim tương tự. Bản trên nhánh `feat/brief-ai-plan` qua Redocly với 0 lỗi và 4 cảnh báo có sẵn. Prism chạy trực tiếp trả đúng 7 phản hồi mẫu gợi ý. | [Gợi ý cá nhân](https://github.com/manhtranVN/HK1_2627_INT3505E_2_Group7/commit/5be479edffcd0c872ee9eef9e7bc805654ae3a90), [phim tương tự](https://github.com/manhtranVN/HK1_2627_INT3505E_2_Group7/commit/c7d1162c01575cd2745f5c2b1c459d7f9395da61), [Project Brief và README](https://github.com/manhtranVN/HK1_2627_INT3505E_2_Group7/commit/7acdcf70007711d55c1df5b0f8db2f9eabd1612c). |

Kiểm tra trực tiếp trên Prism cho luồng nhận gợi ý: đăng nhập, chọn thể loại, lấy gợi ý và mở chi tiết phim đều trả HTTP 200. Gọi gợi ý cá nhân khi thiếu token trả HTTP 401 với application/problem+json.

## Việc còn lại và hỗ trợ cần thiết

- **Mạnh và Nguyên** cần review hai đặc tả gợi ý, thống nhất tên `popular_fallback` giữa OpenAPI và [tài liệu kiến trúc](design/architecture.md), rồi tích hợp và kiểm tra bản chung. Hai commit API gợi ý đang trên nhánh của Nguyên.
- **TPhong** cần kiểm tra lại URL mock trước tổng duyệt. Swagger hiện gọi Prism qua `/api/v1` và nhận `404`. Có thể demo bằng cách gọi Prism trực tiếp. Cần rà lại mẫu `401` và `422` để phản ánh đúng endpoint và trường `limit`.
- **Cả nhóm** cần chốt các issue và người phụ trách. Khi báo cáo kết quả, ghi rõ bằng chứng từ mock, log kiểm tra đặc tả hoặc kiểm thử triển khai. Mock tĩnh minh họa hợp đồng và chưa xác nhận lưu dữ liệu, quyền sở hữu hay tính idempotent thực tế.

## Đầu việc đề xuất cho Tuần 13

| Phụ trách | Đầu việc |
| --- | --- |
| **Mạnh** | Chốt hợp đồng tích hợp và khởi tạo Flask cho Auth, Catalog. |
| **QPhong** | Chốt mô hình dữ liệu, chuẩn bị migration và triển khai phần tương tác `/me/*`. |
| **TPhong** | Sửa cấu hình đường dẫn mock, tổng duyệt luồng demo và chuẩn bị môi trường Docker cho nhóm. |
| **Nguyên** | Gán người phụ trách backlog, phối hợp review API gợi ý và chuẩn bị dữ liệu mẫu cho TF-IDF/cosine cùng các ca cold-start. |
