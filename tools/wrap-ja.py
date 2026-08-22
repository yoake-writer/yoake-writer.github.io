#!/usr/bin/env python3
"""日本語の改行位置を文節単位に固定する。

CSS の word-break: auto-phrase は Chrome 系にしか効かず、Safari（iPhone）では
1文字単位で折り返されて「サムネ／イル」「くだ／さい」のような崩れが出る。
そこで BudouX で文節を判定し、境界に <wbr>（改行可能位置）を埋め込む。
CSS 側は word-break: keep-all で「<wbr> 以外では折り返さない」状態にする。

使い方:  python3 tools/wrap-ja.py            # 全ページを処理
        python3 tools/wrap-ja.py --check    # 変更せず、差分の有無だけ確認
本文を書き換えたら再実行すること（何度実行しても結果は同じ）。
"""
import re, sys, pathlib

try:
    import budoux
except ImportError:
    sys.exit("budoux が必要です:  pip install budoux")

TARGETS = ['index.html', 'kango/index.html']
SKIP_TAGS = {'script', 'style', 'title', 'textarea', 'code', 'pre'}
VOID_TAGS = {'br', 'wbr', 'img', 'meta', 'link', 'input', 'hr', 'source', 'area', 'base', 'col'}
# class="w" は「ここで切らせない」ための既存の仕組みなので、中には改行位置を入れない
SKIP_CLASS = re.compile(r'class="[^"]*\bw\b[^"]*"')
# BudouX が割ってしまう複合語。この境目は改行位置にしない
KEEP_TOGETHER = [
    ('間に', '合わ'), ('引き', '受け'), ('取り', '戻'), ('持ち', '帰'),
    ('打ち', '合わせ'), ('問い', '合わせ'), ('組み', '合わせ'), ('立ち', '上げ'),
    ('切り', '替え'), ('叩き', '台'), ('言い', '回し'), ('書き', '手'),
    ('院内説', '明'), ('夜', '勤'), ('一', '本'), ('回', '分'),
    ('下', '調べ'), ('一つ', '一つ'), ('議事', '録'), ('見', '直'),
    ('説', '明'), ('しに', 'くい'), ('やす', 'さ'), ('入り', '口'),
]
JA = re.compile(r'[぀-ヿ㐀-䶿一-鿿]')
PARSER = budoux.load_default_japanese_parser()


ALNUM = re.compile(r'[A-Za-z0-9]')


def segment(text):
    """テキストを文節に分け、境界に <wbr> を入れて返す。

    BudouX は "YouTube" を "YouTub"+"e" のように英単語の途中で割ることがある。
    英数字が続いている境目は改行位置として不正なので、隣とつなぎ直す。
    """
    chunks = PARSER.parse(text)
    merged = []
    for c in chunks:
        glue = False
        if merged:
            prev = merged[-1]
            if ALNUM.fullmatch(prev[-1]) and ALNUM.fullmatch(c[0]):
                glue = True          # 英単語・数字を分断する境界は採用しない
            elif any(prev.endswith(a) and c.startswith(b) for a, b in KEEP_TOGETHER):
                glue = True          # 複合語を分断する境界も採用しない
        if glue:
            merged[-1] += c
        else:
            merged.append(c)
    return '<wbr>'.join(merged) if len(merged) > 1 else text


def process(html):
    html = html.replace('<wbr>', '')          # 冪等性のため既存の <wbr> を除去
    out, pos, stack = [], 0, []   # stack: 開いている要素が「改行位置を入れない」対象か
    for m in re.finditer(r'<[^>]+>', html):
        text = html[pos:m.start()]
        if text:
            if not any(stack) and JA.search(text):
                lead = re.match(r'\s*', text).group()
                tail = re.search(r'\s*$', text).group()
                body = text[len(lead):len(text) - len(tail) or None]
                out.append(lead + segment(body) + tail)
            else:
                out.append(text)
        tag = m.group()
        name = re.match(r'</?\s*([a-zA-Z0-9]+)', tag)
        if name:
            n = name.group(1).lower()
            if tag.startswith('</'):
                if stack:
                    stack.pop()
            elif not tag.rstrip('>').rstrip('/').endswith('/') and n not in VOID_TAGS:
                stack.append(n in SKIP_TAGS or bool(SKIP_CLASS.search(tag)))
        out.append(tag)
        pos = m.end()
    out.append(html[pos:])
    return ''.join(out)


def main():
    check = '--check' in sys.argv
    root = pathlib.Path(__file__).resolve().parent.parent
    changed = False
    for rel in TARGETS:
        f = root / rel
        src = f.read_text(encoding='utf-8')
        new = process(src)
        n = new.count('<wbr>')
        if new != src:
            changed = True
            if not check:
                f.write_text(new, encoding='utf-8')
        print(f"{rel}: <wbr> {n}個 " + ("(要更新)" if new != src and check else ""))
    if check and changed:
        sys.exit(1)


def audit(root):
    """英数字の途中に改行位置が入っていないか検査する。"""
    bad = 0
    for rel in TARGETS:
        for m in re.finditer(r'([A-Za-z0-9])<wbr>([A-Za-z0-9])', (root / rel).read_text(encoding='utf-8')):
            print(f"  NG {rel}: {m.group(1)}|{m.group(2)}")
            bad += 1
    print("英数字を分断する改行位置: %d件" % bad)
    return bad


if __name__ == '__main__':
    main()
    audit(pathlib.Path(__file__).resolve().parent.parent)
