import sys
import pygame
import config
from hand_tracker import HandTracker
from game_engine import GameEngine

def main():
    # Initialize Hand Tracker & Game Engine
    try:
        tracker = HandTracker()
    except Exception as e:
        print(f"Error initializing vision pipeline: {e}")
        sys.exit(1)

    engine = GameEngine()
    running = True

    while running:
        # Tick at fixed target FPS and compute delta time
        dt_ms = engine.clock.tick(config.FPS_TARGET)

        # Handle system exit and restart events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE and engine.game_over:
                    engine.reset()

        # Step 1: Query Hand Tracker for gestures and coordinates
        gesture_code, normalized_x, debug_frame = tracker.process_frame()

        # Step 2: Step the game physics engine forward
        engine.update(gesture_code, normalized_x, dt_ms)

        # Step 3: Render frame
        engine.render(debug_frame=debug_frame)

    # Cleanup hardware and software contexts on exit
    tracker.release()
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()