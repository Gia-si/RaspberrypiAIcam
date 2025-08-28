# EMBEDED_AICAM
*** 
## Stream Camera C270 trên máy tính nhúng raspberry pi 4 model B 4GB với model yolov11s bằng Flask và up ảnh lên google drive 
***
## Phần cứng cần chuẩn bị:
### 1. Raspberry pi 4 Model B( hoặc các loại máy tính nhúng khác như jetson nano, raspberry pi 5, .... )
### 2. Camera c270(hoặc các loại camera usb có thể tích hợp)
### 3. Một thẻ nhớ SD tối thiểu 8GB
### 4. Một bộ nguồn tối thiểu 5VDC 3A
***
## Tiến hành:
#### 1. tải các thư viện trên rapsberri pi 4 bao gồm:
#### Ultralytics=8.3.78, google-api-python-client, google-auth-httplib2, google-auth-oauthlib, opencv2, flask.
#### 2. Vào Google console cloud → APIs & Services → Enabled APIs & services → Enable APIs → bật Google Drive API → OAuth consent screen → External → Create → Điền: App name, User support email, Developer contact email → Save and continue → Credentials → Create credentials → OAuth client ID  → Application type: Desktop app → Create → Download JSON
#### 3. chạy file uptodrive để lấy token ở lần đầu tiên
#### 4. đẩy các file detectwebv3.py và uptodrive.py lên raspberry pi bằng lệnh scp <đường_dẫn_file_trên_máy> pi@<IP_của_Pi>:<đường_dẫn_lưu_trên_Pi>
- ex: scp detectwebv3.py pi@192.168.1.20:/home/pi/
#### 5. tạo service: sudo nano /etc/systemd/system/myservice.service và thêm code này vào:
<img width="527" height="315" alt="image" src="https://github.com/user-attachments/assets/b64dc1f9-6ea8-46d6-ab32-14f2423489f8" />

- [Unit]
-Description=Test autorun Python script
-After=network.target

-[Service]
-WorkingDirectory=/home/pi/yolo
-ExecStart=/home/pi/yolo/venv/bin/python /home/pi/yolo/detectwebv3.py
-Environment="PYTHONPATH=/home/pi/yolo"
-Environment="PATH=/home/pi/yolo/venv/bin:/usr/local/bin:/usr/bin:/bin"
-Restart=always
-User=pi

-[Install]
-WantedBy=multi-user.target
##### giải thích:
-📌 Phần [Unit]
-[Unit]
-Description=Test autorun Python script
-After=network.target


-Description → mô tả service, chỉ để bạn dễ phân biệt khi chạy systemctl list-units.

-After=network.target → chỉ ra rằng service sẽ chạy sau khi mạng khởi động xong. Cái này quan trọng nếu script cần WiFi hoặc Internet.

-👉 Chỗ quan trọng: After rất hữu ích cho các script cần kết nối mạng/MQTT. Nếu không cần, có thể bỏ.

-📌 Phần [Service]
-WorkingDirectory=/home/pi/yolo


-Thư mục hiện tại khi chạy service.

-Quan trọng vì nếu script đọc/ghi file mà không dùng đường dẫn tuyệt đối thì sẽ lỗi nếu không set.

-ExecStart=/home/pi/yolo/venv/bin/python /home/pi/yolo/detectwebv3.py


-Đây là lệnh chính để chạy script.

-venv/bin/python nghĩa là chạy bằng Python trong virtual environment (venv), thay vì Python hệ thống.

-Quan trọng vì đảm bảo script chạy đúng môi trường, đúng thư viện đã cài trong venv.

-Environment="PYTHONPATH=/home/pi/yolo"


-Thiết lập biến môi trường PYTHONPATH, để Python biết tìm module trong /home/pi/yolo.

-Quan trọng nếu bạn import module từ project của mình.

-Environment="PATH=/home/pi/yolo/venv/bin:/usr/local/bin:/usr/bin:/bin"


-Ghi đè PATH, để đảm bảo khi script gọi lệnh ngoài (ví dụ ffmpeg, git, …) thì nó dùng phiên bản trong venv trước tiên.

-Quan trọng nếu bạn cần công cụ đã cài riêng trong venv.

-Restart=always


-Nếu script bị crash thì service sẽ tự khởi động lại.

-Đây là điểm rất quan trọng để đảm bảo script luôn sống.

-User=pi


-Chạy service dưới quyền user pi, thay vì root.

-Quan trọng vì chạy dưới root có thể gây lỗi quyền hoặc không an toàn.

-📌 Phần [Install]
-[Install]
-WantedBy=multi-user.target


-Xác định khi nào service được kích hoạt.

-multi-user.target = chạy ở chế độ multi-user (mặc định sau khi boot xong).

-Đây là điều làm cho service tự động chạy khi reboot
#### kiểm tra:
- 1. reload lại systemd để nó nhận service mới: sudo systemctl daemon-reload  

- 2. chạy service ngay lập tức (không cần reboot): sudo systemctl start test_autorun.service  

- 3. kiểm tra trạng thái: sudo systemctl status test_autorun.service
  
- 4.Nếu thấy failed thì dùng thêm lệnh này để coi log lỗi chi tiết:
-sudo journalctl -u test_autorun.service -n 50 --no-pager
