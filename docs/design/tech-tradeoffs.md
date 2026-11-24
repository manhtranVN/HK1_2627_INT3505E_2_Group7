# Phân tích Lựa chọn Công nghệ & Đánh đổi Kiến trúc

---

## 1. Đánh đổi 1: Modular Monolith vs. Microservices

### 1.1. Bối cảnh & Bài toán

Dự án yêu cầu thiết kế hệ thống có tính module hóa cao, hợp đồng API rõ ràng và khả năng kiểm thử độc lập. 

### 1.2. Phân tích so sánh các phương án

| Tiêu chí đánh giá                           | Phương án A: Microservices phân tán                                                                        | Phương án B: Modular Monolith - Được chọn                                                                                                                         |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Độ phức tạp hạ tầng**              | Rất cao: Cần API Gateway, Service Discovery, Message Broker, Distributed Tracing.                             | **Thấp - Trung bình:** Đóng gói trong 1 dịch vụ web Flask duy nhất, quản lý bằng 1 Docker container.                                                    |
| **Giao tiếp mạng & Độ trễ**           | Giao tiếp qua mạng (HTTP REST hoặc gRPC) giữa các service gây trễ và rủi ro lỗi mạng từng phần.    | **Cực thấp:** Giao tiếp qua lời gọi hàm nội bộ giữa các module, không phát sinh chi phí mạng.                                                       |
| **Tính nhất quán dữ liệu**            | Phức tạp: Mỗi service có DB riêng, cần triển khai Saga Pattern hoặc Two-Phase Commit khi ghi dữ liệu. | Mạnh mẽ: Dùng chung 1 cơ sở dữ liệu PostgreSQL với các schema/tables phân định rõ ràng.                                                                   |
| **Chi phí triển khai & Debug**           | Khó khăn khi debug lỗi liên service; môi trường kiểm thử cục bộ nặng nề trên máy cá nhân.      | Nhanh chóng & dễ kiểm soát: Đặt breakpoint debug dễ dàng, chạy trọn vẹn bằng `docker compose up`.                                                         |
| **Khả năng tách dịch vụ tương lai** | Đã tách sẵn.                                                                                                | Dễ dàng: Code tuân thủ ranh giới Controller - Service - Repository, hoàn toàn có thể trích xuất module `AI Recommender` thành service độc lập khi cần. |

### 1.3. Quyết định & Đánh đổi

* **Quyết định:** Chọn **Modular Monolith** cho giai đoạn MVP đồ án môn học.
* **Đánh đổi chấp nhận:**
  * *Chấp nhận:* Tất cả các module (`Auth`, `Catalog`, `Interactions`, `AI`) cùng triển khai và scale theo một khối.
  * *Biện pháp kiểm soát:* Nghiêm cấm việc module này truy vấn trực tiếp bảng dữ liệu của module khác mà không thông qua Service Interface nội bộ. Nếu sau này yêu cầu môn học bắt buộc có 2 service độc lập giao tiếp qua mạng, module `AI Recommender` sẽ được tách ra thành dịch vụ độc lập đầu tiên.

---

## 2. Đánh đổi 2: Tách Video Media khỏi Cơ sở Dữ liệu

### 2.1. Bối cảnh & Bài toán

Nền tảng MNP cho phép người dùng xem phim trực tuyến. Cần lựa chọn phương thức lưu trữ file video demo (định dạng `.mp4`, kích thước từ 50MB – 300MB/phim).

### 2.2. Phân tích so sánh

