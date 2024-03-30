# TODO: 進んだ部分の見た目を変更する。今は枠線だが通った部分に線が残るようにする
# TOOD: 進んだ後に戻ることができるようにする
# TODO: どのように進んだか経路を後からデータとして保存できるようにする（経路の再現）
# TODO: Seed値が日付によって決まり同じ日には同じ経路が生成されるようにする

import pyxel
import random

class Game:
    def __init__(self, seed=None):
        self.seed = seed
        self.width = 256
        self.height = 256
        self.cell_size = self.width // 9
        self.start_pos = (1, 1)  # スタート地点の座標
        self.goal_pos = (7, 7)  # ゴール地点の座標
        self.reset_game()

        pyxel.init(self.width, self.height, title="Path Game")
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        random.seed(self.seed)
        self.player_pos = list(self.start_pos)  # プレーヤーの初期位置をスタート地点に設定
        self.score = 0  # スコア
        self.game_over = False
        self.visited = {}  # 訪問済みの通路を追跡
        self.multiplier_used = set()  # 使用済みのマルチプライヤーを追跡
        self.init_game()

    def init_game(self):
        # 交差点と通路の設定
        self.board = [[' ' for _ in range(9)] for _ in range(9)]
        # 外壁と内壁の設定
        for y in range(9):
            for x in range(9):
                if x == 0 or x == 8 or y == 0 or y == 8:  # 外壁
                    self.board[y][x] = 'wall'
                elif y % 2 == 0 and x % 2 == 0:  # 内壁
                    self.board[y][x] = 'wall'

        # 交差点の得点設定
        for y in range(1, 8, 2):
            for x in range(1, 9, 2):
                if (x, y) not in [self.start_pos, self.goal_pos]:
                    self.board[y][x] = random.choice([1, 2, 3])

        # x2 and x3 multipliers are placed at random positions
        multipliers = ['x2', 'x2', 'x3']
        random.shuffle(multipliers)
        for multiplier in multipliers:
            while True:
                x = random.choice(range(1, 9, 2))
                y = random.choice(range(1, 8, 2))
                if (x, y) not in [self.start_pos, self.goal_pos] and isinstance(self.board[y][x], int):
                    self.board[y][x] = multiplier
                    break

        # 訪問済みリストの初期化
        for y in range(9):
            for x in range(9):
                self.visited[(x, y)] = False

        # スタートとゴールの設定
        self.board[self.start_pos[1]][self.start_pos[0]] = 'start'
        self.board[self.goal_pos[1]][self.goal_pos[0]] = 'goal'
        self.visited[self.start_pos] = True  # スタート地点を訪問済みとする

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_SPACE):  # 何かキーが押されたら
                self.reset_game()  # ゲームを初期化
            return

        if self.player_pos == list(self.goal_pos):
            self.game_over = True
            return
        
        # 進める方向がない場合はゲームオーバー
        if not self.get_valid_moves():
            self.game_over = True

        dx, dy = 0, 0
        if pyxel.btnp(pyxel.KEY_UP): dy = -2
        elif pyxel.btnp(pyxel.KEY_DOWN): dy = 2
        elif pyxel.btnp(pyxel.KEY_LEFT): dx = -2
        elif pyxel.btnp(pyxel.KEY_RIGHT): dx = 2

        # 移動先が通路または交差点であり、まだ訪問していないことをチェック
        next_x, next_y = self.player_pos[0] + dx, self.player_pos[1] + dy

        # 通路の中間地点の座標
        mid_x, mid_y = (self.player_pos[0] + next_x) // 2, (self.player_pos[1] + next_y) // 2

        if (0 <= next_x < 9 and 0 <= next_y < 9 and 
            self.board[next_y][next_x] != 'wall' and 
            not self.visited[(mid_x, mid_y)]):

            # 通路を訪問済みとマーク
            self.visited[(next_x, next_y)] = True
            # 前回の場所から今の場所の間にあった通路もマーク
            self.visited[(mid_x, mid_y)] = True

            self.move_player(dx, dy)

    def move_player(self, dx, dy):
        next_pos = (self.player_pos[0] + dx, self.player_pos[1] + dy)
        score = self.board[next_pos[1]][next_pos[0]]

        # 移動先が得点の場合のみスコアを加算
        if (dx != 0 or dy != 0) and isinstance(score, int):
            self.score += score
        elif isinstance(score, str) and score in ['x2', 'x3'] and next_pos not in self.multiplier_used:
            self.score *= int(score[1])
            self.multiplier_used.add(next_pos)

        self.player_pos = list(next_pos)

    def get_valid_moves(self):
        valid_moves = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in directions:
            x, y = self.player_pos[0] + dx, self.player_pos[1] + dy
            next_pos = (x, y)
            if self.board[y][x] != 'wall' and not self.visited[next_pos]:
                valid_moves.append((dx, dy))
        return valid_moves
    
    def draw(self):
        pyxel.cls(0)
        
        # 壁、通路、交差点の描画
        for y in range(9):
            for x in range(9):
                elem = self.board[y][x]
                if elem == 'wall':
                    color = 0  # 黒色
                else:
                    color = 7  # 白色

                # 交差点や通路を描画
                pyxel.rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size, color)

                # Display scores or multipliers
                if isinstance(elem, int) or elem in ['x2', 'x3']:
                    # Calculate the center of the cell
                    center_x = x * self.cell_size + self.cell_size // 2
                    center_y = y * self.cell_size + self.cell_size // 2
                    # Adjust the position to draw the text in the center of the cell
                    text_x = center_x - len(str(elem)) * pyxel.FONT_WIDTH // 2
                    text_y = center_y - pyxel.FONT_HEIGHT // 2
                    # Increase the font size by drawing each character individually and larger
                    for i, char in enumerate(str(elem)):
                        pyxel.text(text_x + i * pyxel.FONT_WIDTH * 2, text_y, char, 0)
        
        # Draw a line in the center of the path that the player has passed
        for (x, y), visited in self.visited.items():
            if visited and not isinstance(self.board[y][x], int) and (x % 2 == 0 or y % 2 == 0):
                center_x = x * self.cell_size + self.cell_size // 2
                center_y = y * self.cell_size + self.cell_size // 2
                pyxel.line(center_x, center_y, center_x , center_y + 1, 8)  # Use red color
                pyxel.line(center_x + 1, center_y, center_x + 1 , center_y + 1, 8)  # Use red color
        
        # スタート地点とゴール地点の描画(Start, Goalと表示)
        pyxel.text(self.start_pos[0] * self.cell_size + self.cell_size // 2 - len("Start") * pyxel.FONT_WIDTH // 2, 
               self.start_pos[1] * self.cell_size + self.cell_size // 2 - pyxel.FONT_HEIGHT // 2, 
               "Start", 8)
        pyxel.text(self.goal_pos[0] * self.cell_size + self.cell_size // 2 - len("Goal") * pyxel.FONT_WIDTH // 2, 
               self.goal_pos[1] * self.cell_size + self.cell_size // 2 - pyxel.FONT_HEIGHT // 2, 
               "Goal", 8)

        # プレーヤーの描画
        pyxel.rect(self.player_pos[0] * self.cell_size, self.player_pos[1] * self.cell_size, self.cell_size, self.cell_size, 8)

        # スコアの表示
        pyxel.text(5, 5, f"Score: {self.score}", 7)

        if self.game_over:
            # Create a window in the center of the screen
            window_width = 150
            window_height = 50
            window_x = (self.width - window_width) // 2
            window_y = (self.height - window_height) // 2
            pyxel.rect(window_x, window_y, window_width, window_height, 6)
            # Display the score and instructions in the window
            pyxel.text(window_x + 20, window_y + 10, f"Score: {self.score}", 0)
            pyxel.text(window_x + 20, window_y + 20, "Press space key to restart", 0)

if __name__ == "__main__":
    Game(seed=12345)
