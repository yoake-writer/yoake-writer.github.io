# CLAUDE.md

ヨアケ（ライター / 動画編集）の GitHub Pages サイト。素の HTML/CSS のみで、
ビルドもフレームワークもパッケージ管理もない。編集したファイルがそのまま公開される。

## ディレクトリの役割

| パス | 中身 | 検索エンジン |
|---|---|---|
| `index.html` | 本体。プロフィール兼ポートフォリオ | 公開 |
| `kango/index.html` | LP「看護師のためのAI活用室」 | 公開 |
| `portfolio/index.html` | `/` へのリダイレクトのみ。**中身を足さない** | `noindex` |
| `works/*/` | 架空クライアント想定の自主制作サンプル6件 | `noindex, nofollow` |
| `tools/wrap-ja.py` | 日本語の改行位置を固定するスクリプト（下記） | — |
| `.claude/notes/lp-qa-checklist.md` | 納品前チェックリスト | — |

## 日本語の改行 ― 一番事故るところ

**改行ルールが2系統ある。混ぜない。**

### 本体2ページ（`index.html`, `kango/index.html`）

CSS が `word-break: keep-all` なので、**`<wbr>` が入っている位置でしか折り返さない**。
その `<wbr>` は `tools/wrap-ja.py` が BudouX（Chrome の `auto-phrase` と同じ
Google の文節分割エンジン）で自動生成している。

**本文テキストを1文字でも変更したら、必ず最後にこれを実行する:**

```sh
python3 tools/wrap-ja.py        # 初回のみ pip install budoux
```

流し忘れると、追加・変更した文が**どこでも折り返せない1本の長い行**になり、
狭い画面ではみ出す。何度実行しても結果は同じ（冪等）なので、迷ったら実行してよい。
変更の有無だけ見たいときは `--check`（要更新なら終了コード 1）。

守ること:

- **`class="w"` の中に `<wbr>` を手で入れない。** ここは改行位置を人が決める場所で、
  スクリプトが意図的に除外している。見出しなどで改行位置を固定したいときは
  `class="w"` で囲う。
- BudouX が複合語を割ってしまうときは、`wrap-ja.py` の `KEEP_TOGETHER` に
  ペアを足して再実行する（「院内説／明」「間に／合わない」など）。
  HTML 側を手で直さない。直しても次の実行で戻る。
- **`overflow-wrap: anywhere` を `break-word` に変えない。** `anywhere` は
  要素の最小幅にも反映されるので、狭い画面でグリッドがはみ出すのを防いでいる。
  `break-word` にすると効かなくなる。

### `works/*/`

こちらは CSS の `word-break: auto-phrase` だけで処理している（Chrome 系のみ有効、
サンプルなので割り切っている）。**`wrap-ja.py` の対象外**で、`TARGETS` にも入っていない。
`works/` 配下に `<wbr>` を手で足さないこと。

## 制作サンプル（`works/*/`）の決まり

- **実在しない架空の店舗・施設。** `<title>` に必ず `(架空)` を入れる。
- 全ページに `<meta name="robots" content="noindex, nofollow">` を入れる。
  実在の店舗と誤認されたり、検索結果に出たりしないため。
- **各制作物は独立させる。** `style.css` を共通化しない。配色（`:root`）も
  `--maxw` も1件ごとに違う値にしてある（例: `salon` は 560px のスマホファースト、
  `koumuten` は 1080px）。別クライアントの想定なので、揃えるほうが不自然になる。

## 納品前

`.claude/notes/lp-qa-checklist.md` を上から通す。特に落としやすいのは:

- 画像の `alt`、本文コントラスト 4.5:1、`header`/`nav`/`main`/`footer` のランドマーク、
  `:focus-visible` のアウトライン、`input` に対応する `label`
- リンク・ボタンのタップ領域 44px 角
- 320〜1440px で横スクロールが出ないこと、内部リンクが全部 200 を返すこと

## 触るときの注意

- **配色は各ファイル冒頭の `:root` 変数だけで変える。** 個別セレクタに色を直書きしない。
- 本体2ページの CSS は HTML 内の `<style>` に内包、`works/*` は `style.css` に分離。
  この構成は変えない。
- OGP の `og:image` / `og:url` と `canonical` は絶対URL
  （`https://yoake-writer.github.io/...`）。相対パスにするとカードが出ない。
- `.nojekyll` は消さない。GitHub Pages の Jekyll 処理を止めている。
