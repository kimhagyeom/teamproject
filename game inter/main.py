import cv2 as cv
import numpy as np
import mediapipe as mp
import random
import time

LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

LEFT_IRIS = [474, 475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]

capture = cv.VideoCapture(0)

mp_face_mesh = mp.solutions.face_mesh

with mp_face_mesh.FaceMesh(max_num_faces=1,
                           refine_landmarks=True,
                           min_detection_confidence=0.5,
                           min_tracking_confidence=0.5
                           ) as face_mesh:
    while True:
        if capture.get(cv.CAP_PROP_POS_FRAMES) == capture.get(cv.CAP_PROP_FRAME_COUNT):
            capture.set(cv.CAP_PROP_POS_FRAMES, 0)
        ret, frame = capture.read()
        if not ret:
            break
        img_h, img_w = frame.shape[:2]
        results = face_mesh.process(frame)
        if results.multi_face_landmarks:
            mesh_points = np.array([np.multiply([p.x, p.y], [img_w, img_h]).astype(int)
                                    for p in results.multi_face_landmarks[0].landmark])
            for pt in mesh_points:
                cv.circle(frame, pt, 1, (255, 255, 255), -1, cv.LINE_AA)
            cv.polylines(frame, [mesh_points[LEFT_EYE]], True, (0, 0, 255), 2, cv.LINE_AA)
            cv.polylines(frame, [mesh_points[RIGHT_EYE]], True, (0, 0, 255), 2, cv.LINE_AA)
            # 눈동자
            cv.polylines(frame, [mesh_points[LEFT_IRIS]], True, (0, 255, 0), 2, cv.LINE_AA)
            cv.polylines(frame, [mesh_points[RIGHT_IRIS]], True, (0, 255, 0), 2, cv.LINE_AA)

            (l_cx, l_cy), l_rad = cv.minEnclosingCircle(mesh_points[LEFT_IRIS])
            (r_cx, r_cy), r_rad = cv.minEnclosingCircle(mesh_points[RIGHT_IRIS])
            l_center = np.array([l_cx, l_cy], dtype=np.int32)
            r_center = np.array([r_cx, r_cy], dtype=np.int32)
            cv.circle(frame, l_center, int(l_rad), (0, 255, 0), 2, cv.LINE_AA)
            cv.circle(frame, r_center, int(r_rad), (0, 255, 0), 2, cv.LINE_AA)

        img_bg = cv.imread('bg.jpg')
        img_tool = cv.imread('tool_small.png', cv.IMREAD_UNCHANGED)

        _, mask = cv.threshold(img_tool[:, :, 3], 1, 255, cv.THRESH_BINARY)
        mask_inverse = cv.bitwise_not(mask)

        coords_dict = {(10, 10): 'coord_1', (700, 700): 'coord_2', (1400, 700): 'coord_3',
                       (1400, 10): 'coord_4', (1400, 350): 'coord_5', (10, 350): 'coord_6',
                       (700, 10): 'coord_7', (10, 700): 'coord_8'}

        # 랜덤한 좌표 선택
        rand_key = random.choice(list(coords_dict.keys()))
        rand_coords = coords_dict[rand_key]

        # 좌표 추출
        x, y = rand_key

        img_tool = cv.cvtColor(img_tool, cv.COLOR_BGRA2BGR)
        height, width = img_tool.shape[:2]
        roi = img_bg[x:x + height, y:y + width]

        masked_bg = cv.bitwise_and(roi, roi, mask=mask_inverse)
        masked_tool = cv.bitwise_and(img_tool, img_tool, mask=mask)

        added = masked_tool + masked_bg
        img_bg[y:y + height, x:x + width] = added
        time.sleep(1)

        cv.imshow('result', img_bg)
        # cv.imshow('main', frame)

        key = cv.waitKey(1)
        if key == ord('q'):
            break

capture.release()
cv.destroyAllWindows()