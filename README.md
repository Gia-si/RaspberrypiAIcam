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
### 1. tải các thư viện trên rapsberri pi 4 bao gồm:
#### Ultralytics=8.3.78, google-api-python-client, google-auth-httplib2, google-auth-oauthlib, opencv2, flask.

#### 2. đẩy các file detectwebv3.py và uptodrive.py lên raspberry pi bằng lệnh scp <đường_dẫn_file_trên_máy> pi@<IP_của_Pi>:<đường_dẫn_lưu_trên_Pi>
- ex: scp detectwebv3.py pi@192.168.1.20:/home/pi/
### 3. Vào Google console cloud → APIs & Services → Enabled APIs & services → Enable APIs → bật Google Drive API → OAuth consent screen → External → Create.


