import cv2
from picamera2 import Picamera2

def main():
    # 1. 최신 Picamera2 객체 생성 (libcamerify 마법의 주문 필요 없음!)
    picam2 = Picamera2()
    
    # 2. 카메라 해상도 및 포맷 설정 (OpenCV에 딱 맞는 RGB 배열로 알아서 세팅됨)
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    
    # 3. 카메라 시작 (자동 초점 AF도 알아서 작동함!)
    picam2.start()
    print("Webcam started perfectly. Press 'q' to quit.")

    while True:
        # 4. 카메라에서 프레임을 OpenCV용 행렬(Numpy Array)로 바로 뽑아옴!
        # reshape 에러, 포맷 에러, 노이즈 전부 원천 차단.
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # 거울 모드 (좌우 반전)
        frame = cv2.flip(frame, 1)

        # 1. 흑백(Grayscale) 필터 적용
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 2. Canny Edge(윤곽선) 필터 적용
        edges_frame = cv2.Canny(gray_frame, 100, 200)

        # 화면에 띄우기
        cv2.imshow("1. Original Webcam", frame)
        cv2.imshow("2. Grayscale Filter", gray_frame)
        cv2.imshow("3. Canny Edge Filter", edges_frame)

        # 'q' 키를 누르면 탈출
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 종료 시 안전하게 카메라 끄기
    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()