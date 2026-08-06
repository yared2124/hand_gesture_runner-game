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

        # Extra safety: if for any reason the player is below ground, bring them up
        if self.y > PLAYER_Y_GROUND:
            self.y = PLAYER_Y_GROUND
            if self.state == "JUMPING":
                self.vel_y = 0
                self.grounded = True
                self.state = "RUNNING"

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
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
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
        self.last_spawn_x = SCREEN_WIDTH + 100

        # Colours
        self.BG_COLOR = (135, 206, 235)
        self.GROUND_COLOR = (34, 139, 34)
        self.OBSTACLE_COLOR = (139, 69, 19)
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

    def draw_player(self):
        """Draw the player as a cute 'small man toy' with arms and hands."""
        x, y = self.player.x, self.player.y
        w, h = self.player.width, self.player.height

        # Colors
        body_color = (0, 150, 255)
        skin_color = (255, 200, 150)
        pants_color = (50, 50, 200)
        shoe_color = (200, 50, 50)
        eye_color = (0, 0, 0)
        mouth_color = (50, 50, 50)

        # --- Head ---
        head_radius = int(w * 0.4)
        head_x = x + w // 2
        head_y = y + int(h * 0.25)
        pygame.draw.circle(self.screen, skin_color, (head_x, head_y), head_radius)

        # --- Body ---
        body_rect = pygame.Rect(
            x + int(w * 0.15),
            y + int(h * 0.4),
            int(w * 0.7),
            int(h * 0.35)
        )
        pygame.draw.rect(self.screen, body_color, body_rect)

        # --- Arms ---
        arm_width = int(w * 0.1)
        arm_height = int(h * 0.3)
        left_arm_rect = pygame.Rect(
            x + int(w * 0.05),
            y + int(h * 0.4),
            arm_width,
            arm_height
        )
        pygame.draw.rect(self.screen, skin_color, left_arm_rect)
        right_arm_rect = pygame.Rect(
            x + int(w * 0.85),
            y + int(h * 0.4),
            arm_width,
            arm_height
        )
        pygame.draw.rect(self.screen, skin_color, right_arm_rect)

        # --- Hands ---
        hand_radius = int(w * 0.08)
        pygame.draw.circle(
            self.screen,
            skin_color,
            (x + int(w * 0.1), y + int(h * 0.65)),
            hand_radius
        )
        pygame.draw.circle(
            self.screen,
            skin_color,
            (x + int(w * 0.9), y + int(h * 0.65)),
            hand_radius
        )

        # --- Legs ---
        leg_width = int(w * 0.2)
        leg_height = int(h * 0.25)
        pygame.draw.rect(
            self.screen,
            pants_color,
            (x + int(w * 0.2), y + int(h * 0.75), leg_width, leg_height)
        )
        pygame.draw.rect(
            self.screen,
            pants_color,
            (x + int(w * 0.6), y + int(h * 0.75), leg_width, leg_height)
        )

        # --- Shoes ---
        shoe_width = int(w * 0.3)
        shoe_height = int(h * 0.1)
        pygame.draw.rect(
            self.screen,
            shoe_color,
            (x + int(w * 0.15), y + int(h * 0.95), shoe_width, shoe_height)
        )
        pygame.draw.rect(
            self.screen,
            shoe_color,
            (x + int(w * 0.55), y + int(h * 0.95), shoe_width, shoe_height)
        )

        # --- Eyes ---
        eye_y_offset = int(head_radius * 0.1)
        eye_size = int(head_radius * 0.15)
        pygame.draw.circle(
            self.screen,
            eye_color,
            (head_x - int(head_radius * 0.3), head_y - eye_y_offset),
            eye_size
        )
        pygame.draw.circle(
            self.screen,
            eye_color,
            (head_x + int(head_radius * 0.3), head_y - eye_y_offset),
            eye_size
        )

        # --- Mouth ---
        mouth_y = head_y + int(head_radius * 0.3)
        start_pos = (head_x - int(head_radius * 0.2), mouth_y)
        end_pos = (head_x + int(head_radius * 0.2), mouth_y)
        pygame.draw.line(self.screen, mouth_color, start_pos, end_pos, 2)

    def update(self, gesture_code, norm_x, dt_ms):
        if self.game_over:
            return

        padding = 20
        self.player.x = padding + (norm_x * (SCREEN_WIDTH - 2 * padding - self.player.width))
        self.player.x = max(0, min(self.player.x, SCREEN_WIDTH - self.player.width))

        if gesture_code == 1:
            self.player.jump()
        elif gesture_code == 2:
            self.player.slide()

        self.player.update(dt_ms)

        self.frame_count += 1
        if self.frame_count % OBSTACLE_SPAWN_INTERVAL == 0:
            y_pos = PLAYER_Y_GROUND + (PLAYER_HEIGHT - OBSTACLE_HEIGHT)
            if (not self.obstacles) or (SCREEN_WIDTH - self.obstacles[-1].rect.x > OBSTACLE_MIN_GAP):
                speed = OBSTACLE_SPEED_BASE + (self.score // 200) * 0.5
                obs = Obstacle(SCREEN_WIDTH, y_pos, OBSTACLE_WIDTH, OBSTACLE_HEIGHT, speed)
                self.obstacles.append(obs)

        for obs in self.obstacles[:]:
            obs.update()
            if obs.off_screen():
                self.obstacles.remove(obs)
                self.score += 1
                if self.score > self.high_score:
                    self.high_score = self.score
                    self._save_high_score()

        player_rect = self.player.get_rect()
        for obs in self.obstacles:
            if player_rect.colliderect(obs.rect):
                self.game_over = True
                break

    def render(self):
        self.screen.fill(self.BG_COLOR)
        ground_y = PLAYER_Y_GROUND + PLAYER_HEIGHT
        pygame.draw.rect(self.screen, self.GROUND_COLOR,
                         (0, ground_y, SCREEN_WIDTH, SCREEN_HEIGHT - ground_y))

        self.draw_player()

        for obs in self.obstacles:
            pygame.draw.rect(self.screen, self.OBSTACLE_COLOR, obs.rect)

        score_text = self.font.render(f"Score: {self.score}", True, self.TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))

        high_text = self.font.render(f"High: {self.high_score}", True, self.TEXT_COLOR)
        self.screen.blit(high_text, (10, 50))

        state_text = self.small_font.render(f"State: {self.player.state}", True, (0, 0, 0))
        self.screen.blit(state_text, (10, 90))

        hint = self.small_font.render("Open palm = Jump | Fist = Slide", True, (0, 0, 0))
        self.screen.blit(hint, (SCREEN_WIDTH - 250, 10))

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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.VIDEORESIZE:
                pass
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
                    return True
        return True

    def quit(self):
        pygame.quit()