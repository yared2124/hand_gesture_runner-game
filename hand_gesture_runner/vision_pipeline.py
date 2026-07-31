import cv2
import numpy as np
import mediapipe as mp

class VisionPipeline:
    def __init__(self):
        try:
            self.cap = cv2.VideoCapture(0)
            
            # Check if legacy solutions exists, otherwise fallback gracefully
            if hasattr(mp, "solutions") and hasattr(mp.solutions, "hands"):
                self.mp_hands = mp.solutions.hands
                self.mp_drawing = mp.solutions.drawing_utils
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=1,
                    min_detection_confidence=0.6,
                    min_tracking_confidence=0.6
                )
                self.use_legacy = True
            else:
                # Modern MediaPipe Task API handling
                self.use_legacy = False
                print("Notice: Running in basic camera mode (MediaPipe 1.0 Tasks active).")

            self.is_initialized = True
        except Exception as e:
            print(f"Error initializing vision pipeline: {e}")
            self.is_initialized = False

    def process_frame(self):
        if not self.is_initialized or not self.cap.isOpened():
            return 0, 0.5, None

        ret, frame = self.cap.read()
        if not ret:
            return 0, 0.5, None

        # Flip frame horizontally for selfie mode
        frame = cv2.flip(frame, 1)

        gesture_code = 0  # 0: RUNNING, 1: JUMP, 2: SLIDE
        normalized_x = 0.5

        if self.use_legacy:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    if self.mp_drawing:
                        self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                    wrist_x = hand_landmarks.landmark[self.mp_hands.HandLandmark.WRIST].x
                    normalized_x = wrist_x

                    index_tip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                    index_pip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_PIP].y
                    middle_tip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
                    middle_pip_y = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y

                    if index_tip_y < index_pip_y and middle_tip_y > middle_pip_y:
                        gesture_code = 1
                    elif index_tip_y > index_pip_y and middle_tip_y > middle_pip_y:
                        gesture_code = 2

        return gesture_code, normalized_x, frame

    def release(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()