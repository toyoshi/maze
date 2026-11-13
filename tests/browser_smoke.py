"""Real WASM game on a mobile viewport; run from repository root.

Loads the pinned Pyxel CDN, so network access is required. No deployed site is
modified. Shared-file APIs are stubbed only for payload/cancellation checks.
"""

import functools
import http.server
import os
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def best_route(snapshot):
    board = snapshot["board"]
    end = (len(board) - 2, len(board) - 2)
    best = (-1, [])

    def walk(pos, used, score, route):
        nonlocal best
        if pos == end:
            if score > best[0]:
                best = (score, route)
            return
        for name, dx, dy in (("right", 2, 0), ("down", 0, 2), ("left", -2, 0), ("up", 0, -2)):
            q = (pos[0] + dx, pos[1] + dy)
            edge = frozenset((pos, q))
            if not (0 < q[0] < len(board) - 1 and 0 < q[1] < len(board) - 1) or edge in used:
                continue
            tile = board[q[1]][q[0]]
            points = (
                score + tile
                if isinstance(tile, int)
                else score * int(tile[1])
                if tile in ("x2", "x3")
                else score
            )
            walk(q, used | {edge}, points, route + [name])

    walk((1, 1), set(), 0, [])
    return best


def check_milestone_journey(browser, port):
    page = browser.new_page(
        viewport={"width": 390, "height": 844},
        is_mobile=True,
        has_touch=True,
        reduced_motion="reduce",
    )
    # Only this test page pins the daily seed. Production code has no test hook.
    fixture = (
        (ROOT / "main.py")
        .read_text()
        .replace('Game(seed=int(datetime.now().strftime("%Y%m%d")))', "Game(seed=20261113)")
    )
    assert fixture != (ROOT / "main.py").read_text()
    page.route("**/main.py", lambda route: route.fulfill(body=fixture, content_type="text/plain"))
    page.goto(f"http://127.0.0.1:{port}", wait_until="domcontentloaded")
    page.locator("#pyxel-prompt").wait_for(state="visible", timeout=90000)
    page.locator("#pyxel-screen").tap()
    page.wait_for_function("!document.querySelector('#shareButton').disabled", timeout=90000)
    page.evaluate("""() => {
      const publish = window.updateGameState;
      window.updateGameState = json => {window.testSnapshot = JSON.parse(json); publish(json);};
    }""")
    page.locator("[data-action=reset]").tap()
    page.wait_for_function("!!window.testSnapshot")
    maximum, route = best_route(page.evaluate("window.testSnapshot"))
    assert maximum >= 200
    observed = []
    for index, direction in enumerate(route, 1):
        page.locator(f"[data-action={direction}]").tap()
        page.wait_for_function("moves => window.testSnapshot.moves === moves", arg=index)
        snapshot = page.evaluate("window.testSnapshot")
        milestone = snapshot["feedback"]["milestone"]
        if milestone:
            observed.append(milestone)
            assert str(milestone) in page.locator("#milestoneMessage").inner_text()
            assert page.evaluate("window.reducedMotion") is True
            if milestone == 200 and os.environ.get("MAZE_MILESTONE_SCREENSHOT"):
                page.screenshot(path=os.environ["MAZE_MILESTONE_SCREENSHOT"], full_page=True)
            if milestone == 200 and os.environ.get("MAZE_CELEBRATION_DETAIL"):
                page.locator("#milestoneMessage").screenshot(
                    path=os.environ["MAZE_CELEBRATION_DETAIL"]
                )
            # Undo removes the transient cue; replaying it does not farm fanfares.
            page.locator("#undoButton").tap()
            page.wait_for_function("moves => window.testSnapshot.moves === moves", arg=index - 1)
            assert page.locator("#milestoneMessage").inner_text() == ""
            page.locator(f"[data-action={direction}]").tap()
            page.wait_for_function("moves => window.testSnapshot.moves === moves", arg=index)
            assert page.evaluate("window.testSnapshot.feedback.milestone") == 0
            assert page.locator("#milestoneMessage").inner_text() == ""
    assert observed == [100, 200], observed
    assert page.evaluate("window.testSnapshot.status") == "clear"
    assert page.locator("#maximumValue").inner_text() == "?"
    assert page.locator("#scoreValue").inner_text() == str(maximum)
    # Hidden maximum does not appear in the shared image or accompanying text.
    assert page.evaluate("""() => {
      const state = window.testSnapshot;
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const texts = [];
      const fill = ctx.fillText.bind(ctx);
      ctx.fillText = (...args) => {texts.push(args[0]); fill(...args);};
      window.renderShareCard(canvas, state);
      return !texts.some(text => String(text).startsWith('BEST POSSIBLE'));
    }""")
    page.evaluate("""() => {
      Object.defineProperty(navigator, 'canShare', {configurable:true, value:()=>true});
      Object.defineProperty(navigator, 'share', {configurable:true, value:async data=>{window.shareText=data.text;}});
    }""")
    page.locator("#shareButton").tap()
    page.wait_for_function("!!window.shareText")
    assert " / " not in page.evaluate("window.shareText")
    page.locator("#maximumButton").tap()
    page.wait_for_function("window.testSnapshot?.maximumRevealed === true")
    assert page.evaluate("window.testSnapshot.status") == "perfect"
    assert page.locator("#maximumValue").inner_text() == str(maximum)
    assert "PERFECT" in page.locator("#result").inner_text()
    page.locator("[data-action=reset]").tap()
    page.wait_for_function("window.testSnapshot.moves === 0")
    for index, direction in enumerate(route, 1):
        page.locator(f"[data-action={direction}]").tap()
        page.wait_for_function("moves => window.testSnapshot.moves === moves", arg=index)
        if page.evaluate("window.testSnapshot.feedback.milestone") == 100:
            assert "100" in page.locator("#milestoneMessage").inner_text()
            break
    else:
        raise AssertionError("Reset did not restore milestone eligibility")
    page.close()


