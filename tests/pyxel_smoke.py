"""Exercise actual Pyxel drawing, input, and audio definitions without a window."""

from types import SimpleNamespace
from unittest.mock import patch

import main

real_init = main.pyxel.init
with (
    patch.object(
        main.pyxel, "init", side_effect=lambda w, h, **kw: real_init(w, h, headless=True, **kw)
    ),
    patch.object(main.pyxel, "run"),
):
    game = main.Game(seed=20261113)
game.draw()
assert game.share_state()["maximum"] is None
assert not game.share_state()["maximumRevealed"]
assert main.pyxel.pget(*game.center(1, 1)) != 1
with patch.object(main.pyxel, "btnp", side_effect=lambda key: key == main.pyxel.KEY_RIGHT):
    game.update()
assert game.player_pos == [3, 1]
with patch.object(main.pyxel, "btnp", side_effect=lambda key: key == main.pyxel.KEY_Z):
    game.update()
assert game.player_pos == [1, 1]
with patch.object(main.pyxel, "btnp", side_effect=lambda key: key == main.pyxel.KEY_M):
    game.update()
assert not game.sound_enabled
for sound in main.pyxel.sounds[:7]:
    assert len(sound.notes) > 0
# Exercise real milestone rendering and cue routing, preserving the game's rules.
game.feedback.record(80, 224, "move")
game.draw()
with patch.object(main.pyxel, "play") as play:
    game.play_sound(6, channel=1)
    play.assert_not_called()  # Mute covers fanfare too.
game.sound_enabled = True
with patch.object(main.pyxel, "play") as play:
    game.play_sound(6, channel=1)
    play.assert_called_once_with(1, 6)
with patch.object(main.pyxel, "btnp", side_effect=lambda key: key == main.pyxel.KEY_SPACE):
    game.update()
assert game.feedback.celebrated == set()
assert game.feedback.frames == 0
# Zero-point moves and undo still have explicit native feedback.
for action, expected in (("move", "+0"), ("undo", "UNDO +0")):
    game.feedback.record(0, 0, action)
    with patch.object(main.pyxel, "text", wraps=main.pyxel.text) as text:
        game.draw()
        assert any(call.args[2] == expected for call in text.call_args_list)
# The OS preference suppresses moving margin particles, but leaves the toast.
game.feedback.record(80, 224, "move")
for reduced in (True, False):
    with (
        patch.object(main, "js", SimpleNamespace(reducedMotion=reduced)),
        patch.object(main.pyxel, "rect", wraps=main.pyxel.rect) as rect,
    ):
        game.draw()
        particles = [
            call
            for call in rect.call_args_list
            if call.args[0] in (3, 250) and call.args[2:4] == (3, 3)
        ]
        assert bool(particles) is not reduced
with patch.object(main.pyxel, "btnp", side_effect=lambda key: key == main.pyxel.KEY_H):
    game.update()
assert game.share_state()["maximum"] == game.maximum_score
assert game.share_state()["maximumRevealed"]
game.reset_game()
assert game.share_state()["maximumRevealed"]  # Same map keeps the explicit reveal.
print("Pyxel drawing, input, mute and sound definitions: OK")
