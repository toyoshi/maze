# Progress / handoff — 2026-11-13 JST

## Objective and decisions

Develop toyoshi/maze as a Software Factory. The user initially chose tests/CI first, then selected the highest-autonomy StrongDM-style scenario-driven loop. Requested features: better graphics, effects, route undo, image sharing, exact theoretical-maximum indication, and phone play.

Preserve the original edge-based rules: another edge may revisit a node and apply its value again. Undo restores score, position, and visited cells, including after clear/dead-end. The maximum means the whole board's best goal score, not a continuation estimate.

Adapt the process from shokai/software-factory-mode-2026aki. Do not claim the original skill is installed or active: its Opus-primary environment and related skills are not present. The user explicitly removed this project’s wait-for-push-instruction rule and authorized automatic push after checks; draft PR creation is part of the adopted active-task loop. Merge and production deployment remain separate explicit decisions. No scheduled/background agent is installed.

## Current local implementation

Branch: `codex/software-factory-foundation`, based on `34fe31e`.

- `main.py`: headless rules, full undo, exact used-edge solver, terminal-state handling, updated Pyxel visuals, five synthesized sound cues and mute, browser-state publication.
- `index.html`, `style.css`, `share.js`: responsive page and touch controls; PNG card with date, score, unmarked board and maximum; route, position and move count are hidden; native image share with PNG fallback, cancellation/error handling.
- Pinned Pyxel 3.0.1 for native and WASM. Python 3.11+ documented.
- GitHub Actions configuration for rules, lint/format, actual Pyxel smoke check, and mobile Chromium/WASM integration. Issue and PR templates and acceptance contract added.
- `AGENTS.md` and `docs/factory.md`: small-change workflow, independent review, persistent handoff, publication gates, and complementary loop references.

## Local validation evidence

- 14 unit tests passed on Python 3.12.15. These cover seeded boards, undo, repeated scoring/multipliers, dead ends, goal state, reset, and exact solver comparison with an independent unpruned enumeration (7×7 and 9×9 boards, four seeds each).
- Ruff lint and format checks passed. JavaScript syntax check passed.
- Actual Pyxel 3.0.1 headless draw/input/sound-definition smoke check passed. Headless environment reported no audio device; audible sound quality is not verified.
- Actual WASM game passed mobile Chromium tests: startup, movement, undo, goal then undo, reset, mute, valid PNG download, updated image after scoring, native-share payload/cancellation/error fallback. API stubs were used only for the OS sharing calls.
- Width/height cases: 320×568, 375×667, 390×844, 844×390, 1280×900; no horizontal overflow; tested control targets at least 44×44.
- Phone screenshot and the actual downloadable PNG card were visually inspected.
- Independent fresh-context read-only review inspected Python, JS, UI, tests, CI, docs; no actionable implementation defect found. It identified missing repeated-node and browser end-state/share-update coverage; that coverage was added and passed. Follow-up review found a date-dependent assumption in the browser test: two steps might both land on multipliers and keep the score at zero. The test now advances through up to four distinct non-goal intersections (only three multipliers exist), guaranteeing it reaches a numbered tile before checking a nonzero-score image. The corrected browser test passed, and the final read-only review confirmed the issue resolved with no remaining actionable defects. A later user request changed image sharing to conceal the solution; the renderer now uses only public fields. Added a browser regression assertion that changing or removing visited cells, player position, and move count leaves image pixels identical. The additional independent review found no route/position/move-count leaks across native sharing, download, or error fallback, and no actionable defects in the adapted autonomy rules. All relevant local checks passed before push.

## Limits and next steps

- Pushed the reviewed implementation (`4c9709b`) and opened draft PR https://github.com/toyoshi/maze/pull/1. GitHub Actions Quality started on the PR. Latest-commit CI status and findings are reported in that PR; do not infer success from this progress file. Local execution used Python 3.12 on macOS.
- Real iPhone Safari / Android Chrome testing is still needed for OS file-share behavior, audible output, touch comfort, and slow-network startup. Browser emulation is not physical-device certification.
- No global skill installation or unattended feature loop is configured. Full original workflow would require a supported Claude primary environment and its referenced skills.
- Next product iteration: gather real-device feedback, then refine visuals and sound against that feedback. Keep each change tied to a replayable scenario.
- Standing project authorization: after checks/review, push branch, open/update a draft PR with acceptance evidence and safe handoff summary, then verify latest-commit CI and repair failures. Keep merge and production deployment separate and explicit.
