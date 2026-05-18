import cv2
import numpy as np
from picamera2 import Picamera2

def overlay_image_on_marker(frame, corners, overlay_img):
    pts = corners.reshape((4, 2)).astype(np.float32)

    h, w = overlay_img.shape[:2]

    src_pts = np.array([
        [0, 0],
        [w - 1, 0],
        [w - 1, h - 1],
        [0, h - 1]
    ], dtype=np.float32)

    matrix = cv2.getPerspectiveTransform(src_pts, pts)

    warped = cv2.warpPerspective(
        overlay_img,
        matrix,
        (frame.shape[1], frame.shape[0])
    )

    mask = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)
    cv2.fillConvexPoly(mask, pts.astype(np.int32), 255)

    mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    frame = np.where(mask_3ch == 255, warped, frame)

    return frame


def main():
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    kkobugi = cv2.imread("kkobugi.png")
    pikachu = cv2.imread("pikachu.png")

    if kkobugi is None:
        print("kkobugi.png 파일을 찾을 수 없습니다.")
        picam2.stop()
        return

    if pikachu is None:
        print("pikachu.png 파일을 찾을 수 없습니다.")
        picam2.stop()
        return

    # 이미지 반시계 방향 90도 회전
    kkobugi = cv2.rotate(kkobugi, cv2.ROTATE_90_COUNTERCLOCKWISE)
    pikachu = cv2.rotate(pikachu, cv2.ROTATE_90_COUNTERCLOCKWISE)

    print("🪄 마법의 비전 리모컨 시작! (종료: q)")

    try:
        while True:
            frame = picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame = cv2.flip(frame, 1)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            corners, ids, rejected = detector.detectMarkers(gray)

            display_frame = frame.copy()

            if ids is not None:
                for i in range(len(ids)):
                    marker_id = ids[i][0]
                    marker_corners = corners[i][0]

                    if marker_id == 8:
                        display_frame = overlay_image_on_marker(
                            display_frame,
                            marker_corners,
                            kkobugi
                        )

                    elif marker_id == 9:
                        display_frame = overlay_image_on_marker(
                            display_frame,
                            marker_corners,
                            pikachu
                        )

                cv2.aruco.drawDetectedMarkers(display_frame, corners, ids)

            else:
                display_frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                cv2.putText(display_frame, "GRAY MODE (Waiting...)", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (255, 255, 255), 2)

            cv2.imshow("Vision Remote", display_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        picam2.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()