| Tiêu chí                             | Lưu Binary trực tiếp trong PostgreSQL                                                                                                         | Lưu Video trên Media Server / File Storage - Được chon                                                                                                                                               |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Hiệu năng I/O Database**     | Kém: Bộ nhớ RAM và cache buffer của PostgreSQL bị chiếm dụng bởi dữ liệu video nhị phân, làm chậm các câu lệnh SQL nghiệp vụ. | **Tối ưu:** PostgreSQL chỉ lưu chuỗi đường dẫn `streamUrl`; I/O video do web server tĩnh hoặc storage xử lý.                                                                         |
| **Kích thước & Sao lưu DB**  | Tệ: Backup `pg_dump` mất nhiều gigabyte, thời gian phục hồi thảm họa kéo dài.                                                        | Nhẹ: Database dump chỉ vài Megabyte dữ liệu quan hệ, sao lưu trong vài giây.                                                                                                                    |
| **Hỗ trợ HTTP Range Requests** | Rất phức tạp: Cần viết code backend tự động đọc byte từ cột BLOB để cắt chunk theo header `Range: bytes=start-end`.              | Tự chiên & chuẩn hóa: Các máy chủ tĩnh (Nginx/Flask static) tự động hỗ trợ mã trạng thái `206 Partial Content`, cho phép người dùng tua nhanh video tức thì trên trình duyệt. |

### 2.3. Quyết định & Đánh đổi

* **Quyết định:** **Tách hoàn toàn file video ra khỏi Database**. File video được đặt trong thư mục lưu trữ media riêng (`static/media/` hoặc Object Storage/CDN).
* **Phạm vi MVP:** Giới hạn 2–3 video mã nguồn mở được cấp phép Creative Commons. Chỉ các phim có video tương ứng mới hiển thị nút xem; các phim còn lại chỉ phục vụ khám phá và thử nghiệm thuật toán AI.

---

## 3. Đánh đổi 3: Thuật toán AI Gợi ý Phim 

### 3.1. Bối cảnh & Bài toán

Cần xây dựng hệ thống gợi ý phim cá nhân hóa cho người dùng dựa trên sở thích thể loại, danh sách phim yêu thích và lịch sử đánh giá sao.

### 3.2. Phân tích so sánh

| Tiêu chí                                                         | Deep Learning / Collaborative Filtering                                                                                    | Content-Based - Được chọn cho MVP                                                                                                                                                                                        |
| ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Vấn đề Cold-Start (Người dùng/Phim mới)**           | Rất yếu: Cần ma trận tương tác lớn (người dùng phải đánh giá nhiều phim) thì mô hình mới học được. | **Tốt:** Gợi ý dựa trên thuộc tính nội dung phim (thể loại, mô tả, đạo diễn), người dùng chỉ cần chọn sở thích ban đầu là đã có kết quả.                                                 |
| **Tài nguyên tính toán & Huấn luyện**                  | Tốn GPU, thời gian train lâu, khó chạy mượt mà trên máy tính cá nhân của sinh viên hoặc server chấm bài. | **Rất nhẹ:** `scikit-learn` tính toán ma trận TF-IDF trong vài giây trên CPU thông thường; lưu artifact vector ra đĩa và tải lên RAM nhanh chóng.                                                   |
| **Tính minh bạch & Giải thích được (Explainability)** | Hộp đen (Black-box): Rất khó giải thích lý do gợi ý cho người dùng một cách chính xác.                     | **Rõ ràng (White-box):** Dễ dàng sinh lý do trực quan theo dữ liệu thực tế (Ví dụ: *"Vì bạn thích thể loại Khoa học viễn tưởng"* hoặc *"Tương tự phim Inception bạn đánh giá 5 sao"*). |

### 3.3. Quyết định & Chiến lược Fallback

* **Quyết định:** Dùng **TF-IDF + Cosine Similarity** của `scikit-learn` làm baseline vững chắc cho MVP.
* **Chiến lược Fallback:**
  * Khi người dùng chưa có bất kỳ tương tác nào hoặc khi module AI gặp sự cố tính toán: Hệ thống tự động chuyển sang chiến lược dự phòng (`strategy: "fallback_popular"`), trả về danh sách các bộ phim có điểm đánh giá trung bình cao nhất và phổ biến nhất.

---

## 4. Đánh đổi 4: Lựa chọn Tech Stack & Công cụ Triển khai

### 4.1. Backend Framework: Flask vs. FastAPI

