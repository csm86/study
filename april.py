import cv2
from picamera2 import Picamera2

def main():
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    # [핵심 1] ArUco 탐지기를 쓰되, '사전'만 AprilTag(tag36h11)로 바꿔치기합니다!
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h10)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    print("OpenCV 내장 AprilTag Scanner Started. 마커를 보여주세요!")

    try:
        while True:
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame = cv2.flip(frame, 1)

            # [핵심 2] 흑백 변환 (인식률 향상의 핵심)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # [핵심 3] 마커 찾기 (ArUco와 동일한 함수 사용)
            corners, ids, rejected = detector.detectMarkers(gray)

            # 화면에 마커가 보인다면 초록색 테두리 치기
            if ids is not None:
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                
                # 마커 ID 번호 텍스트 띄우기 (선택 사항)
                for i, corner in enumerate(corners):
                    # 마커의 왼쪽 위(Top-Left) 좌표 구하기
                    tl = corner[0][0]
                    x, y = int(tl[0]), int(tl[1])
                    cv2.putText(frame, f"AprilTag ID: {ids[i][0]}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # [주의] 모니터 연결 에러(qt.qpa.xcb)가 났다면, 이 코드를 app.py(Flask)에 합치셔야 합니다!
            cv2.imshow("AprilTag Scanner", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()