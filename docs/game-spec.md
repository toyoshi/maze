# ThreeNotesQuest — acceptance contract

## Board and scoring

- The default 9×9 board contains a 4×4 grid of intersections. Boundary cells and even/even cells are walls.
- Start is (1,1); goal is (7,7). The board is seeded with the local date at game launch, in YYYYMMDD form. It stays the same across reset for that session. Reload after midnight to change the map.
- Intersections other than start and goal contain 1, 2, or 3, except two x2 tiles and one x3 tile.
- A move traverses one corridor between neighboring intersections. A corridor may be used once. Another corridor may revisit an intersection; its number or multiplier applies again, matching the original game.
- Reaching the goal ends forward play immediately. A dead end also ends forward play. Neither state prevents undo or reset.

## Undo

- Z, gamepad B, or the browser Undo button restores the preceding position, score, and all visited cells. A reverse arrow toward the previous position does the same.
- Undo works after a multiplier, including a zero score, and after clear or a dead end. It removes the abandoned move so another route can be taken. It never grants points.
- At the start, undo does nothing. Reset clears all history and restores the seeded board.

## Theoretical maximum

- The maximum is the largest final score among all legal trails from start to goal, with the goal ending a trail. No corridor repeats; intersection values can repeat.
- The solver exhaustively enumerates used-edge states and prunes a state only when an equal-or-better score has already reached the same position using the same edges. This is valid for nonnegative additions and positive multipliers.
- The total is for the whole board, not the best possible continuation of the current route. It remains constant on undo/reset. Hide its value until the user presses the reveal button (or H / the canvas header in native play). Once revealed, it stays revealed for the same board through undo/reset.
- Before revealing, omit the maximum from the browser snapshot, PNG image and sharing text; show a normal clear rather than PERFECT even for an optimal goal route. Revealing after clearing updates the result if optimal.
- Once revealed, PERFECT appears only upon reaching the goal with exactly that score. A partial route matching the number is not PERFECT.
- The supported board sizes are 7 and 9. Larger boards require a separately measured solver strategy before enabling them.

## Graphics, audio, and phones

- Corridors, the used route, numbers, multipliers, start, goal, and player are visually distinct. Labels carry meaning in addition to color.
- Move, multiplier, undo, clear, and blocked-move events have short distinct audio cues. M or the browser sound button toggles audio.
- A 320px-wide browser has no horizontal overflow. Direction and action touch targets are at least 44px wide/high. Controls remain accessible through scrolling on short displays.
- The actual WASM game must start and respond to phone controls, rather than merely displaying a phone-shaped mockup.

## Score feedback and input guidance

- A successful move crossing 100 or 200 points (inclusive) for the first time in an attempt triggers a three-second toast, margin-only confetti, and its own fanfare. A move crossing both thresholds celebrates 200 and marks both reached.
- Cue memory persists through undo, so undo/replay does not retrigger it. Undo immediately clears the animation and fanfare. Reset clears cue memory for a fresh attempt.
- Animation never blocks input, covers board labels, changes scoring, or replaces clear/dead-end feedback. Mute silences fanfares. The web prefers-reduced-motion setting suppresses moving confetti while retaining static text.
- Current score remains visible during play, clear and dead ends. Last-move delta distinguishes undo and resets appropriately.
- Direction buttons are enabled only for a legal forward move or immediate reverse undo; reverse buttons are labeled as undo, including at the goal/dead-end. This supplies input guidance, not a suggested solution.

## Image sharing

- A PNG card includes the map ID (with year), current score, the unmarked daily board, the maximum only if explicitly revealed, and current completion status. It must not reveal the used route, current player position, or move count. Changing or removing those private fields must leave PNG pixels identical for the same public result.
- Every successful move, undo, and reset publishes the current state. Image generation uses that snapshot, avoiding stale score or WebGL capture problems.
- A share gesture invokes native file sharing if supported, otherwise downloads a PNG. Cancelling sharing restores the button. Errors provide a PNG link.
- OS share-sheet behavior, installed sharing destinations, audible output, and physical-device ergonomics require testing on real devices. Browser tests cover integration and API payloads; a mocked native API is not a real OS share.
