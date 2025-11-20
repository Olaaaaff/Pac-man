# settings.py
import pygame


# 遊戲視窗與常數
TILE_SIZE = 20
SCREEN_WIDTH = 28 * TILE_SIZE
SCREEN_HEIGHT = 36 * TILE_SIZE
FRIGHTENED_DURATION = 7000 # 7 秒
SPEED = 2 #玩家與鬼的基本速度
SCATTER_DURATION = 7000   # 散開 7 秒
CHASE_DURATION = 20000    # 追逐 20 秒

# 顏色定義
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)       
PINK = (255, 184, 255)  
CYAN = (0, 255, 255)    
ORANGE = (255, 184, 82)
GREY = (150, 150, 150)
FRIGHTENED_BLUE = (0, 0, 139)

# 字型設定
# 初始化字型模組
pygame.font.init()
SCORE_FONT = pygame.font.Font(None, 24)
GAME_OVER_FONT = pygame.font.Font(None, 64)
WIN_FONT = pygame.font.Font(None, 64)

# 分數資料 
PELLELETS_POINT = 10
POWER_PELLET_POINT = 50
GHOST_POINT = 200

# 地圖資料 (Layout) 
MAP_STRINGS = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "W............WW............W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "WOWWWW.WWWWW.WW.WWWWW.WWWWOW",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "W..........................W",
    "W.WWWW.WW.WWWWWWWW.WWWW.WW.W",
    "W.WWWW.WW.WWWWWWWW.WWWW.WW.W",
    "W......WW....WW....WW......W",
    "WWWWWW.WWWWW WW WWWWW.WWWWWW",
    "     W.WWWWW WW WWWWW.W     ",
    "     W.WW          WW.W     ",
    "     W.WW WWW==WWW WW.W     ",     # <--- 加入門 '='
    "WWWWWW.WW W      W WW.WWWWWW",
    "      .   W      W   .      ",
    "WWWWWW.WW W      W WW.WWWWWW",
    "     W.WW WWWWWWWW WW.W     ",
    "     W.WW          WW.W     ",
    "     W.WW WWWWWWWW WW.W     ",
    "WWWWWW.WW WWWWWWWW WW.WWWWWW",
    "W............WW............W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "WO..WW.......  .......WW..OW",
    "WWW.WW.WW.WWWWWWWW.WW.WW.WWW",
    "WWW.WW.WW.WWWWWWWW.WW.WW.WWW",
    "W......WW....WW....WW......W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",
    "W..........................W",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    " ", " ", " ", " ", " "
]

# 將字串地圖轉換成可修改的列表 (List)
GAME_MAP = [list(row) for row in MAP_STRINGS]