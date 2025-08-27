from flask import Flask, Response
import cv2
import threading
import time
from ultralytics import YOLO
import tempfile
from uptodrive import upload_to_drive
import os
import queue

"""
===========================
Danh mục bệnh cây lettuce
===========================
0. Bacterial Leaf Spot    → Vi khuẩn gây đốm lá
1. Downy mildew           → Bệnh sương mai
2. Lettuce mosaic virus   → Virus khảm rau diếp
3. Powdery mildew         → Bệnh phấn trắng
4. Septoria blight        → Bệnh bạc lá nhiễm trùng huyết
"""

# =======================
# Khởi tạo Flask
# =======================
app = Flask(__name__)

# =======================
# Cấu hình YOLO + Camera
# =======================
model_path   = "bestmodel.pt"
camera_idx   = 0
min_thresh   = 0.5  #conf
process_every = 15  # xử lý mỗi 15 frame

model  = YOLO(model_path)
labels = model.names

cap = cv2.VideoCapture(camera_idx)
if not cap.isOpened():
    raise RuntimeError("❌ Cannot open camera")

# cấu hình độ phân giải
resW, resH = 640, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, resW)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resH)

# màu bbox
bbox_colors = [
    (164, 120, 87), (68, 148, 228), (93, 97, 209),
    (178, 182, 133), (88, 159, 106), (96, 202, 231)
]

# =======================
# Biến toàn cục
# =======================
latest_frame = None      # frame sao chép  từ frame gốc từ camera
last_boxes   = []        # kết quả YOLO
frame_count  = 0         # số frame đã chạy
lock = threading.Lock()  # tạo một khóa để tranh khi các biến chung bị nhiều thread truy cập gây xung đột

frame_rate_buffer = []   #danh sách để lưu fps của các frame
fps_avg_len = 60         #biến kiểm tra xem đã đủ 60 frame để tính fps chưa
avg_frame_rate = 0       #fps trung bình

seen_classes = {}        # lưu frame cuối upload của mỗi class
cooldown = 1000          # số frame phải chờ trước khi upload lại cùng class

vn_labels = [
    "Vi khuẩn gây đốm lá",                # 0
    "Bệnh sương mai",                     # 1
    "Virus khảm rau diếp",                # 2
    "Bệnh phấn trắng",                    # 3
    "Bệnh bạc lá nhiễm trùng huyết"       # 4
]

# =======================
# Hàm upload
# =======================
def upload_frame_to_drive(frame):
    """Lưu frame tạm rồi upload lên Google Drive"""
    # Tạo một file tạm thời (.png) trong hệ thống, delete=False nghĩa là
    # sau khi đóng file, nó KHÔNG tự xoá, mình sẽ tự xoá sau khi upload.
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name # Lấy đường dẫn của file tạm
        cv2.imwrite(tmp_path, frame) # Ghi (save) ảnh từ biến `frame` (ảnh từ camera) vào file tạm vừa tạo
    upload_to_drive(tmp_path)  # hàm upload lên gg drive
    os.remove(tmp_path) #xoa đường dẫn tạm

upload_queue = queue.Queue(maxsize=10)  # tối đa 10 ảnh chờ upload

def thread_upload():
    """Thread phụ trách upload ảnh từ queue"""
    while True:
        frame = upload_queue.get()
        try:
            upload_frame_to_drive(frame)
        except Exception as e:
            print("⚠️ Upload error:", e)
        upload_queue.task_done()

# =======================
# Hàm tiện ích
# =======================
def class_name_from_idx(cls_idx):
    """Lấy tên class từ index"""
    # Nếu labels là dictionary (vd: {0: "dog", 1: "cat"})
    # thì lấy tên class từ dict
    if isinstance(labels, dict):
        return str(labels.get(cls_idx, cls_idx))
    try:
        # Nếu labels là list (vd: ["dog", "cat"])
        # thì lấy tên class theo index
        return str(labels[cls_idx])
    except:
        # Nếu không tìm thấy hoặc có lỗi thì trả về số index luôn
        return str(cls_idx)

# =======================
# Thread đọc camera
# =======================
def thread_cam():
    global latest_frame
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        with lock:
            latest_frame = frame.copy() # sao chép vô lastest_frame
        time.sleep(0.01)  # tránh chiếm CPU 100%

# =======================
# Thread YOLO detect
# =======================
def thread_detect():
    global latest_frame, last_boxes, frame_count
    while True:
        if latest_frame is None:
            time.sleep(0.05)
            continue

        frame_count += 1
        if frame_count % process_every == 0:
            with lock:
                frame_copy = latest_frame.copy()

            detected_boxes = []
            for results in model(frame_copy, stream=True):
                for box in results.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    conf = float(box.conf[0])
                    cls  = int(box.cls[0])
                    detected_boxes.append({
                        'box': (x1, y1, x2, y2),
                        'conf': conf,
                        'cls': cls
                    })

            with lock:
                last_boxes = detected_boxes#sao chép kết quả vào last boxes

        time.sleep(0.01)

# =======================
# Flask video generator
# =======================
def generate():
    global latest_frame, last_boxes
    while True:
        if latest_frame is None:
            continue

        with lock:
            frame = latest_frame.copy()
            boxes = list(last_boxes)

        # bắt đầu đo FPS
        t_start = time.perf_counter()
        object_count = 0

        # Vẽ bbox
        for item in boxes:
            x1, y1, x2, y2 = item['box']
            conf = item['conf']
            cls  = item['cls']

            if conf > min_thresh:
                color = bbox_colors[cls % len(bbox_colors)]
                name = class_name_from_idx(cls)
                vn_name = vn_labels[cls] if cls < len(vn_labels) else str(name)

                # vẽ rectangle + label
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                label = f"{vn_name}: {int(conf*100)}%"
                object_count += 1
                cv2.putText(frame, label, (x1, y1-7),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1)

                # kiểm tra upload
                if cls not in seen_classes or frame_count - seen_classes[cls] >= cooldown:
                    seen_classes[cls] = frame_count
                    try:
                        upload_queue.put_nowait(frame.copy())
                        break
                    except queue.Full:
                        print("⚠️ Queue đầy, bỏ qua upload")

        # FPS
        t_stop = time.perf_counter()
        frame_rate = 1.0 / max(t_stop - t_start, 1e-6)
        frame_rate_buffer.append(frame_rate)
        if len(frame_rate_buffer) > fps_avg_len:
            frame_rate_buffer.pop(0)
        avg_frame_rate = sum(frame_rate_buffer) / len(frame_rate_buffer)

        # hiển thị FPS + số object
        cv2.putText(frame, f"FPS: {avg_frame_rate:.2f}", (10, 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Objects: {object_count}", (10, 44),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # encode sang jpg và stream
        _, buffer = cv2.imencode('.jpg', frame)
        jpg = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')

# =======================
# Flask routes
# =======================
@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return "<h2>YOLO Stream (Threaded)</h2><img src='/video_feed'>"

# =======================
# Run server
# =======================
if __name__ == "__main__":
    t1 = threading.Thread(target=thread_cam, daemon=True)
    t2 = threading.Thread(target=thread_detect, daemon=True)
    t3 = threading.Thread(target=thread_upload, daemon=True)

    t1.start()
    t2.start()
    t3.start()

    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        cap.release()
        cv2.destroyAllWindows()
