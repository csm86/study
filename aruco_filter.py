import cv2
from picamera2 import Picamera2

def main():
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    # 4x4 사전 세팅
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    print("🪄 마법의 비전 리모컨 시작! (종료: q)")

    try:
        while True:
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame = cv2.flip(frame, 1)

            # 마커 인식을 위해 흑백 변환
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # 마커 찾기
            corners, ids, rejected = detector.detectMarkers(gray)

            # [✨ 핵심 수정 포인트] 
            # 매 프레임마다 일단 기본 모드를 'gray'로 리셋합니다!
            # 마커가 화면에서 사라지면 조건문에 걸리지 않으므로 자연스럽게 흑백이 유지됩니다.
            current_mode = 'gray'

            # 마커가 화면에 보일 때만 덮어쓰기!
            if ids is not None:
                # 인식된 마커에 테두리 그리기
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                
                # 어떤 마커가 들어왔는지 확인
                for i in range(len(ids)):
                    marker_id = ids[i][0]
                    if marker_id == 8:
                        current_mode = 'color' # 8번이 보이면 컬러로 덮어쓰기
                    elif marker_id == 9:
                        current_mode = 'edge'  # 9번이 보이면 윤곽선으로 덮어쓰기

            # current_mode 상태에 따라 최종 화면(display_frame) 결정
            if current_mode == 'color':
                display_frame = frame.copy()
                cv2.putText(display_frame, "COLOR MODE ON", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
            elif current_mode == 'edge':
                display_frame = cv2.Canny(gray, 100, 200)
                # 글씨(컬러)를 쓰기 위해 1채널 엣지를 3채널 껍데기로 뻥튀기
                display_frame = cv2.cvtColor(display_frame, cv2.COLOR_GRAY2BGR)
                cv2.putText(display_frame, "EDGE MODE ON", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
            else: # 기본값 'gray'
                display_frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                cv2.putText(display_frame, "GRAY MODE (Waiting...)", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow("Vision Remote", display_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()