server = http.server.ThreadingHTTPServer(
    ("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(ROOT))
)
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 390, "height": 844},
            is_mobile=True,
            has_touch=True,
            device_scale_factor=1,
        )
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(
            os.environ.get("MAZE_BASE_URL", f"http://127.0.0.1:{server.server_port}"),
            wait_until="domcontentloaded",
        )
        page.locator("#pyxel-prompt").wait_for(state="visible", timeout=90000)
        page.locator("#pyxel-screen").tap()
        page.wait_for_function("!document.querySelector('#shareButton').disabled", timeout=90000)
        page.evaluate("""() => {
          const publish = window.updateGameState;
          window.updateGameState = json => {
            window.testSnapshot = JSON.parse(json);
            publish(json);
          };
        }""")
        assert page.locator("[data-action=up]").is_disabled()
        assert page.locator("[data-action=left]").is_disabled()
        assert page.locator("[data-action=right]").is_enabled()
        initial = page.locator("#result").inner_text()
        assert page.locator("#maximumValue").inner_text() == "?"
        assert page.locator("#maximumButton").is_enabled()
        if os.environ.get("MAZE_README_SCREENSHOT"):
            page.screenshot(path=os.environ["MAZE_README_SCREENSHOT"], full_page=True)
        page.locator("#maximumButton").tap()
        page.wait_for_function("window.testSnapshot?.maximumRevealed === true")
        assert page.locator("#maximumValue").inner_text() == str(
            page.evaluate("window.testSnapshot.maximum")
        )
        assert page.locator("#maximumButton").is_disabled()
        page.locator("[data-action=right]").tap()
        page.wait_for_function("!document.querySelector('#undoButton').disabled")
        page.locator("#undoButton").tap()
        page.wait_for_function("document.querySelector('#undoButton').disabled")
        assert page.locator("#result").inner_text() == initial
        assert page.locator("#scoreValue").inner_text() == "0"
        assert page.locator("#scoreDelta").inner_text().startswith("↶")
        page.locator("#soundButton").tap()
        page.wait_for_function("document.querySelector('#soundButton').textContent === '音 OFF'")
        # Exercise a complete route, terminal-state undo, and daily reset in WASM.
        for index, direction in enumerate(["right"] * 3 + ["down"] * 3, 1):
            page.locator(f"[data-action={direction}]").tap()
            page.wait_for_function("moves => window.testSnapshot.moves === moves", arg=index)
        assert page.evaluate("window.testSnapshot.status") in ("clear", "perfect")
        assert page.locator("#scoreValue").inner_text() == str(
            page.evaluate("window.testSnapshot.score")
        )
        assert page.locator("[data-action=down]").is_disabled()
        assert page.locator("[data-action=up]").get_attribute("data-kind") == "undo"
        page.locator("#undoButton").tap()
        page.wait_for_function("window.testSnapshot.moves === 5")
        assert page.evaluate("window.testSnapshot.status") == "playing"
        page.locator("[data-action=reset]").tap()
        page.wait_for_function("window.testSnapshot.moves === 0")
        assert page.evaluate("window.testSnapshot.score") == 0
        assert page.locator("#result").inner_text() == initial
        # Exercise PNG fallback download, including its actual file signature.
        page.evaluate(
            "Object.defineProperty(navigator, 'canShare', {configurable:true, value:()=>false})"
        )
        with page.expect_download() as info:
            page.locator("#shareButton").tap()
        download = info.value
        assert download.suggested_filename.endswith(".png")
        initial_image = Path(download.path()).read_bytes()
        assert initial_image.startswith(b"\x89PNG\r\n\x1a\n")
        # Native sharing receives an image file; cancellation leaves the UI usable.
        page.evaluate("""() => {
          Object.defineProperty(navigator, 'canShare', {configurable:true, value:()=>true});
          Object.defineProperty(navigator, 'share', {configurable:true, value:async data => {
            window.sharedImage = {type:data.files[0].type, size:data.files[0].size};
            throw new DOMException('cancelled', 'AbortError');
          }});
        }""")
        page.locator("#shareButton").tap()
        page.wait_for_function(
            "document.querySelector('#shareStatus').textContent.includes('キャンセル')"
        )
        assert page.evaluate("window.sharedImage.type") == "image/png"
        assert page.evaluate("window.sharedImage.size") > 1000
        assert page.locator("#shareButton").is_enabled()
        # The actual game canvas and touch targets must fit narrow screens.
        for width, height in ((320, 568), (375, 667), (390, 844), (844, 390), (1280, 900)):
            page.set_viewport_size({"width": width, "height": height})
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (
                width,
                height,
            )
            for action in ("up", "left", "right", "down", "undo"):
                box = page.locator(f"[data-action={action}]").bounding_box()
                assert box["width"] >= 44 and box["height"] >= 44
        page.set_viewport_size({"width": 390, "height": 844})
        # Verify non-cancellation errors expose the PNG fallback link.
        page.evaluate(
            "Object.defineProperty(navigator, 'share', {configurable:true, value:async()=>{throw new Error('unavailable')}})"
        )
        page.locator("#shareButton").tap()
        page.locator("#shareStatus a[download]").wait_for()
        assert page.locator("#shareButton").is_enabled()
        # Four distinct intersections contain at most three multipliers, so this
        # legal, non-goal route must reach a number on every daily board.
        for index, direction in enumerate(("right", "down", "right", "down"), 1):
            page.locator(f"[data-action={direction}]").tap()
            page.wait_for_function("moves => window.testSnapshot.moves === moves", arg=index)
            if index >= 2 and page.evaluate("window.testSnapshot.score") > 0:
                break
        assert page.evaluate("window.testSnapshot.score") > 0
        # Share pixels must reveal no path, position, or move count. The same
        # result renders identically when each private field changes or is absent.
        assert page.evaluate("""() => {
          const state = structuredClone(window.testSnapshot);
          const render = value => window.renderShareCard(document.createElement('canvas'), value).toDataURL();
          const expected = render(state);
          const variants = [
            {...state, visited: [[2, 1], [3, 2], [4, 3]]},
            {...state, player: [7, 5]},
            {...state, moves: 999}
          ];
          const publicState = {...state};
          delete publicState.visited;
          delete publicState.player;
          delete publicState.moves;
          variants.push(publicState);
          return variants.every(value => render(value) === expected);
        }""")
        page.evaluate(
            "Object.defineProperty(navigator, 'canShare', {configurable:true, value:()=>false})"
        )
        with page.expect_download() as final_info:
            page.locator("#shareButton").tap()
        assert Path(final_info.value.path()).read_bytes() != initial_image
        if os.environ.get("MAZE_SHARE_IMAGE"):
            final_info.value.save_as(os.environ["MAZE_SHARE_IMAGE"])
        if os.environ.get("MAZE_SCREENSHOT"):
            page.screenshot(path=os.environ["MAZE_SCREENSHOT"], full_page=True)
        overlay = page.locator("#pyxel-error-overlay")
        assert overlay.count() == 0, overlay.inner_text() if overlay.count() else ""
        assert not errors, errors
        check_milestone_journey(browser, server.server_port)
        browser.close()
        print("Mobile WASM, undo, mute, PNG download, native-share payload/cancel and layout: OK")
finally:
    server.shutdown()
    server.server_close()
