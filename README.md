# Pygame Pac-Man Project

這是一個使用 Python 與 Pygame 函式庫開發的進階《小精靈》(Pac-Man) 復刻版遊戲。本專案不僅還原了經典遊戲機制，更作為一個**路徑搜尋演算法 (Pathfinding Algorithms)** 的視覺化展示平台，允許玩家在遊戲中即時切換與觀察不同 AI 的決策邏輯。

## ✨ 遊戲特色 (Features)

* **經典遊戲機制**：完整實作吃豆子、吃大力丸 (Power Pellets)、鬼魂重生、傳送通道與分數計算。
* **多種路徑演算法**：內建三種不同的鬼魂追蹤演算法，可比較其效能與行為差異：
    * **Greedy (貪婪法)**：只看眼前最近的一步，計算快但容易陷入死路。
    * **BFS (廣度優先搜尋)**：地毯式搜索，保證找到最短路徑，但計算量大。
    * **A* (A-Star)**：結合距離與預估代價，是效能與準確度最佳的選擇。
* **演算法視覺化 (Visual Mode)**：在「Algorithm VISUAL」模式下，畫面會即時繪製出鬼魂計算出的路徑線（Pathfinding Lines），讓您一目了然 AI 打算怎麼抓你。
* **四種鬼魂個性**：忠實還原原作中 Blinky, Pinky, Inky, Clyde 四隻鬼魂不同的目標鎖定邏輯。
* **響應式介面**：支援 F11 全螢幕切換，並在寬螢幕模式下自動顯示側邊除錯日誌 (Log Panel)，即時顯示遊戲狀態與事件。

## 🛠️ 安裝與執行 (Installation)

確保你的電腦已安裝 Python 3.x。

1.  安裝必要的依賴套件：
    ```bash
    pip install -r requirements.txt
    ```

2.  進入 code 資料夾並執行遊戲：
    ```bash
    python code/main.py
    ```

## 🎮 操作說明 (Controls)

### 選單介面 (Menu)
* **滑鼠點擊** 或 **數字鍵 1-4**：選擇鬼魂使用的演算法模式。
    * `1`: Greedy (貪婪)
    * `2`: BFS (廣度優先)
    * `3`: A* (預設推薦)
    * `4`: Algorithm VISUAL (視覺化模式)

### 遊戲中 (In-Game)
* **方向鍵 (↑ ↓ ← →)**：控制小精靈移動。
* **P** 或 **ESC**：暫停 / 繼續遊戲。
* **F11**：切換全螢幕模式。

### 視覺化模式限定 (Visual Mode Only)
當您選擇「Algorithm VISUAL」模式開始遊戲後，可即時切換 AI 演算法：
* **1**：切換為 Greedy
* **2**：切換為 BFS
* **3**：切換為 A*

### 暫停/結束畫面
* **R**：重新開始 (Restart)。
* **Q**：回到主選單 (Quit to Menu)。

## 👻 鬼魂 AI 機制 (Ghost AI)

本專案中的鬼魂並非單純隨機移動，而是根據 **目標點 (Target Tile)** 配合選定的 **演算法** 計算路徑。

### 1. 行為模式 (State Machine)
* **散開 (Scatter)**：鬼魂放棄追捕，轉而繞行地圖四個角落的固定巡邏點（定時切換）。
* **追逐 (Chase)**：根據各自的個性鎖定玩家位置進行夾擊。
* **受驚 (Frightened)**：玩家吃到大力丸後觸發，鬼魂變藍並隨機逃竄，移動速度減慢。

### 2. 鬼魂個性 (Personalities)
* 🔴 **Blinky (紅)**：直球對決，目標鎖定玩家當前位置。
* 🩷 **Pinky (粉)**：預判埋伏，目標設在玩家「前方 4 格」。
* 🩵 **Inky (藍)**：戰術夾擊，參考 Blinky 位置與玩家前方向量計算對稱點。
* 🧡 **Clyde (橘)**：隨性遊走，距離遠時追逐，距離玩家 8 格內時會反而跑回角落。

## 📂 檔案結構 (File Structure)

```text
Pac-man/
├── code/
│   ├── main.py       # 遊戲核心：視窗管理、主迴圈、繪圖與輸入處理
│   ├── settings.py   # 設定檔：定義顏色、地圖佈局、常數 (如速度、分數)
│   ├── player.py     # 玩家類別：處理 Pac-Man 的移動、動畫與碰撞
│   ├── ghost.py      # 鬼魂類別：實作 AI 演算法 (A*/BFS/Greedy) 與狀態機
│   └── entity.py     # 實體基類：定義座標轉換與網格對齊邏輯
├── requirements.txt  # 專案依賴列表
└── README.md         # 專案說明文件
