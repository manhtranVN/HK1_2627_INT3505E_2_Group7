# MNP — Movie Navigator Promax

Đồ án INT3505E · Nhóm 7

MNP giúp người xem tìm và lọc phim, lưu phim yêu thích, xem tiếp video mẫu và nhận gợi ý dựa trên sở thích. Quản trị viên dùng chung API để quản lý danh mục phim và thể loại. Xem [Project Brief](docs/project-brief.md) để biết luồng nghiệp vụ trọng tâm và phạm vi MVP.

## Trạng thái Tuần 12

Repo chứa hợp đồng **OpenAPI 3.0.3**, tài liệu thiết kế và cấu hình **Swagger UI + Prism** để demo bằng dữ liệu mẫu. Kiến trúc dự kiến dùng React, Flask REST API dưới `/api/v1`, PostgreSQL và scikit-learn. Mock chạy độc lập với Flask và PostgreSQL.

## Cấu trúc repo

| Thư mục | Nội dung |
| --- | --- |
| [`openapi/`](openapi/) | Hợp đồng API cho hệ thống, xác thực, danh mục, tương tác cá nhân và gợi ý phim. |
| [`mock/`](mock/) | Docker Compose cho Swagger UI và Prism. |
| [`docs/design/`](docs/design/) | Kiến trúc, mô hình tài nguyên, ERD và đánh đổi công nghệ. |
| [`docs/api/`](docs/api/) | Quy ước API, xác thực, phân quyền và lỗi. |
| [`docs/demo/responses/`](docs/demo/responses/) | Phản hồi JSON minh họa cho demo. |
| [`docs/slides/`](docs/slides/) | Nội dung trình bày Design Review. |
| [`old_exercise/`](old_exercise/) | Bài thực hành các tuần trước. |

## Chạy mock

Chạy từ thư mục gốc. Với Docker và Compose, dùng lệnh sau để mở Swagger UI và Prism.

```sh
docker compose -f mock/docker-compose.mock.yml up -d
```

Xem đặc tả tại [Swagger UI](http://localhost:8080). Gọi thử API bằng URL Prism `http://localhost:4010`. Bản mock nhận đường dẫn trực tiếp, chẳng hạn `/health`. Tùy chọn mock hiện hiển thị trong Swagger UI có đuôi `/api/v1` và dẫn tới lỗi `404` khi dùng **Try it out**. Dùng các lệnh bên dưới để gửi request.

Nếu chỉ cần Prism, dùng Node.js và npm.

```sh
npx --yes @stoplight/prism-cli@5.16.0 mock -h 127.0.0.1 -p 4010 openapi/openapi.yaml
```

### Thử API

`mock-token` là giá trị mẫu để gọi endpoint yêu cầu Bearer trong Prism. Trong Windows PowerShell, dùng `curl.exe` thay cho `curl`.

```sh
curl -i http://localhost:4010/health
curl -i "http://localhost:4010/me/recommendations?limit=1" -H "Authorization: Bearer mock-token" -H "Prefer: example=genreFallback"
curl -i "http://localhost:4010/movies/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d/similar?limit=1"
```

Ba lệnh trên trả `200 OK` cho kiểm tra trạng thái, gợi ý cá nhân theo thể loại và phim tương tự. Xem [hợp đồng API](openapi/openapi.yaml) và [ví dụ JSON](docs/demo/responses/) để đối chiếu cấu trúc phản hồi.

Dừng hai dịch vụ Docker bằng lệnh sau. Nếu chạy Prism bằng `npx`, nhấn Ctrl+C trong terminal đang chạy.

```sh
docker compose -f mock/docker-compose.mock.yml down
```
