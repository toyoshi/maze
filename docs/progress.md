# Progress / handoff — 2026-11-15 JST

## Released baseline

PR #1 established rules/tests/CI; PR #2 added milestone effects, score feedback and opt-in maximum visibility. PR #2 was merged as `5e26b8d`, deployed to https://threen.netlify.app/, and verified with green CI plus live controls/sharing and a live 100/200-point journey.

## Current requests and scope

The user wants the game easier to play on smartphones and an iPhone app plan. Continue the previously requested autonomous SF loop for the mobile-web improvement through checks, independent review, PR/CI and publication. The user then explicitly selected native SwiftUI implementation and asked for a GitHub toyoshi repository. Native source/tests/project are now separated into private toyoshi/threenotesquest-ios. No account purchase, agreement signing, beta distribution or store submission is authorized by this implementation task.

Branch: `codex/mobile-playability`, based on `5e26b8d`.

## Changes

- Compact board-only browser canvas (256×244), preserving native Pyxel's 256×304 HUD. The HTML scoreboard and status provide browser feedback without duplicating it inside the canvas.
- Responsive portrait layout: board, score and movement controls fit the tested small viewports. Direction/undo targets are at least 52px. Sharing/help can scroll on the shortest phones. Landscape places board and controls side by side; safe-area padding is reserved.
- Touch/pen swipes on the board enqueue one legal move/reverse undo. Taps, near-diagonals, cancelled gestures and multitouch are ignored. Board-only touch capture leaves the rest of the page scrollable.
- A bounded eight-action queue replaces the single pending-action slot so fast enabled-button taps are handled in order.
- README explains swipes and links `docs/iphone-plan.md`; its initial-state screenshot is refreshed without revealing the maximum or route.
- iPhone plan is now fixed to SwiftUI native. The separate initial app builds and passes 1,007seed parity plus Core6 tests and iPhone17 Pro/SE Simulator UI checks. WebView is not used; remaining physical-device/store work is documented. No developer credentials were inspected.

## Evidence and remaining checks

- Local 19 rule/feedback tests and real headless Pyxel smoke passed. Native scoring/undo and opt-in reveal remain unchanged.
- Local real-WASM Chromium smoke passed after adding real touch-event swipe tests, accidental-gesture suppression, ordered double-tap tests and phone viewport/52px target assertions.
- Screenshot inspection confirms the compact initial 390px phone layout. 320px portrait and landscape artifacts are also produced for visual inspection.
- Independent read-only Web review found two corner cases: a second finger outside the board could leave a swipe active, and top safe-area padding was absent. Added document-level active touch tracking plus top-inset padding/height reservation. Regression includes mixed board/outside touches and synthetic safe-area values. Both fixes passed the real-WASM regression suite and independent follow-up review found no additional actionable defects. Latest-commit CI and production results are recorded in the PR only after observation.

## Limits / next step

Phone emulation does not certify physical Safari touch handling, audible sound or the native OS sharing sheet. No recurring daemon is installed. For the actual iPhone app, begin with the deterministic GameCore PoC in `docs/iphone-plan.md`; use a physical iPhone and TestFlight before App Store submission.

## Native release support pages (2026-11-15)

Prepared `/ios/privacy.html` and `/ios/support.html` in 20 localizations for the separate SwiftUI app. Privacy describes offline/local save, OS backups, opt-in result PNG sharing, no developer collection or tracking, external link/support handling. Support provides user-authorized r@toyoshi.jp and this public repository’s issue tracker because the native repository is private. No Web gameplay code changes. Native release is still in preparation; neither page claims App Store availability. Fresh independent read-only review covers these pages. Deployment/HTTP evidence is recorded in the PR.
