# Môi trường Mock Server và Swagger UI Độc lập

---

## 1. Kiến trúc Môi trường Mock

Hệ thống mock bao gồm 2 dịch vụ độc lập đóng gói qua Docker:

1. **Stoplight Prism Mock Server - Cổng 4010:**
   * Lắng nghe tại: `http://localhost:4010/api/v1`
   * Cơ chế: Tự động phân tích cú pháp `openapi/openapi.yaml`. Khi nhận request, Prism kiểm tra tính hợp lệ của headers, query parameters và request body; sau đó tự động trả về mock response tương ứng với các examples và schema đã đặc tả.
2. **Swagger UI - Cổng 8080:**
   * Truy cập qua trình duyệt: `http://localhost:8080`
   * Cơ chế: Nạp trực tiếp file `openapi/openapi.yaml`, cho phép người dùng xem tài liệu trực quan và bấm nút **"Try it out"** để gửi request trực tiếp sang server mock.

---

## 2. Hướng dẫn Khởi động Nhanh

### Cách 1: Sử dụng Docker Compose

Từ thư mục gốc của dự án, chạy lệnh:

```bash
docker compose -f mock/docker-compose.mock.yml up -d
```

Sau khi chạy xong:

* Mở trình duyệt truy cập Swagger UI: **[http://localhost:8080](http://localhost:8080)**
* Endpoint Mock Server API: **`http://localhost:4010/api/v1`**

Để dừng mock server:

```bash
docker compose -f mock/docker-compose.mock.yml down
```

### Cách 2: Sử dụng Script tự động `run-mock.sh`

```bash
chmod +x mock/run-mock.sh
./mock/run-mock.sh
```

### Cách 3: Chạy trực tiếp bằng Node.js hoặc npx

```bash
npx @stoplight/prism-cli mock -p 4010 openapi/openapi.yaml
```

---

## 3. Thử nghiệm Nhanh với cURL

Bạn có thể mở một cửa sổ terminal mới và chạy các lệnh cURL mẫu sau để kiểm tra phản hồi từ Mock Server:

### 3.1. Kiểm tra trạng thái hệ thống Health Check

```bash
curl -i http://localhost:4010/healthz
```

**Kết quả kỳ vọng:** HTTP `200 OK`, JSON `{"status": "healthy"}`.

### 3.2. Đăng nhập và lấy JWT Token

```bash
curl -i -X POST http://localhost:4010/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@mnp.vn", "password": "Password123!"}'
```

**Kết quả kỳ vọng:** HTTP `200 OK`, trả về `accessToken` dạng JWT và thông tin tài khoản.

### 3.3. Tra cứu danh mục phim có phân trang và lọc

```bash
curl -i "http://localhost:4010/api/v1/movies?page=1&limit=20&genre=action"
```

**Kết quả kỳ vọng:** HTTP `200 OK`, danh sách items kèm đối tượng meta PageMeta.

### 3.4. Thử nghiệm mã lỗi RFC 7807

Prism hỗ trợ ép kiểu phản hồi mã lỗi thông qua header `Prefer`:

```bash
curl -i -X POST http://localhost:4010/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -H "Prefer: code=401" \
  -d '{"email": "user@mnp.vn", "password": "WrongPassword"}'
```

**Kết quả kỳ vọng:** HTTP `401 Unauthorized`, `Content-Type: application/problem+json`, cấu trúc chuẩn ProblemDetails.
