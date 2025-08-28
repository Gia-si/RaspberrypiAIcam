# Hướng Dẫn Streaming Camera Logitech C270 với YOLOv11s trên Raspberry Pi 4 bằng Flask và Upload Ảnh lên Google Drive

---

## 1. Phần cứng cần chuẩn bị

- **Raspberry Pi 4 Model B** (hoặc các máy tính nhúng khác như Jetson Nano, Raspberry Pi 5,...)
- **Camera USB Logitech C270** (hoặc các loại camera USB khác có thể tích hợp)
- **Thẻ nhớ SD tối thiểu 8GB**
- **Nguồn cấp tối thiểu 5VDC 3A**

---

## 2. Cài đặt thư viện trên Raspberry Pi 4

Sử dụng python3 và pip để cài đặt các thư viện cần thiết:

pip install ultralytics==8.3.78 google-api-python-client google-auth-httplib2 google-auth-oauthlib opencv-python flask

text

---

## 3. Thiết lập Google Drive API

1. Truy cập Google Cloud Console:
   - Vào **APIs & Services** → **Enabled APIs & services** → **Enable APIs**
   - Tìm và kích hoạt **Google Drive API**

2. Cấu hình màn hình OAuth consent screen:
   - Chọn **External**
   - Nhấn **Create**
   - Điền các thông tin cần thiết: 
     - App name
     - User support email
     - Developer contact email
   - Nhấn **Save and Continue**

3. Tạo Credentials:
   - Vào **Credentials** → **Create Credentials** → **OAuth client ID**
   - Application type: **Desktop app**
   - Nhấn **Create**
   - Tải file JSON (chứa client secrets), lưu vào thư mục làm việc

---

## 4. Khởi chạy script lấy token Google Drive lần đầu

Chạy script `uptodrive.py` để xác thực và lấy token truy cập Google Drive lần đầu.

---

## 5. Upload các file lên Raspberry Pi

Sử dụng lệnh `scp` để gửi file từ máy tính tới Raspberry Pi:

scp <đường_dẫn_file_trên_máy> pi@<IP_của_Pi>:<đường_dẫn_lưu_trên_Pi>

text

Ví dụ:

scp detectwebv3.py pi@192.168.1.20:/home/pi/
scp uptodrive.py pi@192.168.1.20:/home/pi/

text

---

## 6. Tạo systemd Service để tự động chạy script khi khởi động

### 6.1. Tạo file service

Mở file cấu hình service:

sudo nano /etc/systemd/system/myservice.service

text

### 6.2. Dán đoạn cấu hình sau vào:

[Unit]
Description=Test autorun Python script
After=network.target

[Service]
WorkingDirectory=/home/pi/yolo
ExecStart=/home/pi/yolo/venv/bin/python /home/pi/yolo/detectwebv3.py
Environment="PYTHONPATH=/home/pi/yolo"
Environment="PATH=/home/pi/yolo/venv/bin:/usr/local/bin:/usr/bin:/bin"
Restart=always
User=pi

[Install]
WantedBy=multi-user.target

text

### Giải thích cấu hình:

- `[Unit]`
  - **Description**: mô tả service giúp dễ nhận biết.
  - **After=network.target**: chạy service sau khi mạng được kích hoạt (quan trọng nếu script cần kết nối internet).

- `[Service]`
  - **WorkingDirectory**: thư mục làm việc hiện tại, tránh lỗi khi đọc/ghi file không dùng đường dẫn tuyệt đối.
  - **ExecStart**: lệnh chạy script, ở đây chạy Python trong virtual environment (`venv`).
  - **Environment**:
    - `PYTHONPATH` giúp Python biết đường dẫn import các module trong dự án.
    - `PATH` ưu tiên tìm kiếm lệnh trong `venv`.
  - **Restart=always**: tự động restart nếu script bị crash, giúp duy trì hoạt động liên tục.
  - **User=pi**: chạy dưới quyền user `pi`, an toàn và tránh lỗi quyền.

- `[Install]`
  - **WantedBy=multi-user.target**: service sẽ tự động khởi động khi boot vào chế độ multi-user (chế độ thường dùng).

---

## 7. Quản lý Service

### 7.1. Reload lại daemon systemd để nhận service mới

sudo systemctl daemon-reload

text

### 7.2. Khởi chạy service ngay mà không cần reboot

sudo systemctl start myservice.service

text

### 7.3. Kiểm tra trạng thái service

sudo systemctl status myservice.service

text

### 7.4. Xem log chi tiết nếu bị lỗi (xem 50 dòng cuối)

sudo journalctl -u myservice.service -n 50 --no-pager

text

---

# Kết luận

Tài liệu trên tổng hợp các bước chuẩn bị phần cứng, cài đặt phần mềm, thiết lập Google Drive API cũng như cấu hình systemd service giúp tự động chạy ứng dụng streaming camera Logitech C270 với YOLOv11s và Flask trên Raspberry Pi 4, đồng thời upload ảnh lên Google Drive một cách tự động, giúp dễ dàng triển khai và quản lý ứng dụng của bạn.
