"""ThreeNotesQuest: deterministic rules, exact solver, and a thin Pyxel view."""

import json
import random
from datetime import datetime

try:
    import pyxel
except ImportError:
    pyxel = None
try:
    import js
except ImportError:
    js = None


class GameState:
    """No graphics or audio dependencies; every successful move is reversible."""

    def __init__(self, board_size=9, seed=None):
        if board_size not in (7, 9):
            raise ValueError("board_size must be 7 or 9")
        self.board_size = board_size
        self.seed = seed
        self.start_pos = (1, 1)
        self.goal_pos = (board_size - 2, board_size - 2)
        self.reset_game()

    def reset_game(self):
        rng = random.Random(self.seed)
        n = self.board_size
        self.board = [[" " for _ in range(n)] for _ in range(n)]
        for y in range(n):
            for x in range(n):
                if x in (0, n - 1) or y in (0, n - 1) or (x % 2 == 0 and y % 2 == 0):
                    self.board[y][x] = "wall"
        for y in range(1, n - 1, 2):
            for x in range(1, n - 1, 2):
                if (x, y) not in (self.start_pos, self.goal_pos):
                    self.board[y][x] = rng.choice([1, 2, 3])
        multipliers = ["x2", "x2", "x3"]
        rng.shuffle(multipliers)
        for multiplier in multipliers:
            while True:
                x = rng.choice(range(1, n - 1, 2))
                y = rng.choice(range(1, n - 1, 2))
                if (x, y) not in (self.start_pos, self.goal_pos) and isinstance(
                    self.board[y][x], int
                ):
                    self.board[y][x] = multiplier
                    break
        self.board[1][1] = "start"
        self.board[self.goal_pos[1]][self.goal_pos[0]] = "goal"
        self.player_pos = list(self.start_pos)
        self.score = 0
        self.visited = {(x, y): False for y in range(n) for x in range(n)}
        self.visited[self.start_pos] = True
        self.history = []
        self.game_over = False
        self.maximum_score = self.solve_maximum()

    @staticmethod
    def score_after(score, tile):
        if isinstance(tile, int):
            return score + tile
        if tile in ("x2", "x3"):
            return score * int(tile[1])
        return score

    def get_valid_moves(self):
        x, y = self.player_pos
        moves = []
        for dx, dy in ((0, -2), (0, 2), (-2, 0), (2, 0)):
            nx, ny = x + dx, y + dy
            if (
                0 <= nx < self.board_size
                and 0 <= ny < self.board_size
                and self.board[ny][nx] != "wall"
                and not self.visited[(x + dx // 2, y + dy // 2)]
            ):
                moves.append((dx, dy))
        return moves

    def move_player(self, dx, dy):
        if self.game_over or (dx, dy) not in self.get_valid_moves():
            return False
        self.history.append((self.player_pos[:], self.score, self.visited.copy()))
        x, y = self.player_pos
        self.visited[(x + dx // 2, y + dy // 2)] = True
        self.player_pos = [x + dx, y + dy]
        self.visited[tuple(self.player_pos)] = True
        self.score = self.score_after(self.score, self.board[y + dy][x + dx])
        self.game_over = tuple(self.player_pos) == self.goal_pos or not self.get_valid_moves()
        return True

    def undo(self):
        if not self.history:
            return False
        self.player_pos, self.score, self.visited = self.history.pop()
        self.game_over = False
        return True

    def step(self, dx, dy):
        # The reverse arrow retraces the last edge; Z / Undo also works at the goal.
        if self.history:
            previous = self.history[-1][0]
            if [self.player_pos[0] + dx, self.player_pos[1] + dy] == previous:
                return "undo" if self.undo() else None
        return "move" if self.move_player(dx, dy) else None

    def solve_maximum(self):
        """Exhaustive edge-trail search, stopping at the goal.

        For equal (position, used edges), only the largest score matters:
        all future additions and multiplications are monotone. Undo does not
        increase the optimum because it restores the entire previous state.
        """
        nodes = [
            (x, y)
            for y in range(1, self.board_size - 1, 2)
            for x in range(1, self.board_size - 1, 2)
        ]
        graph = {p: [] for p in nodes}
        edge = 1
        for x, y in nodes:
            for q in ((x + 2, y), (x, y + 2)):
                if q in graph:
                    graph[(x, y)].append((q, edge))
                    graph[q].append(((x, y), edge))
                    edge <<= 1
        stack = [(self.start_pos, 0, 0)]
        seen = {}
        maximum = 0
        while stack:
            position, used, score = stack.pop()
            key = (position, used)
            if seen.get(key, -1) >= score:
                continue
            seen[key] = score
            if position == self.goal_pos:
                maximum = max(maximum, score)
                continue
            for q, bit in graph[position]:
                if not used & bit:
                    stack.append((q, used | bit, self.score_after(score, self.board[q[1]][q[0]])))
        return maximum

    def get_action_options(self):
        directions = {"up": (0, -2), "down": (0, 2), "left": (-2, 0), "right": (2, 0)}
        valid = self.get_valid_moves() if not self.game_over else []
        options = {name: "move" for name, delta in directions.items() if delta in valid}
        if self.history:
            previous = self.history[-1][0]
            reverse = (previous[0] - self.player_pos[0], previous[1] - self.player_pos[1])
            options.update({name: "undo" for name, delta in directions.items() if delta == reverse})
        return options

    def share_state(self):
        won = tuple(self.player_pos) == self.goal_pos
        return {
            "mapId": str(self.seed) if self.seed is not None else "random",
            "board": self.board,
            "player": self.player_pos,
            "score": self.score,
            "visited": [[x, y] for (x, y), used in self.visited.items() if used],
            "maximum": self.maximum_score,
            "moves": len(self.history),
            "actions": self.get_action_options(),
            "status": "perfect"
            if won and self.score == self.maximum_score
            else "clear"
            if won
            else "stuck"
            if self.game_over
            else "playing",
        }


class ScoreFeedback:
    """Transient presentation only; undo never changes the scoring contract."""

    def __init__(self):
        self.celebrated = set()
        self.milestone = 0
        self.frames = 0
        self.delta_frames = 0
        self.event = {"action": "reset", "delta": 0, "milestone": 0}

    def record(self, before, after, action):
        reached = [
            threshold
            for threshold in (100, 200)
            if action == "move" and before < threshold <= after and threshold not in self.celebrated
        ]
        self.celebrated.update(reached)
        self.event = {
            "action": action,
            "delta": after - before,
            "milestone": max(reached, default=0),
        }
        self.delta_frames = 45
        if action == "undo":
            self.frames = 0
            self.milestone = 0
        elif reached:
            self.milestone = max(reached)
            self.frames = 90
        return self.event["milestone"]

    def tick(self):
        self.frames = max(0, self.frames - 1)
        self.delta_frames = max(0, self.delta_frames - 1)


class Game(GameState):
    def __init__(self, board_size=9, seed=None):
        if pyxel is None:
            raise RuntimeError("Install Pyxel: pip install -r requirements.txt")
        self.sound_enabled = True
        self.maximum_revealed = False
        super().__init__(board_size, seed)
        self.width, self.height = 256, 304
        self.cell_size = 26 if board_size == 9 else 33
        self.board_x = (self.width - board_size * self.cell_size) // 2
        self.board_y = 35
        pyxel.init(self.width, self.height, title="ThreeNotesQuest")
        # Short, distinct cues: move, multiplier, undo, goal, blocked.
        for index, (notes, tone, speed) in enumerate(
            [
                ("c3e3", "p", 5),
                ("e3g3c4", "t", 5),
                ("e3c3", "p", 5),
                ("c3e3g3c4", "t", 8),
                ("c2", "n", 5),
                ("c3e3g3c4e4", "t", 7),
                ("c3e3g3c4e4g4c4", "t", 6),
            ]
        ):
            pyxel.sounds[index].set(notes, tone, "4", "f", speed)
        self.publish_state()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        super().reset_game()
        self.feedback = ScoreFeedback()

    def share_state(self):
        state = super().share_state()
        state["maximumRevealed"] = self.maximum_revealed
        if not self.maximum_revealed:
            state["maximum"] = None
            if state["status"] == "perfect":
                state["status"] = "clear"
        return state

    def publish_state(self, include_feedback=False):
        if js is not None:
            state = self.share_state()
            state["feedback"] = self.feedback.event if include_feedback else {"action": "sync"}
            js.updateGameState(json.dumps(state))

    def update(self):
        self.feedback.tick()
        action = ""
        if js is not None:
            action = str(js.pendingGameAction)
            js.pendingGameAction = ""
        if (
            pyxel.btnp(pyxel.KEY_H)
            or action == "reveal"
            or (
                pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
                and 137 <= pyxel.mouse_x < 245
                and 15 <= pyxel.mouse_y < 31
            )
        ):
            self.maximum_revealed = True
            self.publish_state()
            return
        if pyxel.btnp(pyxel.KEY_M) or action == "mute":
            self.sound_enabled = not self.sound_enabled
            if not self.sound_enabled:
                pyxel.stop()
            if js is not None:
                js.setSoundEnabled(self.sound_enabled)
        if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B) or action == "undo":
            before = self.score
            if self.undo():
                self.feedback.record(before, self.score, "undo")
                pyxel.stop(1)
                self.play_sound(2)
                self.publish_state(include_feedback=True)
            return
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or action == "reset":
            self.reset_game()
            pyxel.stop(1)
            self.publish_state(include_feedback=True)
            return
        directions = [
            ("up", pyxel.KEY_UP, pyxel.GAMEPAD1_BUTTON_DPAD_UP, 0, -2),
            ("down", pyxel.KEY_DOWN, pyxel.GAMEPAD1_BUTTON_DPAD_DOWN, 0, 2),
            ("left", pyxel.KEY_LEFT, pyxel.GAMEPAD1_BUTTON_DPAD_LEFT, -2, 0),
            ("right", pyxel.KEY_RIGHT, pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT, 2, 0),
        ]
        for name, key, pad, dx, dy in directions:
            if pyxel.btnp(key) or pyxel.btnp(pad) or action == name:
                before = self.score
                result = self.step(dx, dy)
                if result:
                    milestone = self.feedback.record(before, self.score, result)
                    if result == "undo":
                        pyxel.stop(1)
                    tile = self.board[self.player_pos[1]][self.player_pos[0]]
                    cue = (
                        2
                        if result == "undo"
                        else 3
                        if tuple(self.player_pos) == self.goal_pos
                        else 1
                        if tile in ("x2", "x3")
                        else 0
                    )
                    # Milestone fanfare uses another channel so clear still sounds.
                    self.play_sound(cue)
                    if milestone:
                        self.play_sound(6 if milestone == 200 else 5, channel=1)
                    self.publish_state(include_feedback=True)
                else:
                    self.play_sound(4)
                break

    def play_sound(self, index, channel=0):
        if self.sound_enabled:
            pyxel.play(channel, index)

    def center(self, x, y):
        return (
            self.board_x + x * self.cell_size + self.cell_size // 2,
            self.board_y + y * self.cell_size + self.cell_size // 2,
        )

    @staticmethod
    def text_center(x, y, text, color):
        pyxel.text(x - len(text) * pyxel.FONT_WIDTH // 2, y - 2, text, color)

    def draw(self):
        pyxel.cls(1)
        pyxel.text(12, 9, "THREE NOTES QUEST", 7)
        pyxel.text(12, 22, f"SCORE {self.score}", 10)
        best_label = f"BEST {self.maximum_score}" if self.maximum_revealed else "BEST: CLICK / H"
        pyxel.text(137, 22, best_label, 11)
        if self.feedback.delta_frames and self.feedback.event["action"] in ("move", "undo"):
            delta = self.feedback.event["delta"]
            label = f"UNDO {delta:+}" if self.feedback.event["action"] == "undo" else f"{delta:+}"
            pyxel.text(85, 22, label, 11 if delta > 0 else 6)
        size = self.cell_size
        for y, row in enumerate(self.board):
            for x, tile in enumerate(row):
                if tile != "wall":
                    pyxel.rect(self.board_x + x * size, self.board_y + y * size, size, size, 5)
        # Completed route in blue; future choices remain visible.
        for (x, y), used in self.visited.items():
            if used and (x % 2 == 0 or y % 2 == 0):
                cx, cy = self.center(x, y)
                if x % 2 == 0:
                    pyxel.rect(cx - size, cy - 2, size * 2, 5, 12)
                else:
                    pyxel.rect(cx - 2, cy - size, 5, size * 2, 12)
        for y in range(1, self.board_size - 1, 2):
            for x in range(1, self.board_size - 1, 2):
                tile = self.board[y][x]
                cx, cy = self.center(x, y)
                color = 9 if tile in ("x2", "x3") else 3
                if tile == "goal":
                    color = 10
                pyxel.rect(cx - 10, cy - 10, 21, 21, color)
                pyxel.rectb(cx - 10, cy - 10, 21, 21, 7 if self.visited[(x, y)] else color)
                label = "S" if tile == "start" else "G" if tile == "goal" else str(tile)
                self.text_center(cx, cy, label, 1 if tile in ("x2", "x3", "goal") else 7)
        cx, cy = self.center(*self.player_pos)
        pyxel.rectb(cx - 12, cy - 12, 25, 25, 10)
        pyxel.circ(cx, cy - 8, 2, 10)
        state = self.share_state()
        message = {
            "perfect": "PERFECT! THEORETICAL MAXIMUM",
            "clear": "CLEAR! TRY ANOTHER ROUTE?",
            "stuck": "NO MOVES - UNDO TO TRY AGAIN",
            "playing": "FIND YOUR HIGHEST SCORING ROUTE",
        }[state["status"]]
        self.text_center(128, 276, message, 10 if state["status"] == "perfect" else 7)
        if self.feedback.frames:
            color = 10 if self.feedback.milestone == 200 else 11
            self.text_center(128, 291, f"{self.feedback.milestone} POINTS! AMAZING ROUTE!", color)
            reduced_motion = js is not None and bool(js.reducedMotion)
            if not reduced_motion:
                # Confetti stays in the outer margins: no board occlusion or flash.
                for index in range(16 if self.feedback.milestone == 200 else 8):
                    x = 3 if index % 2 else self.width - 6
                    y = 40 + ((90 - self.feedback.frames) * 3 + index * 29) % 220
                    pyxel.rect(x, y, 3, 3, (10, 11, 12)[index % 3])
        else:
            self.text_center(128, 291, "ARROWS: MOVE  Z: UNDO  SPACE: RESET  M: SOUND", 6)


if __name__ == "__main__":
    Game(seed=int(datetime.now().strftime("%Y%m%d")))
