import copy
import json
import random
import unittest

from main import GameState


def brute_force_maximum(game):
    """Independent reference: enumerate trails without score dominance pruning."""

    def visit(position, used, score):
        if position == game.goal_pos:
            return score
        best = -1
        x, y = position
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            q = (x + dx, y + dy)
            edge = frozenset((position, q))
            if (
                not (0 < q[0] < game.board_size - 1 and 0 < q[1] < game.board_size - 1)
                or edge in used
            ):
                continue
            tile = game.board[q[1]][q[0]]
            next_score = (
                score + tile
                if isinstance(tile, int)
                else score * int(tile[1])
                if tile in ("x2", "x3")
                else score
            )
            best = max(best, visit(q, used | {edge}, next_score))
        return best

    return visit(game.start_pos, set(), 0)


class RulesTests(unittest.TestCase):
    def setUp(self):
        self.game = GameState(seed=20261113)

    def test_daily_board_is_deterministic_without_mutating_global_random(self):
        before = random.getstate()
        other = GameState(seed=20261113)
        self.assertEqual(self.game.board, other.board)
        self.assertEqual(before, random.getstate())
        self.assertNotEqual(self.game.board, GameState(seed=20261114).board)

    def test_multiplier_counts_and_start_goal(self):
        tiles = [tile for row in self.game.board for tile in row]
        self.assertEqual(tiles.count("x2"), 2)
        self.assertEqual(tiles.count("x3"), 1)
        self.assertEqual(self.game.board[1][1], "start")
        self.assertEqual(self.game.board[7][7], "goal")
        self.assertEqual(self.game.score, 0)

    def test_invalid_moves_do_not_change_state(self):
        before = copy.deepcopy(self.game.__dict__)
        for direction in ((0, 0), (-2, 0), (1, 0), (2, 2), (0, -2)):
            self.assertFalse(self.game.move_player(*direction))
        self.assertEqual(self.game.__dict__, before)

    def test_undo_restores_full_state_and_alternate_path(self):
        g = self.game
        before = (g.player_pos[:], g.score, g.visited.copy())
        self.assertTrue(g.move_player(2, 0))
        self.assertTrue(g.visited[(2, 1)])
        self.assertTrue(g.undo())
        self.assertEqual((g.player_pos, g.score, g.visited), before)
        self.assertTrue(g.move_player(0, 2))
        self.assertFalse(g.visited[(2, 1)])

    def test_multiplier_undo_restores_zero_without_division(self):
        g = self.game
        g.board[1][3] = "x3"
        self.assertTrue(g.move_player(2, 0))
        self.assertEqual(g.score, 0)
        self.assertTrue(g.undo())
        self.assertEqual(g.score, 0)

    def test_revisited_number_reapplies_score_but_same_edge_is_blocked(self):
        g = self.game
        g.board[1][3], g.board[3][3], g.board[3][5], g.board[1][5] = 2, 1, 3, "x3"
        for move in ((2, 0), (0, 2), (2, 0), (0, -2), (-2, 0)):
            self.assertTrue(g.move_player(*move))
        self.assertEqual(g.player_pos, [3, 1])
        self.assertEqual(g.score, 20)  # (2 + 1 + 3) * 3 + 2, revisiting the 2.
        self.assertFalse(g.move_player(0, 2))
        self.assertTrue(g.undo())
        self.assertEqual(g.player_pos, [5, 1])
        self.assertEqual(g.score, 18)

    def test_revisited_multiplier_reapplies_and_undo_restores_score(self):
        g = self.game
        g.board[1][3], g.board[3][3], g.board[3][5], g.board[1][5] = "x2", 1, 2, 3
        for move in ((2, 0), (0, 2), (2, 0), (0, -2), (-2, 0)):
            self.assertTrue(g.move_player(*move))
        self.assertEqual(g.score, 12)  # (0 * 2 + 1 + 2 + 3) * 2.
        self.assertTrue(g.undo())
        self.assertEqual(g.score, 6)

    def test_reverse_direction_is_one_step_undo(self):
        g = self.game
        self.assertEqual(g.step(2, 0), "move")
        self.assertEqual(g.step(-2, 0), "undo")
        self.assertEqual(g.player_pos, [1, 1])
        self.assertEqual(g.score, 0)
        self.assertEqual(g.history, [])
        self.assertFalse(g.undo())

    def test_goal_freezes_forward_moves_but_allows_undo(self):
        g = self.game
        for move in [(2, 0)] * 3 + [(0, 2)] * 3:
            self.assertTrue(g.move_player(*move))
        self.assertTrue(g.game_over)
        self.assertEqual(g.share_state()["status"], "clear")
        before = g.score
        self.assertFalse(g.move_player(-2, 0))
        self.assertEqual(g.score, before)
        self.assertTrue(g.undo())
        self.assertFalse(g.game_over)
        self.assertEqual(g.share_state()["status"], "playing")

    def test_dead_end_can_be_undone(self):
        g = self.game
        for move in [(2, 0), (0, 2), (-2, 0), (0, -2)]:
            g.move_player(*move)
        self.assertTrue(g.game_over)
        self.assertEqual(g.share_state()["status"], "stuck")
        self.assertTrue(g.undo())
        self.assertFalse(g.game_over)

    def test_reset_discards_history_and_restores_daily_board(self):
        g = self.game
        board = copy.deepcopy(g.board)
        g.move_player(2, 0)
        g.reset_game()
        self.assertEqual(g.board, board)
        self.assertEqual(g.history, [])
        self.assertEqual(g.player_pos, [1, 1])
        self.assertEqual(g.score, 0)
        self.assertFalse(g.undo())

    def test_exact_solver_matches_independent_enumeration(self):
        for size in (7, 9):
            for seed in (1, 42, 20261113, 20261114):
                with self.subTest(size=size, seed=seed):
                    g = GameState(board_size=size, seed=seed)
                    self.assertEqual(g.maximum_score, brute_force_maximum(g))

    def test_perfect_requires_goal_and_current_snapshot(self):
        g = self.game
        # A controlled all-zero board makes every goal route optimal.
        for y in range(1, 8, 2):
            for x in range(1, 8, 2):
                if g.board[y][x] not in ("start", "goal"):
                    g.board[y][x] = 0
        g.maximum_score = g.solve_maximum()
        self.assertEqual(g.share_state()["status"], "playing")
        for move in [(2, 0)] * 3 + [(0, 2)] * 3:
            g.move_player(*move)
        state = json.loads(json.dumps(g.share_state()))
        self.assertEqual(state["status"], "perfect")
        self.assertEqual(state["maximum"], 0)
        self.assertEqual(state["moves"], 6)
        self.assertEqual(state["mapId"], "20261113")
        self.assertEqual(state["player"], [7, 7])
        g.undo()
        self.assertEqual(g.share_state()["status"], "playing")
        self.assertEqual(g.share_state()["moves"], 5)

    def test_unsupported_board_size_fails_instead_of_infinite_generation(self):
        for size in (0, 5, 8, 11):
            with self.assertRaises(ValueError):
                GameState(board_size=size)


if __name__ == "__main__":
    unittest.main()
