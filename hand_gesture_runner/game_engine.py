"""
Game Engine: Manages Pygame display, player state, obstacles, collisions, and scoring.
"""

import pygame
import random
import os
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS_TARGET,
    GRAVITY, JUMP_SPEED, SLIDE_DURATION,
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_Y_GROUND,
    OBSTACLE_WIDTH, OBSTACLE_HEIGHT, OBSTACLE_SPEED_BASE,
    OBSTACLE_SPAWN_INTERVAL, OBSTACLE_MIN_GAP,
    HIGH_SCORE_FILE
)

class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH // 4
        self.y = PLAYER_Y_GROUND
        self.vel_y = 0
        self.grounded = True
        self.state = "RUNNING"   # RUNNING, JUMPING, SLIDING
        self.slide_timer = 0
        self.normal_height = PLAYER_HEIGHT
        self.slide_height = PLAYER_HEIGHT // 2

    def jump(self):
        if self.grounded:
            self.vel_y = JUMP_SPEED
            self.grounded = False
            self.state = "JUMPING"

    def slide(self):
        if self.grounded:
            self.state = "SLIDING"
            self.slide_timer = SLIDE_DURATION
            self.height = self.slide_height
            self.y = PLAYER_Y_GROUND + (self.normal_height - self.slide_height)

    def update(self, dt_ms):
        # Update slide timer
        if self.state == "SLIDING":
            self.slide_timer -= dt_ms
            if self.slide_timer <= 0:
                self.state = "RUNNING"
                self.height = self.normal_height
                self.y = PLAYER_Y_GROUND

        # Physics for jumping
        if self.state == "JUMPING":
            self.vel_y += GRAVITY
            self.y += self.vel_y
            if self.y >= PLAYER_Y_GROUND:
                self.y = PLAYER_Y_GROUND
                self.vel_y = 0
                self.grounded = True
                self.state = "RUNNING"

        # Keep within vertical bounds (shouldn't go below ground)
        if self.y > PLAYER_Y_GROUND:
            self.y = PLAYER_Y_GROUND

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Obstacle:
    def __init__(self, x, y, width, height, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

    def off_screen(self):
        return self.rect.x + self.rect.width < 0


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Hand Gesture Runner")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.player = Player()
        self.obstacles = []
        self.score = 0
        self.high_score = self._load_high_score()
        self.game_over = False
        self.frame_count = 0

        # For spawning control
        self.last_spawn_x = SCREEN_WIDTH + 100

        # Colours
        self.BG_COLOR = (135, 206, 235)    # Sky blue
        self.GROUND_COLOR = (34, 139, 34)  # Forest green
        self.PLAYER_COLOR = (255, 0, 0)    # Red
        self.OBSTACLE_COLOR = (139, 69, 19) # Saddle brown
        self.TEXT_COLOR = (255, 255, 255)

    def _load_high_score(self):
        if os.path.exists(HIGH_SCORE_FILE):
            with open(HIGH_SCORE_FILE, "r") as f:
                try:
                    return int(f.read().strip())
                except:
                    return 0
        return 0

    def _save_high_score(self):
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write(str(self.high_score))

    def reset(self):
        self.player = Player()
        self.obstacles.clear()
        self.score = 0
        self.game_over = False
        self.frame_count = 0
        self.last_spawn_x = SCREEN_WIDTH + 100

    def update(self, gesture_code, norm_x, dt_ms):
        """
        Update game state based on gesture input.
        gesture_code: 0=idle, 1=jump, 2=slide
        norm_x: 0..1 (left to right)
        dt_ms: time since last frame in milliseconds
        """
        if self.game_over:
            return

        # --- Player Steering ---
        # Map norm_x to screen position with boundary padding
        padding = 20
        self.player.x = padding + (norm_x * (SCREEN_WIDTH - 2 * padding - self.player.width))
        # Clamp to screen
        self.player.x = max(0, min(self.player.x, SCREEN_WIDTH - self.player.width))

        # --- Gesture Actions ---
        if gesture_code == 1:   # Jump
            self.player.jump()
        elif gesture_code == 2: # Slide
            self.player.slide()

        # --- Update player physics ---
        self.player.update(dt_ms)

        # --- Spawn Obstacles ---
        self.frame_count += 1
        if self.frame_count % OBSTACLE_SPAWN_INTERVAL == 0:
            # Random Y position (ground level)
            y_pos = PLAYER_Y_GROUND + (PLAYER_HEIGHT - OBSTACLE_HEIGHT)
            # Ensure minimum gap from last obstacle
            if (not self.obstacles) or (SCREEN_WIDTH - self.obstacles[-1].rect.x > OBSTACLE_MIN_GAP):
                speed = OBSTACLE_SPEED_BASE + (self.score // 200) * 0.5
                obs = Obstacle(SCREEN_WIDTH, y_pos, OBSTACLE_WIDTH, OBSTACLE_HEIGHT, speed)
                self.obstacles.append(obs)

        # --- Update obstacles ---
        for obs in self.obstacles[:]:
            obs.update()
            if obs.off_screen():
                self.obstacles.remove(obs)
                self.score += 1
                if self.score > self.high_score:
                    self.high_score = self.score
                    self._save_high_score()

        # --- Collision Detection (AABB) ---
        player_rect = self.player.get_rect()
        for obs in self.obstacles:
            if player_rect.colliderect(obs.rect):
                self.game_over = True
                break

    def render(self):
        """Draw everything to the screen."""
        self.screen.fill(self.BG_COLOR)

        # Draw ground
        ground_y = PLAYER_Y_GROUND + PLAYER_HEIGHT
        pygame.draw.rect(self.screen, self.GROUND_COLOR,
                         (0, ground_y, SCREEN_WIDTH, SCREEN_HEIGHT - ground_y))

        # Draw player
        player_rect = self.player.get_rect()
        pygame.draw.rect(self.screen, self.PLAYER_COLOR, player_rect)

        # Draw obstacles
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, self.OBSTACLE_COLOR, obs.rect)

        # Draw HUD
        score_text = self.font.render(f"Score: {self.score}", True, self.TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))

        high_text = self.font.render(f"High: {self.high_score}", True, self.TEXT_COLOR)
        self.screen.blit(high_text, (10, 50))

        state_text = self.small_font.render(f"State: {self.player.state}", True, (0,0,0))
        self.screen.blit(state_text, (10, 90))

        # Gesture hint
        hint = self.small_font.render("Open palm = Jump | Fist = Slide", True, (0,0,0))
        self.screen.blit(hint, (SCREEN_WIDTH - 250, 10))

        # Game Over overlay
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            go_text = self.font.render("GAME OVER", True, (255, 255, 255))
            go_rect = go_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(go_text, go_rect)
            restart_text = self.small_font.render("Press R to restart or ESC to quit", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def handle_events(self):
        """Process Pygame events (keyboard for testing & restart)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
                    return True
        return True

    def quit(self):
        pygame.quit()