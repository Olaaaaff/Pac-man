import pygame
import math
from settings import *  # Import all settings (colors, sizes, map)
from player import Player
from ghost import Ghost


class Game:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.font.init()

        # Window Setup
        self.window_width = int(SCREEN_WIDTH * 1.0)
        self.window_height = int(SCREEN_HEIGHT * 1.0)
        self.display_surface = pygame.display.set_mode(
            (self.window_width, self.window_height), pygame.RESIZABLE)
        pygame.display.set_caption("Pygame Pac-Man (F11: Fullscreen)")

        # Game Content Surface (for map and game elements)
        self.game_content_height = MAP_HEIGHT
        self.game_content_surface = pygame.Surface(
            (SCREEN_WIDTH, self.game_content_height))

        # Clock
        self.clock = pygame.time.Clock()
        self.running = True
        self.is_fullscreen = False

        # Logs System
        self.game_logs = []
        self.MAX_LOGS = 6

        # Game State Variables
        self.game_state = GAME_STATE_MENU
        self.player_lives = MAX_LIVES
        self.current_level = 1
        self.selected_algorithm = ALGO_ASTAR
        self.high_score = high_score  # From settings.py

        # Entities
        self.player = None
        self.ghosts = []

        # Level Specifics
        self.game_map = []  # Will hold the mutable map
        self.total_pellets = 0
        self.starting_pellets = 0
        self.frightened_mode = False
        self.frightened_start_time = 0
        self.level_frightened_duration = FRIGHTENED_DURATION

        # Ghost Modes
        self.global_ghost_mode = MODE_SCATTER
        self.last_mode_switch_time = 0

        # Animation
        self.ready_animation_start_time = 0

        # Bonus Fruit
        self.fruit_active = False
        self.fruit_spawn_time = 0
        self.fruit_score = 100
        self.fruit_pos = (14, 29)
        self.fruits_spawned = 0
        self.initial_log_shown = False

        # Pre-calculated Paths (Scatter targets)
        self.path_blinky = [(26, 1), (26, 5), (21, 5), (21, 1)]
        self.path_pinky = [(1, 1), (1, 5), (6, 5), (6, 1)]
        self.path_inky = [(26, 29), (26, 26), (21, 26), (21, 29)]
        self.path_clyde = [(1, 29), (1, 26), (6, 26), (6, 29)]

        # Background Cache
        self.background_surface = None

        # Menu Buttons storage
        self.menu_buttons = []

        # Initial Setup
        self.generate_background()
        self.log_message(f"Game Loaded! Press ARROW KEYS to start...", GREEN)

    def log_message(self, message, color=WHITE):
        """ Add a message to the in-game log """
        ticks = pygame.time.get_ticks() // 1000
        formatted_msg = f"[{ticks}s] {message}"
        print(formatted_msg)
        self.game_logs.append((formatted_msg, color))
        if len(self.game_logs) > self.MAX_LOGS:
            self.game_logs.pop(0)

    def generate_background(self):
        """ Generate static wall background with connected lines """
        self.background_surface = pygame.Surface((SCREEN_WIDTH, MAP_HEIGHT))
        self.background_surface.fill(BLACK)

        # Wall color and thickness
        wall_color = BLUE
        line_width = 4

        # Helper to check if a tile is a wall
        rows = len(MAP_STRINGS)
        cols = len(MAP_STRINGS[0])

        def is_wall_tile(x, y):
            if 0 <= y < rows and 0 <= x < cols:
                return MAP_STRINGS[y][x] == TILE_WALL
            return False

        for y, row in enumerate(MAP_STRINGS):
            for x, char in enumerate(row):
                if char == TILE_WALL:
                    # Center of the current tile
                    cx = x * TILE_SIZE + TILE_SIZE // 2
                    cy = y * TILE_SIZE + TILE_SIZE // 2

                    # Draw a small joint circle at center to smooth connections
                    pygame.draw.circle(self.background_surface,
                                       wall_color, (cx, cy), line_width // 2)

                    # Check neighbors and draw connections
                    # UP
                    if is_wall_tile(x, y - 1):
                        pygame.draw.line(
                            self.background_surface, wall_color, (cx, cy), (cx, cy - TILE_SIZE//2), line_width)
                    # DOWN
                    if is_wall_tile(x, y + 1):
                        pygame.draw.line(
                            self.background_surface, wall_color, (cx, cy), (cx, cy + TILE_SIZE//2), line_width)
                    # LEFT
                    if is_wall_tile(x - 1, y):
                        pygame.draw.line(
                            self.background_surface, wall_color, (cx, cy), (cx - TILE_SIZE//2, cy), line_width)
                    # RIGHT
                    if is_wall_tile(x + 1, y):
                        pygame.draw.line(
                            self.background_surface, wall_color, (cx, cy), (cx + TILE_SIZE//2, cy), line_width)

                elif char == TILE_DOOR:
                    rect_x = x * TILE_SIZE
                    rect_y = y * TILE_SIZE
                    pygame.draw.line(self.background_surface, PINK, (rect_x, rect_y + TILE_SIZE//2),
                                     (rect_x + TILE_SIZE, rect_y + TILE_SIZE//2), 2)

    def init_level(self, new_level=False):
        """ Reset game state for a level or restart """
        # Reset Map
        if new_level:
            # Deep copy from settings.MAP_STRINGS
            self.game_map = [list(row) for row in MAP_STRINGS]
            self.generate_background()
            self.log_message(
                f"--- Level {self.current_level} Started ---", YELLOW)

        # Difficulty
        speed_bonus = (self.current_level - 1) * 0.1
        level_speed = min(SPEED + speed_bonus, 5.0)

        duration_reduction = (self.current_level - 1) * 500
        self.level_frightened_duration = max(
            FRIGHTENED_DURATION - duration_reduction, 2000)

        if new_level:
            self.log_message(
                f"Difficulty Up! Speed: {level_speed:.1f}, Fright: {self.level_frightened_duration/1000}s", CYAN)
            self.total_pellets = sum(row.count(TILE_PELLET)
                                     for row in self.game_map)
            self.starting_pellets = self.total_pellets
            self.fruits_spawned = 0
            self.fruit_active = False
            self.initial_log_shown = False
            self.log_message(f"Total pellets: {self.total_pellets}", WHITE)

        old_score = 0
        old_lives = MAX_LIVES

        if self.player:
            old_score = self.player.score
            old_lives = self.player.lives

        self.player = Player(14, 23, speed=level_speed)
        self.player.score = old_score
        self.player.lives = old_lives

        # Reset Ghosts
        blinky = Ghost(13, 14, RED, ai_mode=AI_CHASE_BLINKY,
                       scatter_point=self.path_blinky, in_house=True, delay=0,
                       on_log=self.log_message, algorithm=self.selected_algorithm, speed=level_speed)
        pinky = Ghost(14, 14, PINK, ai_mode=AI_CHASE_PINKY,
                      scatter_point=self.path_pinky, in_house=True, delay=3000,
                      on_log=self.log_message, algorithm=self.selected_algorithm, speed=level_speed)
        inky = Ghost(12, 14, CYAN, ai_mode=AI_CHASE_INKY, scatter_point=self.path_inky,
                     in_house=True, delay=6000,
                     on_log=self.log_message, algorithm=self.selected_algorithm, speed=level_speed)
        clyde = Ghost(15, 14, ORANGE, ai_mode=AI_CHASE_CLYDE,
                      scatter_point=self.path_clyde, in_house=True, delay=9000,
                      on_log=self.log_message, algorithm=self.selected_algorithm, speed=level_speed)

        self.ghosts = [blinky, pinky, inky, clyde]

        # Reset modes
        self.frightened_mode = False
        self.global_ghost_mode = MODE_SCATTER
        self.last_mode_switch_time = pygame.time.get_ticks()

    def reset_game(self):
        self.player_lives = MAX_LIVES
        self.current_level = 1
        self.game_state = GAME_STATE_MENU
        self.player = None
        self.log_message("Game Reset to Menu", YELLOW)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    self.is_fullscreen = not self.is_fullscreen
                    if self.is_fullscreen:
                        self.display_surface = pygame.display.set_mode(
                            (0, 0), pygame.FULLSCREEN)
                    else:
                        self.display_surface = pygame.display.set_mode(
                            (self.window_width, self.window_height), pygame.RESIZABLE)

            # --- State Specific Input ---
            if self.game_state == GAME_STATE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        # Calculate scaling to match UI coordinates
                        display_w, display_h = self.display_surface.get_size()
                        scale = min(display_w / SCREEN_WIDTH,
                                    display_h / self.game_content_height)
                        new_w = int(SCREEN_WIDTH * scale)
                        new_h = int(self.game_content_height * scale)
                        offset_x = (display_w - new_w) // 2
                        offset_y = (display_h - new_h) // 2

                        if self.menu_buttons:
                            game_x = (mx - offset_x) / scale
                            game_y = (my - offset_y) / scale

                            for rect, algo in self.menu_buttons:
                                if rect.collidepoint(game_x, game_y):
                                    self.selected_algorithm = algo
                                    self.game_state = GAME_STATE_START
                                    self.init_level(new_level=True)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.selected_algorithm = ALGO_GREEDY
                        self.game_state = GAME_STATE_START
                        self.init_level(new_level=True)
                    elif event.key == pygame.K_2:
                        self.selected_algorithm = ALGO_BFS
                        self.game_state = GAME_STATE_START
                        self.init_level(new_level=True)
                    elif event.key == pygame.K_3:
                        self.selected_algorithm = ALGO_ASTAR
                        self.game_state = GAME_STATE_START
                        self.init_level(new_level=True)

            elif self.game_state == GAME_STATE_START:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        self.game_state = GAME_STATE_READY
                        self.ready_animation_start_time = pygame.time.get_ticks()
                        if self.player:
                            self.player.handle_input(event)

            elif self.game_state == GAME_STATE_PAUSED:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.game_state = GAME_STATE_PLAYING
                        self.log_message("Game Resumed", GREEN)
                    elif event.key == pygame.K_q:
                        self.game_state = GAME_STATE_MENU
                        self.reset_game()
                    elif event.key == pygame.K_r:
                        self.reset_game()

            elif self.game_state == GAME_STATE_PLAYING:
                if self.player:
                    self.player.handle_input(event)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                        self.game_state = GAME_STATE_PAUSED
                        self.log_message("Game Paused", YELLOW)

            elif self.game_state in [GAME_STATE_GAME_OVER, GAME_STATE_WIN]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        # Death Animation
        if self.game_state == GAME_STATE_DEATH:
            anim_done = self.player.update_death_anim()
            if anim_done:
                self.player.lives -= 1
                if self.player.lives > 0:
                    self.log_message(
                        f"Lives: {self.player.lives}, Resetting...", YELLOW)
                    self.init_level(new_level=False)
                    self.game_state = GAME_STATE_READY
                    self.ready_animation_start_time = pygame.time.get_ticks()
                else:
                    self.game_state = GAME_STATE_GAME_OVER
                    self.log_message("Game Over.", RED)
                    save_high_score(self.high_score)

        elif self.game_state == GAME_STATE_PLAYING:
            if not self.frightened_mode:
                time_passed = current_time - self.last_mode_switch_time

                # Check initial log
                if not self.initial_log_shown and time_passed > 100:
                    self.log_message(
                        f">> Init Mode: {self.global_ghost_mode}", YELLOW)
                    self.initial_log_shown = True

                # Mode Switching
                if self.global_ghost_mode == MODE_SCATTER and time_passed > SCATTER_DURATION:
                    self.global_ghost_mode = MODE_CHASE
                    self.last_mode_switch_time = current_time
                    self.log_message(">> Mode Switch: CHASE", RED)
                elif self.global_ghost_mode == MODE_CHASE and time_passed > CHASE_DURATION:
                    self.global_ghost_mode = MODE_SCATTER
                    self.last_mode_switch_time = current_time
                    self.log_message(">> Mode Switch: SCATTER", GREEN)

            # Update Ghosts
            blinky_pos_for_inky = (
                self.ghosts[0].grid_x, self.ghosts[0].grid_y)
            for ghost in self.ghosts:
                if (not ghost.is_frightened and not ghost.is_eaten and
                        ghost.current_ai_mode not in [MODE_GO_HOME, MODE_EXIT_HOUSE, MODE_WAITING]):
                    if self.global_ghost_mode == MODE_SCATTER:
                        ghost.current_ai_mode = MODE_SCATTER
                    elif self.global_ghost_mode == MODE_CHASE:
                        ghost.current_ai_mode = ghost.ai_mode

                ghost.update(self.game_map, self.player, dt,
                             self.global_ghost_mode, blinky_pos_for_inky)

            # Update Frightened Timer
            if self.frightened_mode:
                if current_time - self.frightened_start_time > self.level_frightened_duration:
                    self.frightened_mode = False
                    self.log_message(
                        "Frightened mode ended. Ghosts normal.", WHITE)
                    for ghost in self.ghosts:
                        ghost.end_frightened()
                    self.last_mode_switch_time = current_time

            # Update Player
            player_event = self.player.update(self.game_map, dt)

            # Logic for Player Events
            if player_event:
                px, py = self.player.get_grid_pos()

                # Double check to prevent multiple triggers for same tile
                if self.game_map[py][px] in [TILE_PELLET, TILE_POWER_PELLET]:

                    if player_event == EVENT_ATE_PELLET:
                        self.game_map[py][px] = TILE_EMPTY
                        self.total_pellets -= 1
                        self.player.score += PELLELETS_POINT
                        if self.player.score > self.high_score:
                            self.high_score = self.player.score

                    elif player_event == EVENT_ATE_POWER_PELLET:
                        self.game_map[py][px] = TILE_EMPTY
                        self.player.score += POWER_PELLET_POINT
                        if self.player.score > self.high_score:
                            self.high_score = self.player.score
                        self.frightened_mode = True
                        self.frightened_start_time = pygame.time.get_ticks()
                        self.log_message(
                            "Power Pellet eaten! Ghosts Frightened!", CYAN)
                        for ghost in self.ghosts:
                            ghost.start_frightened()

                # Bonus Fruit Logic
                pellets_eaten = self.starting_pellets - self.total_pellets
                if not self.fruit_active and self.fruits_spawned < 2:
                    should_spawn = False
                    if self.fruits_spawned == 0 and pellets_eaten >= 70:
                        should_spawn = True
                    elif self.fruits_spawned == 1 and pellets_eaten >= 170:
                        should_spawn = True

                    if should_spawn:
                        self.fruit_active = True
                        self.fruit_spawn_time = pygame.time.get_ticks()
                        self.fruits_spawned += 1
                        self.fruit_score = 100 * self.current_level
                        self.log_message(
                            f"Bonus Fruit Appeared! ({self.fruit_score} pts)", PINK)

            # Fruit Timer & Collision
            if self.fruit_active:
                if current_time - self.fruit_spawn_time > 10000:
                    self.fruit_active = False
                    self.log_message("Fruit disappeared...", GREY)
                else:
                    fx, fy = self.fruit_pos[0] * TILE_SIZE + \
                        TILE_SIZE//2, self.fruit_pos[1] * \
                        TILE_SIZE + TILE_SIZE//2
                    dist = math.hypot(self.player.pixel_x -
                                      fx, self.player.pixel_y - fy)
                    if dist < self.player.radius + 15:
                        self.fruit_active = False
                        self.player.score += self.fruit_score
                        if self.player.score > self.high_score:
                            self.high_score = self.player.score
                        self.log_message(
                            f"Yummy! Bonus Fruit: {self.fruit_score}", PINK)

            # Victory Check
            if self.total_pellets <= 0:
                self.game_state = GAME_STATE_WIN
                self.log_message("VICTORY! All pellets cleared!", GREEN)
                save_high_score(self.high_score)

            # Collision Detection
            for ghost in self.ghosts:
                dx = self.player.pixel_x - ghost.pixel_x
                dy = self.player.pixel_y - ghost.pixel_y
                distance = math.hypot(dx, dy)
                collision_distance = self.player.radius + ghost.radius

                if distance < collision_distance:
                    if ghost.is_frightened:
                        ghost.eat()
                        self.player.score += GHOST_POINT
                        if self.player.score > self.high_score:
                            self.high_score = self.player.score
                    elif not ghost.is_eaten:
                        self.log_message("Ghost collision!", RED)
                        self.game_state = GAME_STATE_DEATH
                        self.player.start_death_anim()

    def draw_map(self):
        # 1. Background (Walls)
        if self.background_surface:
            self.game_content_surface.blit(self.background_surface, (0, 0))

        # 2. Pellets (Dynamic)
        for y, row in enumerate(self.game_map):
            for x, char in enumerate(row):
                rect_x = x * TILE_SIZE
                rect_y = y * TILE_SIZE
                if char == TILE_PELLET:
                    pygame.draw.circle(self.game_content_surface, WHITE,
                                       (rect_x + TILE_SIZE//2, rect_y + TILE_SIZE//2), 2)
                elif char == TILE_POWER_PELLET:
                    pygame.draw.circle(self.game_content_surface, WHITE,
                                       (rect_x + TILE_SIZE//2, rect_y + TILE_SIZE//2), 6)

        # 3. Fruit
        if self.fruit_active:
            fx = self.fruit_pos[0] * TILE_SIZE + 10
            fy = self.fruit_pos[1] * TILE_SIZE + 10
            pygame.draw.circle(self.game_content_surface,
                               RED, (fx - 4, fy + 2), 5)
            pygame.draw.circle(self.game_content_surface,
                               RED, (fx + 4, fy + 6), 5)
            pygame.draw.line(self.game_content_surface, GREEN,
                             (fx - 4, fy + 2), (fx, fy - 6), 2)
            pygame.draw.line(self.game_content_surface, GREEN,
                             (fx + 4, fy + 6), (fx, fy - 6), 2)

            elapsed = pygame.time.get_ticks() - self.fruit_spawn_time
            remaining_sec = max(0, 10 - elapsed // 1000)
            timer_text = LOG_FONT.render(f"{remaining_sec}s", True, WHITE)
            self.game_content_surface.blit(timer_text, (fx - 10, fy - 25))

    def draw_menu_ui(self, surface):
        title_surf = WIN_FONT.render("PAC-MAN AI", True, YELLOW)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 -
                     title_surf.get_width() // 2, 100))

        subtitle = SCORE_FONT.render("Select Algorithm to Start:", True, WHITE)
        surface.blit(subtitle, (SCREEN_WIDTH // 2 -
                     subtitle.get_width() // 2, 180))

        btn_w, btn_h = 200, 50
        center_x = SCREEN_WIDTH // 2 - btn_w // 2
        buttons = [
            ("1. GREEDY", ALGO_GREEDY, 250, CYAN),
            ("2. BFS", ALGO_BFS, 320, ORANGE),
            ("3. A* (A-Star)", ALGO_ASTAR, 390, PINK)
        ]

        self.menu_buttons = []
        for label, algo, y, color in buttons:
            rect = pygame.Rect(center_x, y, btn_w, btn_h)
            pygame.draw.rect(surface, color, rect, 2)
            text = SCORE_FONT.render(label, True, color)
            surface.blit(text, (rect.centerx - text.get_width() //
                         2, rect.centery - text.get_height() // 2))
            self.menu_buttons.append((rect, algo))

    def draw(self):
        # --- Game Content Render ---
        self.game_content_surface.fill(BLACK)

        if self.game_state == GAME_STATE_MENU:
            self.draw_menu_ui(self.game_content_surface)
        else:
            self.draw_map()

            if self.game_state != GAME_STATE_DEATH:
                self.player.draw(self.game_content_surface)

            # Ghosts
            if self.game_state != GAME_STATE_DEATH:
                flash_white = False
                if self.frightened_mode:
                    elapsed = pygame.time.get_ticks() - self.frightened_start_time
                    remaining = self.level_frightened_duration - elapsed
                    if remaining < 2000:
                        flash_white = (pygame.time.get_ticks() // 200) % 2 == 0

                for ghost in self.ghosts:
                    ghost.draw(self.game_content_surface,
                               flash_white=flash_white)

            # UI Overlays
            # Score
            score_text = SCORE_FONT.render(
                f"SCORE: {int(self.player.score)}", True, WHITE)
            self.game_content_surface.blit(score_text, (10, 10))

            # High Score
            hs_text = SCORE_FONT.render(
                f"HIGH: {int(self.high_score)}", True, YELLOW)
            self.game_content_surface.blit(
                hs_text, (SCREEN_WIDTH // 2 - 40, 10))

            # Lives
            lives_text = SCORE_FONT.render("LIVES:", True, WHITE)
            self.game_content_surface.blit(
                lives_text, (SCREEN_WIDTH - 150, 10))
            for i in range(self.player_lives):
                cx = SCREEN_WIDTH - 90 + i * 25
                cy = 18
                pygame.draw.circle(self.game_content_surface,
                                   YELLOW, (cx, cy), 8)

            # Center Text States
            center_pos = (SCREEN_WIDTH // 2, self.game_content_height // 2)

            if self.game_state == GAME_STATE_START:
                start_text = WIN_FONT.render("READY!", True, YELLOW)
                hint_text = SCORE_FONT.render(
                    "Press ARROW KEYS to Start", True, WHITE)
                self.game_content_surface.blit(
                    start_text, start_text.get_rect(center=center_pos))
                self.game_content_surface.blit(hint_text, hint_text.get_rect(
                    center=(center_pos[0], center_pos[1] + 40)))
                # Show player in start state
                if self.player:
                    self.player.draw(self.game_content_surface)

            elif self.game_state == GAME_STATE_READY:
                # Animation Ready -> GO
                current_ticks = pygame.time.get_ticks()
                elapsed = current_ticks - self.ready_animation_start_time
                if elapsed < 2000:
                    text = WIN_FONT.render("READY!", True, YELLOW)
                    self.game_content_surface.blit(
                        text, text.get_rect(center=center_pos))
                elif elapsed < 3000:
                    text = WIN_FONT.render("GO!", True, GREEN)
                    self.game_content_surface.blit(
                        text, text.get_rect(center=center_pos))
                else:
                    self.game_state = GAME_STATE_PLAYING
                    self.last_mode_switch_time = pygame.time.get_ticks()
                    self.log_message(
                        f"Level {self.current_level} Start! Algo: {self.selected_algorithm}", YELLOW)

            elif self.game_state == GAME_STATE_DEATH:
                if self.player:
                    self.player.draw(self.game_content_surface)

            elif self.game_state == GAME_STATE_PAUSED:
                # Draw overlay
                overlay = pygame.Surface(
                    (SCREEN_WIDTH, self.game_content_height))
                overlay.fill(BLACK)
                overlay.set_alpha(128)
                self.game_content_surface.blit(overlay, (0, 0))

                p_text = WIN_FONT.render("PAUSED", True, YELLOW)
                self.game_content_surface.blit(
                    p_text, p_text.get_rect(center=center_pos))

                resume_text = SCORE_FONT.render(
                    "Press P / ESC to Resume", True, WHITE)
                self.game_content_surface.blit(resume_text, resume_text.get_rect(
                    center=(center_pos[0], center_pos[1] + 40)))

                quit_text = SCORE_FONT.render(
                    "Press Q to Quit to Menu", True, WHITE)
                self.game_content_surface.blit(quit_text, quit_text.get_rect(
                    center=(center_pos[0], center_pos[1] + 70)))

            elif self.game_state == GAME_STATE_GAME_OVER:
                text = GAME_OVER_FONT.render("GAME OVER", True, RED)
                self.game_content_surface.blit(
                    text, text.get_rect(center=center_pos))
                restart_text = SCORE_FONT.render(
                    "Press R to Restart", True, WHITE)
                self.game_content_surface.blit(restart_text, restart_text.get_rect(
                    center=(center_pos[0], center_pos[1] + 50)))

            elif self.game_state == GAME_STATE_WIN:
                text = WIN_FONT.render("YOU WIN!", True, YELLOW)
                self.game_content_surface.blit(
                    text, text.get_rect(center=center_pos))
                restart_text = SCORE_FONT.render(
                    "Press R to Play Again", True, WHITE)
                self.game_content_surface.blit(restart_text, restart_text.get_rect(
                    center=(center_pos[0], center_pos[1] + 50)))

        # --- Final Composition to Display ---
        display_w, display_h = self.display_surface.get_size()
        self.display_surface.fill(BLACK)

        # Scale to Fit
        # If Fullscreen or Wide, maintain aspect ratio
        target_h = display_h
        scale = target_h / self.game_content_height
        target_w = int(SCREEN_WIDTH * scale)

        # Limit width if it's too wide (keep sidebars for logs if we had them, or just centering)
        # Emulating original logic which put logs on the right for wide screens
        is_wide = (display_w / display_h > 1.2) or self.is_fullscreen

        if is_wide:
            if target_w > display_w * 0.7:
                scale = (display_w * 0.7) / SCREEN_WIDTH
                target_w = int(SCREEN_WIDTH * scale)
                target_h = int(self.game_content_height * scale)

            game_x = (display_w * 0.7 - target_w) // 2
            if game_x < 0:
                game_x = 0
            game_y = (display_h - target_h) // 2

            scaled_surf = pygame.transform.scale(
                self.game_content_surface, (target_w, target_h))
            self.display_surface.blit(scaled_surf, (game_x, game_y))

            # Logs Panel on Right
            self.draw_logs_panel(int(display_w * 0.7), 0,
                                 int(display_w * 0.3), display_h)

        else:
            # Center fit
            scale = min(display_w / SCREEN_WIDTH,
                        display_h / self.game_content_height)
            new_w = int(SCREEN_WIDTH * scale)
            new_h = int(self.game_content_height * scale)

            scaled_surf = pygame.transform.scale(
                self.game_content_surface, (new_w, new_h))
            game_x = (display_w - new_w) // 2
            game_y = (display_h - new_h) // 2
            self.display_surface.blit(scaled_surf, (game_x, game_y))

    def draw_logs_panel(self, x, y, width, height):
        # Background
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.display_surface, (20, 20, 20), rect)
        pygame.draw.line(self.display_surface, GREY, (x, 0), (x, height), 2)

        # Controls
        self.draw_controls(x, y + 20, width)

        # Logs
        log_y_start = height // 2

        title = LOG_FONT.render("Game Logs:", True, GREY)
        self.display_surface.blit(title, (x + 20, log_y_start))

        start_y = log_y_start + 30
        line_spacing = 25
        for i, (msg, color) in enumerate(self.game_logs):
            text_surf = LOG_FONT.render(msg, True, color)
            self.display_surface.blit(
                text_surf, (x + 20, start_y + i * line_spacing))

    def draw_controls(self, x, y, width):
        title = SCORE_FONT.render("- CONTROLS -", True, YELLOW)
        self.display_surface.blit(title, (x + 20, y))

        controls = [
            ("ARROW KEYS", "Move"),
            ("P or ESC", "Pause/Resume"),
            ("F11", "Fullscreen"),
            ("Q", "Quit (in Menu/Pause)"),
            ("R", "Restart (End Game)"),
        ]

        curr_y = y + 40
        for key, action in controls:
            k_surf = LOG_FONT.render(key, True, CYAN)
            a_surf = LOG_FONT.render(action, True, WHITE)
            self.display_surface.blit(k_surf, (x + 20, curr_y))
            self.display_surface.blit(a_surf, (x + 20, curr_y + 20))
            curr_y += 50

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            self.handle_input()
            self.update(dt)
            self.draw()
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
