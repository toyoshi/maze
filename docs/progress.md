# Progress / handoff — 2026-11-13 JST

## Released foundation

PR #1 (https://github.com/toyoshi/maze/pull/1) was merged as `a18d00a` and deployed to https://threen.netlify.app/. All four merge-commit CI jobs passed. Production source files matched that commit, and the live WASM game passed the browser checks. The local checkout was moved to main and the completed local feature branch removed.

## Current authorized iteration

The user requested actual playtesting followed by autonomous implementation, tests, review, merge and publication of the next improvements, specifically suggesting 100/200-point effects. Follow-up requests added README image/text cleanup and making the theoretical maximum opt-in. The authorization includes release of this iteration; do not ask again for those steps. It is not an authorization for unrelated future releases.

Work branch: `codex/score-milestones`, based on `a18d00a`.

## Playtest findings and resulting changes

Played the production game through numeric tiles, multipliers, a dead end, undo, another route, and a 46-point clear using actual screen controls.

- Multiplication from 23 to 46 changed only the small number. Added score delta, an always-visible score panel and 100/200-point celebrations with separate fanfares.
- Clear/dead-end text replaced the outer score. The new panel keeps the score visible through both states.
- Every direction button looked available, including blocked moves. Buttons now expose only legal moves and reverse undo, with explicit undo labels.
- The maximum was visible immediately. The value and PERFECT status are now withheld until explicit reveal; unrevealed browser snapshots, PNG and share text omit the maximum. Revealing after an optimal clear reveals PERFECT. Reveal persists for the same board through reset.
- README lacked a current image and still described the merged feature as unpublished. It now uses an actual phone-width initial-state screenshot without route/maximum spoilers, explains rules and controls, and separates play, sharing and development instructions.

## Acceptance and evidence

The contract is `docs/game-spec.md`. Scoring, daily seeded board, edge reuse and solver are unchanged.

- 19 unit tests passed: rules, independent exhaustive solver comparison, legal/reverse actions, exact threshold boundaries, jumping across both thresholds, undo/replay suppression, timer expiry and reset.
- Actual headless Pyxel checks passed: rendering, input, mute including fanfare, seven sound definitions, reveal and reveal persistence. No audio device exists in this headless environment; audible quality is not asserted.
- Browser coverage runs the real WASM game. A separate local-only page pins the seed to 20261113 and an independent reference enumerator derives a legal route reaching both 100 and 200. It verifies celebration, undo, non-retrigger, reset, reduced-motion preference and an optimal clear before/after reveal. The production code has no seed-testing hook.
- PNG regression checks retain solution hiding; sharing tests verify no maximum text/image before reveal. README screenshot is captured from the real initial game with the maximum hidden.
- Real-WASM browser validation passed locally. Independent read-only review found a native zero-delta feedback omission; it was fixed and covered with real Pyxel text assertions. The follow-up review found no remaining actionable defects. Actual particle rendering is checked with reduced-motion both enabled and disabled. Latest-head CI and deployment evidence are recorded in the PR; do not infer unobserved results from this file.

## Development policy and limits

The user selected StrongDM-style scenario-driven development and removed the source skill's push approval gate for this project. Follow `AGENTS.md` and `docs/factory.md`; do not claim the original Claude-primary skill is installed. Push and draft PR creation are authorized after checks/review. This iteration additionally has explicit authorization for merge and production deployment.

No daemon or recurring automation is installed. Actual device audio, iOS/Android OS sharing and ergonomics remain unverified; Chromium phone emulation and stubbed share APIs do not prove them.