* **Lựa chọn:** **Flask**.
* **Lý do:** Flask có tính linh hoạt cao, cấu trúc đơn giản, không áp đặt ORM hay cơ chế validation cố định, giúp nhóm kiểm soát chi tiết từng header HTTP, mã lỗi RFC 7807 (`application/problem+json`) và ranh giới các tầng theo đúng chuẩn môn học REST API. Đội ngũ thành viên đã có nền tảng Python vững chắc.

### 4.2. Cơ sở dữ liệu: PostgreSQL vs. MongoDB

* **Lựa chọn:** **PostgreSQL 15**.
* **Lý do:**
  * Mối quan hệ giữa người dùng và phim (yêu thích, đánh giá, tiến độ xem) mang bản chất quan hệ nhiều - nhiều cao.
  * PostgreSQL hỗ trợ cực tốt các ràng buộc toàn vẹn: `UNIQUE(user_id, movie_id)`, khóa ngoại `ON DELETE CASCADE`.
  * Khả năng mở rộng trong tương lai: PostgreSQL hỗ trợ extension `pgvector` nếu nhóm muốn nâng cấp lên mô hình Semantic Search / Vector Embedding ở giai đoạn sau.

### 4.3. Công cụ Mocking: Stoplight Prism vs. Viết Mock Server thủ công

* **Lựa chọn:** **Stoplight Prism + Swagger UI**.
* **Lý do:**
  * Tiếp cận chuẩn **API-First**: Không cần viết một dòng code mock nào bằng tay. Prism tự động phân tích file `openapi/openapi.yaml`, đọc schema và trường `examples` để trả về phản hồi chuẩn xác.
  * Tự động kiểm tra tính hợp lệ của request gửi lên: Nếu client gửi sai kiểu dữ liệu hoặc thiếu trường bắt buộc, Prism tự động phản hồi lỗi 422/400.

### 4.4. Kiểm thử Chịu tải: Locust vs. Apache JMeter

* **Lựa chọn:** **Locust**.
* **Lý do:** Kịch bản kiểm thử viết hoàn toàn bằng mã Python (`locustfile.py`), dễ tích hợp vào kho mã Git, hỗ trợ giả lập hàng nghìn người dùng ảo đồng thời đo lường các chỉ số quan trọng (RPS, Latency p95, tỷ lệ lỗi) một cách trực quan trên giao diện Web.

---

## 5. Bảng tổng hợp Đánh đổi Kỹ thuật

Dành cho phần trả lời phản biện nhanh trong buổi thuyết trình:

| Quyết định kỹ thuật        | Phương án lựa chọn  | Đánh đổi chấp nhận                                                             | Lợi ích đạt được                                                                                   |
| ------------------------------- | ------------------------ | ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| **Kiến trúc dịch vụ** | Modular Monolith         | Phải scale toàn bộ ứng dụng cùng nhau.                                         | Triển khai nhanh, không lỗi mạng nội bộ, quản lý transaction ACID dễ dàng.                      |
| **Lưu trữ video**       | Media Storage độc lập | Cần quản lý đồng bộ đường dẫn URL giữa file tĩnh và DB.                 | DB nhẹ, backup tức thì, hỗ trợ HTTP Range stream mượt mà.                                         |
| **Thuật toán gợi ý**  | Content-based (TF-IDF)   | Không bắt được xu hướng cộng đồng phức tạp của Collaborative Filtering. | Xử lý triệt để cold-start cho phim mới, giải thích được lý do gợi ý, tốn rất ít RAM/CPU. |
| **Định danh dữ liệu** | UUID v4                  | URL dài hơn, tốn thêm vài byte lưu trữ chỉ mục trong DB.                    | Không để lộ tổng số lượng bản ghi hệ thống, tránh tấn công đoán ID tuần tự.             |
| **Định dạng lỗi**     | RFC 7807 ProblemDetails  | Phải viết thêm serializer chuẩn hóa mọi exception.                             | Client xử lý lỗi thống nhất tại một nơi duy nhất trên frontend.                                 |
