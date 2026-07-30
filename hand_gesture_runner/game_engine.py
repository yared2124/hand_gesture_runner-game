"""
Game Engine Module (game_engine.py)
Manages player physics, state transitions, obstacle mechanics, scoring, and UI rendering.
Fulfills FR-PM, FR-OB, FR-CD, and FR-SC requirements.
"""

import pygame
import random
import os
import config

class Player:
    def __init__(self):
        self.ground_y = config.SCREEN_HEIGHT - 100
        self.x = config.SCREEN_WIDTH // 2
        self.y = self.ground_y
        self.width = config.PLAYER_NORMAL_WIDTH
        self.height = config.PLAYER_NORMAL_HEIGHT

        self.state = "RUNNING"  # RUNNING, JUMPING, or SLIDING
        self.vy = 0.0
        self.slide_timer = 0.0

    def handle_input(self, gesture_code: int, normalized_x: float):
        # Apply steering
        self.x = int(normalized_x * config.SCREEN_WIDTH)

        # Trigger state transitions
        if gesture_code == 1 and self.state == "RUNNING":
            self.state = "JUMPING"
            self.vy = config.JUMP_SPEED

        elif gesture_code == 2 and self.state == "RUNNING":
            self.state = "SLIDING"
            self.slide_timer = config.SLIDE_DURATION_MS
            self.height = config.PLAYER_SLIDE_HEIGHT
            self.y = self.ground_y + (config.PLAYER_NORMAL_HEIGHT - config.PLAYER_SLIDE_HEIGHT)

    def update(self, dt_ms: float):
        # Physics update loop
        if self.state == "JUMPING":
            self.y += self.vy
            self.vy += config.GRAVITY
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.state = "RUNNING"
                self.vy = 0.0

        elif self.state == "SLIDING":
            self.slide_timer -= dt_ms
            if self.slide_timer <= 0:
                self.state = "RUNNING"
                self.height = config.PLAYER_NORMAL_HEIGHT
                self.y = self.ground_y

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.x - self.width // 2,
            int(self.y - self.height),
            self.width,
            self.height
        )


class Obstacle:
    def __init__(self, obs_type: str, speed: float):
        self.type = obs_type  # "LOW" (must jump over) or "HIGH" (must slide under)
        self.width = random.randint(50, 80)
        self.x = config.SCREEN_WIDTH + self.width

        ground_y = config.SCREEN_HEIGHT - 100
        if self.type == "LOW":
            # Placed on the floor
            self.height = 40
            self.y = ground_y - self.height
            self.color = config.COLOR_OBSTACLE_JUMP
        else:
            # Suspended overhead
            self.height = 50
            self.y = ground_y - config.PLAYER_NORMAL_HEIGHT - 10
            self.color = config.COLOR_OBSTACLE_SLIDE

        self.speed = speed

    def update(self):
        self.x -= self.speed

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)


class GameEngine:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("Hand-Controlled Runner")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 36, bold=True)

        self.high_score = self.load_high_score()
        self.reset()

    def reset(self):
        self.player = Player()
        self.obstacles = []
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0.0
        self.current_speed = config.OBSTACLE_BASE_SPEED

    def load_high_score(self) -> int:
        if os.path.exists(config.SCORE_FILE):
            try:
                with open(config.SCORE_FILE, "r") as f:
                    return int(f.read().strip())
            except ValueError:
                return 0
        return 0

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open(config.SCORE_FILE, "w") as f:
                f.write(str(self.high_score))

    def update(self, gesture_code: int, normalized_x: float, dt_ms: float):
        if self.game_over:
            return

        # Increment Score & Dynamic Difficulty Scaling
        self.score += 1
        self.current_speed = config.OBSTACLE_BASE_SPEED + (self.score // 300)

        # Update Player physics
        self.player.handle_input(gesture_code, normalized_x)
        self.player.update(dt_ms)

        # Spawn Obstacles
        self.spawn_timer += dt_ms
        if self.spawn_timer >= config.OBSTACLE_SPAWN_INTERVAL_MS:
            obs_type = random.choice(["LOW", "HIGH"])
            self.obstacles.append(Obstacle(obs_type, self.current_speed))
            self.spawn_timer = 0.0

        # Update and process obstacles
        player_rect = self.player.get_rect()
        for obs in self.obstacles[:]:
            obs.update()

            # FR-CD-01: AABB Collision Check
            if player_rect.colliderect(obs.get_rect()):
                self.game_over = True
                self.save_high_score()

            # Remove off-screen obstacles
            if obs.x + obs.width < 0:
                self.obstacles.remove(obs)

    def render(self, debug_frame=None):
        self.screen.fill(config.COLOR_BG)

        # Draw Floor Line
        ground_y = config.SCREEN_HEIGHT - 100
        pygame.draw.line(self.screen, (80, 90, 110), (0, ground_y), (config.SCREEN_WIDTH, ground_y), 4)

        # Draw Player
        pygame.draw.rect(self.screen, config.COLOR_PLAYER, self.player.get_rect(), border_radius=6)

        # Draw Obstacles
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, obs.color, obs.get_rect(), border_radius=4)

        # Draw On-Screen HUD (FR-SC-01)
        score_surf = self.font.render(f"Score: {self.score}  |  High Score: {self.high_score}", True, config.COLOR_TEXT)
        self.screen.blit(score_surf, (20, 20))

        state_surf = self.font.render(f"State: {self.player.state}", True, config.COLOR_HUD_ACCENT)
        self.screen.blit(state_surf, (20, 50))

        # Overlay OpenCV Webcam feed in top-right corner (Optional visual feedback)
        if debug_frame is not None:
            # Resize webcam image for debug view window
            debug_resized = cv2.resize(debug_frame, (160, 120))
            # Convert OpenCV BGR format to Pygame RGB
            debug_rgb = cv2.cvtColor(debug_resized, cv2.COLOR_BGR2RGB)
            surf = pygame.surfarray.make_surface(debug_rgb.swapaxes(0, 1))
            self.screen.blit(surf, (config.SCREEN_WIDTH - 180, 20))
            pygame.draw.rect(self.screen, config.COLOR_HUD_ACCENT, (config.SCREEN_WIDTH - 180, 20, 160, 120), 2)

        # Draw Game Over Screen
        if self.game_over:
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            go_surf = self.title_font.render("GAME OVER", True, (255, 60, 60))
            restart_surf = self.font.render("Press SPACE to Restart", True, config.COLOR_TEXT)

            self.screen.blit(go_surf, (config.SCREEN_WIDTH // 2 - go_surf.get_width() // 2, 220))
            self.screen.blit(restart_surf, (config.SCREEN_WIDTH // 2 - restart_surf.get_width() // 2, 280))

        pygame.display.flip()