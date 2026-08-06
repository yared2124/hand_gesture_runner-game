"""
Main Controller: Glues the vision module and game engine together.
Includes optional debug window showing camera feed with landmarks.
"""

import sys
import cv2
from config import FPS_TARGET, SHOW_DEBUG_WINDOW
from hand_tracker import HandTracker
from game_engine import GameEngine

def main():
    print("Initialising Hand Gesture Runner...")
    print("Press ESC to quit, R to restart after game over.")

    try:
        tracker = HandTracker()
    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    game = GameEngine()

    # Main loop
    running = True
    while running:
        # --- Fetch latest gesture from camera (including debug frame) ---
        gesture_code, norm_x, detected, debug_frame = tracker.get_gesture_and_position()

        # --- Optional: show debug window with landmarks ---
        if SHOW_DEBUG_WINDOW and debug_frame is not None:
            cv2.imshow("Hand Tracker Debug", debug_frame)
            # Press 'q' in debug window to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False
                break

        # --- Update game with current gesture ---
        dt_ms = game.clock.get_time()  # time since last tick in ms
        game.update(gesture_code, norm_x, dt_ms)

        # --- Render game ---
        game.render()

        # --- Event handling (quit, restart) ---
        running = game.handle_events() and running

        # --- Cap frame rate ---
        game.clock.tick(FPS_TARGET)

    # Cleanup
    tracker.release()
    game.quit()
    cv2.destroyAllWindows()
    sys.exit(0)

if __name__ == "__main__":
    main()