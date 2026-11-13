# ThreeNotesQuest

Python / [Pyxel](https://github.com/kitao/pyxel)で遊ぶ日替わり経路パズルです。数字と倍率をつないで高得点を狙います。

## 遊ぶ

公開サイト：[ThreeNotesQuest](https://threen.netlify.app/)（このブランチの変更は未公開です）。

- 矢印または画面の方向ボタンで移動。同じ道は一度だけ使用できます。
- Z・ゲームパッドB・「1手戻す」で、位置・スコア・経路を戻せます。直前の地点への反対方向入力でも戻れます。
- Space・ゲームパッドA・「最初から」でリセット。M・「音 ON/OFF」で効果音を切り替えます。
- 理論最高点は盤面全体の最大スコアです。最高点でゴールするとPERFECT。途中やゴール後も、経路・現在位置・手数を隠した画像で共有・保存できます。
- スマホには画面の操作ボタンがあります。ゲーム画面をタップして開始してください。

同じ交差点へ別の道から入ると数字・倍率は再適用されます。日替わり盤面はゲーム開始時の端末の日付で固定されます。ルールと受入条件は [game-spec](docs/game-spec.md) を参照してください。

## 起動

Python 3.11以上、Pyxel 3.0.1を使用します。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

ブラウザで確認する場合：

```bash
python -m http.server 8000
```

[ローカルゲーム](http://localhost:8000/)を開きます。WASM版Pyxelの取得にはインターネットが必要です。画像のネイティブ共有はHTTPSまたはlocalhostの対応ブラウザで利用し、未対応ならPNGを保存します。

## 開発と検証

```bash
pip install -r requirements-dev.txt
python -m playwright install chromium
ruff check main.py tests
ruff format --check main.py tests
python -m unittest discover -s tests -v
PYTHONPATH=. python tests/pyxel_smoke.py
node --check share.js
python tests/browser_smoke.py
```

ルールのテストはPyxelなしでも実行できます。Pyxelの実描画・入力確認はheadlessモードを使います。ブラウザ確認はローカルサーバーを起動し、実際のWASM版でスマホ操作・undo・音の切替・PNG保存・共有APIへの画像受け渡し・キャンセルを検証します。OS共有メニューはモックであり、実機の共有結果や音の聞こえ方は別途確認が必要です。

GitHub ActionsはPython 3.11/3.12/3.13のルール・Pyxel確認と、Chromiumでのブラウザ確認を実行します。設定追加だけではCI実行済みにはなりません。

[開発ルール](AGENTS.md)・[Software Factoryの運用](docs/factory.md)・[進捗と引継ぎ](docs/progress.md)を参照してください。StrongDM型のシナリオ駆動を主軸に、仕様→実装→検証→独立評価→修正→push→Draft PR→CI確認までAIが進めます。通常の各工程で確認は挟まず、ゲームの方向性の未決事項やマージ・本番公開を人が判断します。バックグラウンドの常駐実行は設定していません。

## License

[MIT](LICENSE)
