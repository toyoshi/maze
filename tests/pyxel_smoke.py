"""Exercise actual Pyxel drawing, input, and audio definitions without a window."""

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
for sound in main.pyxel.sounds[:5]:
    assert len(sound.notes) > 0
print("Pyxel drawing, input, mute and sound definitions: OK")
