import pygame
from settings import *


class Entity:
    """
    遊戲物件的基底類別 (Player 與 Ghost 通用)
    負責處理:
    1. 座標系統 (Grid <-> Pixel)
    2. 網格對齊 (Snap to Grid)
    3. 基本移動
    """

    def __init__(self, grid_x, grid_y, speed):
        self.grid_x = grid_x
        self.grid_y = grid_y

        # 初始化像素座標 (置中)
        self.pixel_x = (self.grid_x * TILE_SIZE) + (TILE_SIZE // 2)
        self.pixel_y = (self.grid_y * TILE_SIZE) + (TILE_SIZE // 2)

        self.speed = speed
        self.direction = (0, 0)  # (dx, dy)

    def get_grid_pos(self):
        """ 計算當前所在的網格座標 """
        self.grid_x = int((self.pixel_x - (TILE_SIZE // 2)) // TILE_SIZE)
        self.grid_y = int((self.pixel_y - (TILE_SIZE // 2)) // TILE_SIZE)
        return self.grid_x, self.grid_y

    def snap_to_grid(self):
        """ 強制將像素座標對齊到最近的網格中心 (防止轉彎時卡住) """
        self.pixel_x = (self.grid_x * TILE_SIZE) + (TILE_SIZE // 2)
        self.pixel_y = (self.grid_y * TILE_SIZE) + (TILE_SIZE // 2)

    def is_centered(self):
        """ 判斷是否位於網格中心 (容許小誤差) """
        # 注意: 如果改用 dt 移動，這裡的誤差容許值可能要調整，或者直接用距離判斷
        dist_x = abs((self.pixel_x - (TILE_SIZE // 2)) % TILE_SIZE)
        dist_y = abs((self.pixel_y - (TILE_SIZE // 2)) % TILE_SIZE)

        # 只要距離中心夠近 (小於一次移動的量)，就視為置中
        # 為了安全起見，這裡可以設一個固定的閾值，例如 1.5 像素
        threshold = self.speed if self.speed > 0 else 1.0

        return dist_x < threshold and dist_y < threshold

    def move(self, dt_seconds=None):
        """ 
        通用移動邏輯 
        dt_seconds: 如果有傳入，表示使用時間差移動 (Frame Independent)
        """
        move_speed = self.speed

        if dt_seconds is not None:
            # 如果使用 dt，這裡的 speed 定義應該是 pixels per second
            # 原本 SPEED = 2 pixels/frame @ 60fps = 120 pixels/sec
            move_speed = self.speed * 60 * dt_seconds

        self.pixel_x += self.direction[0] * move_speed
        self.pixel_y += self.direction[1] * move_speed

        # 隧道處理 (Wrap around)
        if self.pixel_x < -TILE_SIZE // 2:
            self.pixel_x = SCREEN_WIDTH + TILE_SIZE // 2
        elif self.pixel_x > SCREEN_WIDTH + TILE_SIZE // 2:
            self.pixel_x = -TILE_SIZE // 2

        # 同步更新 grid 座標 (在此處不做對齊，只算整數格)
        self.get_grid_pos()
