import cv2
import mediapipe as mp
import pyautogui
import time

pyautogui.FAILSAFE = False

screen_w, screen_h = pyautogui.size()

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

last_action = time.time()
ACTION_DELAY = 0.7

mouse_enabled = True
pause_cooldown = 0
exit_start_time = None

while True:

    success, frame = cap.read()

    if not success:
        break

    frame = cv2.flip(frame, 1)

    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    if result.multi_hand_landmarks:

        for hand_landmarks in result.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            landmarks = hand_landmarks.landmark

            # ujung jari
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            ring_tip = landmarks[16]
            pinky_tip = landmarks[20]

            # status jari
            thumb_up = landmarks[4].x < landmarks[3].x
            index_up = landmarks[8].y < landmarks[6].y
            middle_up = landmarks[12].y < landmarks[10].y
            ring_up = landmarks[16].y < landmarks[14].y
            pinky_up = landmarks[20].y < landmarks[18].y

            # posisi telunjuk
            ix = int(index_tip.x * w)
            iy = int(index_tip.y * h)

            # EXIT
            all_open = (
                thumb_up and
                index_up and
                middle_up and
                ring_up and
                pinky_up
            )
            current_time = time.time()

            if all_open:

                if exit_start_time is None:
                    exit_start_time = current_time

                countdown = max(
                    0,
                    3 - int(current_time - exit_start_time)
                )
                cv2.putText(
                    frame,
                    f"EXIT {countdown}",
                    (50, 420),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

                if current_time - exit_start_time >= 3:
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

            else:
                exit_start_time = None

            # PAUSE
            all_folded = (
                not thumb_up and
                not index_up and
                not middle_up and
                not ring_up and
                not pinky_up
            )

            if (
                all_folded and
                current_time - pause_cooldown > 1
            ):
                mouse_enabled = not mouse_enabled
                pause_cooldown = current_time

            if not mouse_enabled:

                cv2.putText(
                    frame,
                    "PAUSED",
                    (50, 370),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )

                continue

            # GERAK CURSOR
            if (
                index_up and
                not middle_up and
                not ring_up and
                not pinky_up
            ):

                screen_x = screen_w * index_tip.x
                screen_y = screen_h * index_tip.y

                pyautogui.moveTo(
                    screen_x,
                    screen_y,
                    duration=0.01
                )

                cv2.putText(
                    frame,
                    "MOVE",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

            # KLIK KIRI
            elif (
                thumb_up and
                not index_up and
                not middle_up and
                not ring_up and
                not pinky_up and
                current_time - last_action > ACTION_DELAY
            ):

                pyautogui.click()
                last_action = current_time

                cv2.putText(
                    frame,
                    "LEFT CLICK",
                    (50, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

            # KLIK KANAN
            elif (
                pinky_up and
                not thumb_up and
                not index_up and
                not middle_up and
                not ring_up and
                current_time - last_action > ACTION_DELAY
            ):

                pyautogui.rightClick()
                last_action = current_time

                cv2.putText(
                    frame,
                    "RIGHT CLICK",
                    (50, 130),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 0, 0),
                    2
                )

            # ZOOM IN
            elif (
                thumb_up and
                pinky_up and
                iy < h // 2 and
                current_time - last_action > ACTION_DELAY
            ):

                pyautogui.keyDown('ctrl')
                pyautogui.press('=')
                pyautogui.keyUp('ctrl')

                last_action = current_time

                cv2.putText(
                    frame,
                    "ZOOM IN",
                    (50, 170),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 0, 255),
                    2
                )

            # ZOOM OUT
            elif (
                thumb_up and
                pinky_up and
                iy > h // 2 and
                current_time - last_action > ACTION_DELAY
            ):

                pyautogui.keyDown('ctrl')
                pyautogui.press('-')
                pyautogui.keyUp('ctrl')

                last_action = current_time

                cv2.putText(
                    frame,
                    "ZOOM OUT",
                    (50, 210),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 0, 255),
                    2
                )

            # SCROLL UP
            elif (
                index_up and
                middle_up and
                not ring_up and
                not pinky_up and
                current_time - last_action > 0.3
            ):

                pyautogui.scroll(100)

                last_action = current_time

                cv2.putText(
                    frame,
                    "SCROLL UP",
                    (50, 250),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                     (255, 255, 0),
                    2
                )

            # SCROLL DOWN
            elif (
                middle_up and
                ring_up and
                not index_up and
                not pinky_up and
                current_time - last_action > 0.3
            ):

                pyautogui.scroll(-100)

                last_action = current_time

                cv2.putText(
                    frame,
                    "SCROLL DOWN",
                    (50, 290),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 0),
                    2
                )

    cv2.imshow("Virtual Mouse", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()