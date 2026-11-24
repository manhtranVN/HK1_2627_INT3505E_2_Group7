#!/usr/bin/env bash
# Script tiện ích khởi động Mock Server và Swagger UI cho MNP

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
REPO_ROOT="$(dirname "$DIR")"
SPEC_FILE="$REPO_ROOT/openapi/openapi.yaml"

echo "  MNP - Movie Navigator Promax | Mock Server & Swagger UI"
echo "  Môn học: INT3505E - Nhóm 7 - Tuần 12 Design Review"

if [ ! -f "$SPEC_FILE" ]; then
    echo "Lỗi: Không tìm thấy file đặc tả tại $SPEC_FILE"
    exit 1
fi

echo "Đã tìm thấy OpenAPI spec: $SPEC_FILE"

# Kiểm tra Docker
if command -v docker >/dev/null 2>&1 && command -v docker compose >/dev/null 2>&1; then
    echo "Phát hiện Docker và Docker Compose. Khởi động môi trường container..."
    echo "   - Swagger UI: http://localhost:8080"
    echo "   - Prism Mock: http://localhost:4010/api/v1"
    echo "----------------------------------------------------------"
    docker compose -f "$DIR/docker-compose.mock.yml" up -d
    echo "Khởi động thành công. Đang chạy ngầm trong container."
    echo "Xem logs: docker compose -f $DIR/docker-compose.mock.yml logs -f"
    echo "Dừng lại: docker compose -f $DIR/docker-compose.mock.yml down"
    exit 0
fi

# Fallback nếu không có Docker, kiểm tra npx prism
if command -v npx >/dev/null 2>&1; then
    echo "Docker không khả dụng. Chuyển sang chạy Prism trực tiếp bằng npx..."
    echo "   - Prism Mock: http://localhost:4010/api/v1"
    echo "----------------------------------------------------------"
    npx @stoplight/prism-cli mock -p 4010 "$SPEC_FILE"
    exit 0
fi

echo "Lỗi: Cần cài đặt Docker hoặc Node.js để chạy mock server."
exit 1
