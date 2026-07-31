import cv2
import numpy as np
import mediapipe as mp

class HandTracker:
    def __init__(self):
        # Check if legacy solutions exists (Python <=3.12)
        if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'hands'):
            self.mp_hands = mp.solutions.hands
            self.mp_drawing = mp.solutions.drawing_utils
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.6,
                min_tracking_confidence=0.6
            )
            self.mode = "legacy"
        else:
            # Python 3.13+ Fallback: Use OpenCV Contour Tracking
            self.mode = "contour"

    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        gesture_code = 0  # 0: RUNNING, 1: JUMP, 2: SLIDE
        normalized_x = 0.5

        if self.mode == "legacy":
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    wrist_x = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST].x
                    normalized_x = wrist_x

                    index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                    index_pip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y
                    
                    if index_tip < index_pip:
                        gesture_code = 1  # JUMP
                    elif index_tip > index_pip:
                        gesture_code = 2  # SLIDE

        elif self.mode == "contour":
            # Direct tracking using hand bounding box on Python 3.13
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_skin = np.array([0, 20, 70], dtype=np.uint8)
            upper_skin = np.array([20, 255, 255], dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_skin, upper_skin)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                largest = max(contours, key=cv2.contourArea)
                if cv2.contourArea(largest) > 2500:
                    x, y, bw, bh = cv2.boundingRect(largest)
                    cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
                    normalized_x = (x + bw / 2) / w

                    if y < h * 0.35:
                        gesture_code = 1  # High position -> JUMP
                    elif y + bh > h * 0.75:
                        gesture_code = 2  # Low position -> SLIDE

        return gesture_code, normalized_x, frame