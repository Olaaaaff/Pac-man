# player.py
import pygame
from settings import *
from entity import Entity


class Player(Entity):
    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, SPEED)
        self.radius = TILE_SIZE // 2 - 2
        self.next_direction = (0, 0)
        self.score = 0
        self.lives = MAX_LIVES

    def draw(self, surface):
        pygame.draw.circle(
            surface, YELLOW, (int(self.pixel_x), int(self.pixel_y)), self.radius)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.next_direction = (0, -1)
            elif event.key == pygame.K_DOWN:
                self.next_direction = (0, 1)
            elif event.key == pygame.K_LEFT:
                self.next_direction = (-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.next_direction = (1, 0)

    def update(self, game_map, dt=0):
        """ 
        更新玩家狀態
        dt: delta time in milliseconds (如果有的話)
        回傳: 事件字串 (ATE_PELLET, etc) 或 None
        """
        dt_seconds = dt / 1000.0 if dt > 0 else None

        # 1. 檢查是否在格子中心 (用於轉彎判定)
        centered = self.is_centered()

        # 2. 嘗試轉彎 (如果玩家有按下方向鍵)
        if self.next_direction != (0, 0):
            # 只有在中心點附近才能轉彎，或者是在反向移動
            # 目前 Pac-Man 規則通常允許隨時反向，但轉彎需要對齊

            # 檢查是否反向 (Reversing)
            is_reverse = (self.next_direction[0] == -self.direction[0] and
                          self.next_direction[1] == -self.direction[1])

            if is_reverse or centered:
                # 檢查轉彎後的目標是否為牆
                curr_x, curr_y = self.get_grid_pos()  # 確保是整數
                next_grid_x = curr_x + self.next_direction[0]
                next_grid_y = curr_y + self.next_direction[1]

                can_turn = True
                if is_wall(game_map, next_grid_x, next_grid_y):
                    can_turn = False

                # 特殊檢查: 門不能進 (除非有特定邏輯，一般 Play 不能進鬼屋)
                if 0 <= next_grid_y < len(game_map) and 0 <= next_grid_x < len(game_map[0]):
                    if game_map[next_grid_y][next_grid_x] == TILE_DOOR:
                        can_turn = False

                if can_turn:
                    self.direction = self.next_direction
                    self.next_direction = (0, 0)
                    # 如果不是反向，而是轉彎，強制對齊網格
                    if not is_reverse:
                        self.snap_to_grid()

        # 3. 移動前檢查前方障礙
        can_move = True
        curr_x, curr_y = self.get_grid_pos()

        # 預測下一步的網格位置
        # 注意：這裡不只檢查相鄰，而是檢查「前方」
        # 如果已經貼牆，就不移動

        # 簡單判定：如果 "不在中心"，通常允許走到中心
        if centered:
            next_grid_x = curr_x + self.direction[0]
            next_grid_y = curr_y + self.direction[1]

            # 邊界檢查 (防止 Index Error) - 雖然 move 會 wrap，但這裡檢查牆壁
            if 0 <= next_grid_y < len(game_map) and 0 <= next_grid_x < len(game_map[0]):
                # 撞牆或撞門
                if is_wall(game_map, next_grid_x, next_grid_y):
                    can_move = False
                if game_map[next_grid_y][next_grid_x] == TILE_DOOR:
                    can_move = False
            else:
                # 超出地圖範圍，如果是隧道 (左右) 則允許
                # 若是上下超出則不允許 (照理說不會發生)
                if not (next_grid_x < 0 or next_grid_x >= len(game_map[0])):
                    can_move = False

        if can_move:
            self.move(dt_seconds)
        else:
            # 撞牆時，強制對齊中心避免微小飄移
            self.snap_to_grid()

        # 4. 吃豆子判定 (不修改地圖，只回傳事件)
        # 取得最新的 grid 座標
        gx, gy = self.get_grid_pos()

        # 邊界保護
        if 0 <= gy < len(game_map) and 0 <= gx < len(game_map[0]):
            tile = game_map[gy][gx]
            if tile == TILE_PELLET:
                return EVENT_ATE_PELLET
            elif tile == TILE_POWER_PELLET:
                return EVENT_ATE_POWER_PELLET

        return None
