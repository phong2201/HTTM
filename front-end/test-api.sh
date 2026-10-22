#!/usr/bin/env bash

# 🧪 API Testing Script
# Hướng dẫn test API endpoints bằng curl

API_BASE_URL="http://localhost:8080"

echo "🚀 Bắt đầu test API Intelligent System"
echo "========================================"
echo ""

# 1. Health Check
echo "1️⃣ Health Check"
curl -X GET "$API_BASE_URL/" -H "Content-Type: application/json"
echo -e "\n"

# 2. Register
echo "2️⃣ Đăng ký tài khoản mới"
TIMESTAMP=$(date +%s)
REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"testuser_$TIMESTAMP\",
    \"email\": \"test_$TIMESTAMP@example.com\",
    \"password\": \"password123\",
    \"age\": 25,
    \"gender\": \"male\"
  }")
echo "$REGISTER_RESPONSE" | jq .
NEW_USERNAME="testuser_$TIMESTAMP"
echo "Username: $NEW_USERNAME"
echo ""

# 3. Login
echo "3️⃣ Đăng nhập"
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$NEW_USERNAME&password=password123")
echo "$LOGIN_RESPONSE" | jq .
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
echo "Token: $ACCESS_TOKEN"
echo ""

# 4. Get Products
echo "4️⃣ Lấy danh sách sản phẩm"
curl -s -X GET "$API_BASE_URL/products" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | jq .
echo ""

# 5. Get Recommendations
echo "5️⃣ Lấy sản phẩm đề xuất"
curl -s -X GET "$API_BASE_URL/recommendations" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" | jq .
echo ""

echo "✅ Test hoàn tất!"
