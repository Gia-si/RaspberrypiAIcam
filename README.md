# 📸 EMBEDED_AICAM  

## 🚀 Stream Camera C270 trên Raspberry Pi 4 (4GB) với YOLOv11s bằng Flask và upload ảnh lên Google Drive  

---

## 🛠️ Phần cứng cần chuẩn bị
1. **Raspberry Pi 4 Model B 4GB** (hoặc các SBC khác: Jetson Nano, Raspberry Pi 5, …)  
2. **Camera Logitech C270** (hoặc camera USB tương thích)  
3. **Thẻ nhớ SD ≥ 8GB**  
4. **Nguồn 5VDC ≥ 3A**  

---

## ⚙️ Các bước thực hiện

### 1. Cài đặt thư viện trên Raspberry Pi
Các thư viện cần thiết:  

```bash
pip install ultralytics==8.3.78
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install opencv-python flask
2. Cấu hình Google Drive API
Truy cập Google Console Cloud → APIs & Services → Enabled APIs & services

Chọn Enable APIs → Bật Google Drive API

Vào OAuth consent screen → Chọn External → Create

Điền thông tin: App name, User support email, Developer contact email → Save and continue

Vào Credentials → Create credentials → OAuth client ID

Application type: Desktop app → Create

Download JSON về để sử dụng

3. Lấy token lần đầu
Chạy file uptodrive.py để tạo token kết nối Google Drive.

4. Upload code lên Raspberry Pi
Dùng scp để đẩy file từ máy tính sang Pi:

bash
Copy code
scp detectwebv3.py pi@<IP_Raspberry>:/home/pi/
scp uptodrive.py pi@<IP_Raspberry>:/home/pi/
Ví dụ:

bash
Copy code
scp detectwebv3.py pi@192.168.1.20:/home/pi/
5. Tạo service tự động chạy khi boot
Tạo file service:

bash
Copy code
sudo nano /etc/systemd/system/test_autorun.service
Thêm nội dung sau:

ini
Copy code
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
📖 Giải thích service
🔹 [Unit]
Description → mô tả service

After=network.target → chạy sau khi mạng khởi động (cần nếu script dùng WiFi/MQTT)

🔹 [Service]
WorkingDirectory → thư mục chứa script

ExecStart → lệnh chạy script (dùng Python trong venv)

Environment="PYTHONPATH=..." → thêm đường dẫn module

Environment="PATH=..." → ưu tiên công cụ trong venv

Restart=always → tự khởi động lại khi crash

User=pi → chạy dưới user pi (không phải root)

🔹 [Install]
WantedBy=multi-user.target → cho phép service chạy khi boot xong

✅ Quản lý service
1. Reload để nhận service mới
bash
Copy code
sudo systemctl daemon-reload
2. Chạy service ngay lập tức (không cần reboot)
bash
Copy code
sudo systemctl start test_autorun.service
3. Kiểm tra trạng thái service
bash
Copy code
sudo systemctl status test_autorun.service
4. Xem log lỗi chi tiết (nếu failed)
bash
Copy code
sudo journalctl -u test_autorun.service -n 50 --no-pager
📌 Bảng lệnh tóm tắt quản lý service
Lệnh	Chức năng
sudo systemctl start test_autorun.service	Chạy service
sudo systemctl stop test_autorun.service	Dừng service
sudo systemctl restart test_autorun.service	Khởi động lại service
sudo systemctl enable test_autorun.service	Cho phép tự chạy khi boot
sudo systemctl disable test_autorun.service	Tắt tự chạy khi boot
systemctl status test_autorun.service	Kiểm tra trạng thái
journalctl -u test_autorun.service -f	Xem log realtime

