# ThreeNotesQuest

数字と倍率をつないで高得点を狙う、日替わりの経路パズルです。PC・スマホのブラウザ、またはPython / [Pyxel](https://github.com/kitao/pyxel)で遊べます。

**[ブラウザで遊ぶ →](https://threen.netlify.app/)**

<p align="center">
  <img src="docs/images/gameplay.png" width="390" alt="スマホ幅の実ゲーム画面。スコア、理論最高点を見るボタン、方向ボタンと1手戻す操作を表示。">
</p>

## 遊び方

- スタートの **S** から **G** へ。数字を通ると加点、**x2 / x3** を通るとその時点のスコアが倍になります。
- **同じ道は一度だけ**通れます。別の道から同じ交差点に入ると、数字や倍率はもう一度適用されます。
- **1手戻す**と、位置・スコア・通った道が元に戻ります。ゴール後や行き止まりからもやり直せます。
- 100点・200点に初めて到達すると、短い演出とファンファーレでお祝いします。戻して同じ点数に再到達しても鳴り直しません。「最初から」で再挑戦するとリセットされます。
- 理論最高点は **「理論最高点を見る」を押すまで非表示**。表示後、最高点でゴールしていれば **PERFECT** になります。同じ盤面ではリセット後も表示を維持します。

盤面はゲーム開始時の端末の日付で決まります。日付が変わったらページを読み込み直すと、次の日の盤面になります。

## 操作

| 操作 | スマホ・画面ボタン | キーボード | ゲームパッド |
| --- | --- | --- | --- |
| 移動 | 方向ボタン | 矢印 | 十字キー |
| 1手戻す | 「1手戻す」または直前の地点への方向 | Z または反対方向 | B または反対方向 |
| 最初から | 「最初から」 | Space | A |
| 音の切替 | 「音 ON / OFF」 | M | — |
| 理論最高点を表示 | 「理論最高点を見る」 | H | — |

開始時はゲーム画面をタップ／クリックしてください。進めない方向は暗く表示され、直前の地点へ戻る方向は「戻る」と表示されます。動きを減らす端末設定では、動く紙吹雪を省きます。

## 画像でシェア

プレイ中もクリア後も、**画像でシェア / 保存**から結果をPNGにできます。

- 日付・スコア・盤面・達成状況を掲載。**経路・現在位置・手数は載せません**。
- 理論最高点は、ゲーム内で表示した場合だけ画像・共有文にも掲載します。
- 対応ブラウザでは共有メニューを開き、それ以外ではPNGを保存します。ブラウザの画像共有にはHTTPSまたはlocalhostが必要です。

## ローカルで起動

Python 3.11以上を使用します。ブラウザ版・Python版ともPyxel 3.0.1に固定しています。

```bash
git clone https://github.com/toyoshi/maze.git
cd maze
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

ブラウザで確認する場合は `python -m http.server 8000` を実行し、[localhost:8000](http://localhost:8000/)を開きます。WASM版Pyxelの取得にはインターネット接続が必要です。

## 開発・検証

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

最後の2つのPython検証は、実際のPyxelとWASMゲームを使います。ブラウザ検証は100点・200点への実経路、巻き戻し、最高点の表示前後、画像保存、スマホ幅を含みます。OSの共有APIは一部モックしており、実機の音・共有メニュー・操作感は別途確認が必要です。Windowsでは `PYTHONPATH=.` の設定方法をシェルに合わせて変更してください。

GitHub ActionsはPython 3.11 / 3.12 / 3.13とChromiumで検証します。

Software Factoryの流れは、受入シナリオ→実装→テスト→独立評価→修正→push→PR→CI確認です。[開発ルール](AGENTS.md)、[受入仕様](docs/game-spec.md)、[運用方針](docs/factory.md)、[進捗・引継ぎ](docs/progress.md)を参照してください。バックグラウンド常駐エージェントは設定していません。

## License

[MIT](LICENSE)
