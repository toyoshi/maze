# maze / ThreeNotesQuest

Read `docs/game-spec.md` before changing rules and `docs/factory.md` before planning work.

- The user selected maximum-autonomy, scenario-driven development. Once a requirement is authorized, proceed through planning, implementation, verification, independent evaluation, repair, push, and draft PR creation without requesting routine step approvals. Ask only for unresolved product decisions or actions beyond that scope.
- Keep each change tied to a user requirement and observable acceptance scenarios.
- Work on a feature branch. Keep game rules headless-testable in `GameState`; Pyxel and browser integration belong at the boundary.
- Preserve the daily seeded layout and edge-based movement unless the user changes the rules. Revisiting a node through a new edge reapplies its value; undo restores the full prior state.
- Run the checks documented in README. Fix failures and run affected checks again. Do not weaken acceptance conditions to make a change pass.
- Shared images contain public results and an unmarked board only; never expose used corridors, player position, or move count.
- For UI changes, inspect a real browser screenshot at phone width. Label emulation, API mocks, and untested physical-device behavior honestly.
- Before publishing changes, obtain an independent review with a fresh context. Give the reviewer the diff and acceptance criteria; ask them to read only, without running tests, lint, builds, or changing files. Fix concrete defects and re-review changed code. Do not describe self-review as independent review.
- Keep `docs/progress.md` current with completed work, evidence, open decisions, and the next small task so another session can resume.
- This project has standing authorization for push and draft PR creation after relevant checks and independent review pass. Inspect the remote branch before updating it; never force-push. Observe latest-commit CI and repair failures automatically. Keep the PR draft while CI or evaluation is incomplete. Ready-for-review, merge, and production deployment require explicit user instruction.
- Do not weaken requirements or tests to obtain a pass. If the same blocker recurs three times, report its evidence and the smallest decision needed rather than looping without progress.
