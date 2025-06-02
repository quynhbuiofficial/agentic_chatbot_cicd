#!/bin/bash
# Cập nhật gói và cài Apache (trên Ubuntu)
apt update -y
apt install apache2 -y

# Khởi động Apache và cấu hình chạy khi khởi động lại
systemctl start apache2
systemctl enable apache2

# Tạo nội dung cho trang index
cd /var/www/html
echo "<html>" > index.html
echo "<h1>Welcome to MyWebsite</h1>" >> index.html
echo "<h3>Test EC2 server - From QuynhBui</h3>" >> index.html

echo "</html>" >> index.html
