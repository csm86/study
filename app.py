from flask import Flask, render_template_string, Response
import cv2
from picamera2 import Picamera2

app = Flask(__name__)

# [핵심] 웹 서버가 켜질 때 Picamera2를 한 번만 초기화하여 켜둡니다.
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
print("카메라 센서가 정상적으로 켜졌습니다.")

def generate_frames():
    while True:
        try:
            # cv2.VideoCapture 대신 Picamera2에서 아주 깔끔하게 프레임을 뽑아옵니다.
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # 거울 모드 (좌우 반전)
            frame = cv2.flip(frame, 1)
            
            # --- 이곳에 비전 처리(흑백, Canny, YOLO 등)를 추가할 수 있습니다 ---
            
            # 프레임을 웹 송출용 JPEG 포맷으로 인코딩
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # 웹 브라우저가 인식할 수 있는 데이터 스트림 형태로 변환 (MJPEG)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print("프레임 읽기 에러:", e)
            break

# 심플한 웹 페이지 HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>HandS Vision Seminar Stream</title>
</head>
<body>
    <h1>라즈베리파이 실시간 비전 스트리밍</h1>
    <img src="/video_feed" width="640" height="480">
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # [주의] 하드웨어 카메라를 쓸 때는 Flask의 debug=True를 끄는 것이 안전합니다!
    # (debug=True는 코드가 바뀔 때마다 서버를 재시작하는데, 이때 카메라 모터가 꼬일 수 있음)
    app.run(host='0.0.0.0', port=5000, debug=False)