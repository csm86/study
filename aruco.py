import cv2
from picamera2 import Picamera2

def main():
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    # [핵심 1] 탐지기 세팅 (Step 1에서 만든 것과 똑같은 4x4 사전 사용)
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    print("ArUco Scanner Started. 마커를 카메라에 보여주세요!")

    try:
        while True:
            # 프레임 가져오기 및 욘두 방지
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame = cv2.flip(frame, 1)

            # [핵심 2] 흑백 변환 (데이터 다이어트!)
            # 컬러보다 흑백 화면에서 마커의 명암 대비가 뚜렷해져 인식률이 훨씬 올라갑니다.
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # [핵심 3] 마커 찾기
            # corners: 마커의 네 모서리 좌표 / ids: 마커의 고유 번호(예: 7)
            corners, ids, rejected = detector.detectMarkers(gray)

            # 화면에 마커가 1개라도 보인다면? 테두리와 ID를 그려라!
            if ids is not None:
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                
                # (보너스) 인식된 ID 콘솔창에 출력하기
                # print(f"인식된 마커 ID: {ids.flatten()}")

            cv2.imshow("ArUco Scanner", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()