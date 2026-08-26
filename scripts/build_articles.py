#!/usr/bin/env python3
"""
記事ビルドスクリプト

Markdown(フロントマター付き)の記事ソースを、Corota AI Lab.サイトの
デザインに合わせた静的HTMLに変換し、/articles/ 配下に出力する。
記事一覧ページ(/articles/index.html)も自動で再生成する。

使い方:
    python build_articles.py

デフォルトのパス:
    ソース: D:/develop/SR/Business/articles/*.md
    出力先: D:/develop/仕事/hp/articles/<slug>/index.html
            D:/develop/仕事/hp/articles/index.html (一覧を再生成)

Markdownファイルの先頭にはYAMLフロントマターを書く。例:

    ---
    slug: claude-code-basics
    title: 初心者向け Claude Code の使い方
    date: 2026-08-26
    category: Claude Code
    excerpt: Claude Codeとは何か、何ができるのかを初めての方向けに解説します。
    ---

    ここから本文をMarkdownで書く。
"""
import re
import sys
import pathlib
import argparse
import yaml
import markdown

SRC_DIR_DEFAULT = pathlib.Path(r"D:/develop/SR/Business/articles")
OUT_DIR_DEFAULT = pathlib.Path(r"D:/develop/仕事/hp/articles")

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)

ARTICLE_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-12M9E3R39H"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-12M9E3R39H');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Corota AI Lab.</title>
    <meta name="description" content="{excerpt}">
    <link rel="canonical" href="https://corota-ai-lab.com/articles/{slug}/">
    <meta property="og:type" content="article">
    <meta property="og:locale" content="ja_JP">
    <meta property="og:site_name" content="Corota AI Lab.">
    <meta property="og:title" content="{title} | Corota AI Lab.">
    <meta property="og:description" content="{excerpt}">
    <meta property="og:url" content="https://corota-ai-lab.com/articles/{slug}/">
    <meta property="og:image" content="https://corota-ai-lab.com/favicon.png">
    <meta name="twitter:card" content="summary">
    <link rel="icon" type="image/png" href="/favicon.png">
    <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Noto+Serif+JP:wght@600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": "{title}",
      "datePublished": "{date}",
      "author": {{"@type": "Organization", "name": "Corota AI Lab."}},
      "publisher": {{"@type": "Organization", "name": "Corota AI Lab.", "url": "https://corota-ai-lab.com/"}}
    }}
    </script>
    <style>
        :root {{ --paper: #fcfcfc; --ink: #111111; --accent: #2563eb; }}
        body {{
            background-color: var(--paper); color: var(--ink);
            font-family: 'Inter', 'Noto Sans JP', sans-serif;
        }}
        .serif {{ font-family: 'Noto Serif JP', serif; }}
        .mono  {{ font-family: 'JetBrains Mono', monospace; }}
        .section-border {{ border-top: 1px solid rgba(0,0,0,0.08); }}
        .btn-main {{
            background: var(--ink); color: #fff; padding: 0.75rem 2rem; font-size: 0.75rem;
            letter-spacing: 0.1em; transition: all 0.3s; border-radius: 2px;
        }}
        .btn-main:hover {{ background: var(--accent); transform: translateY(-2px); }}
        .prose {{ color: #334155; }}
        .prose h2 {{ font-family: 'Noto Serif JP', serif; font-style: italic; font-size: 1.5rem; margin-top: 2.5em; }}
        .prose h3 {{ font-weight: 700; font-size: 1.15rem; margin-top: 2em; }}
        .prose a {{ color: var(--accent); }}
        .prose code {{ background: #f1f5f9; padding: 0.15em 0.4em; border-radius: 4px; font-size: 0.85em; }}
        .prose pre {{ background: #0f172a; color: #e2e8f0; padding: 1.25em; border-radius: 8px; overflow-x: auto; }}
        .prose pre code {{ background: none; padding: 0; color: inherit; }}
        .prose blockquote {{ border-left: 3px solid var(--accent); padding-left: 1em; color: #64748b; font-style: normal; }}
    </style>
</head>
<body class="antialiased">

    <header class="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-black/5">
        <div class="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
            <div class="flex items-center gap-4">
                <a href="/" class="mono text-[10px] text-slate-400 hover:text-blue-600 transition">&larr; Corota AI Lab.</a>
                <a href="/articles/" class="mono text-[10px] text-slate-400 hover:text-blue-600 transition">記事一覧</a>
            </div>
            <nav class="hidden md:flex items-center space-x-10">
                <a href="/cases/" class="mono text-[10px] tracking-widest uppercase hover:text-blue-600 transition">Cases</a>
                <a href="/ai-consulting/" class="mono text-[10px] tracking-widest uppercase hover:text-blue-600 transition">Consulting</a>
                <a href="/#contact" class="btn-main px-6 py-2">Contact</a>
            </nav>
        </div>
    </header>

    <main class="pt-16">
        <article class="max-w-3xl mx-auto px-6 py-20 md:py-28">
            <p class="mono text-[10px] text-blue-600 mb-4 tracking-widest uppercase">{date} &middot; {category}</p>
            <h1 class="serif text-3xl md:text-4xl leading-[1.4] mb-12">{title}</h1>
            <div class="prose prose-slate max-w-none">
{content_html}
            </div>
        </article>

        <section class="section-border bg-[#fcfcfc] py-16 px-6">
            <div class="max-w-3xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                <a href="/articles/" class="mono text-[10px] font-bold border-b border-black pb-1 hover:text-blue-600 hover:border-blue-600 transition uppercase tracking-widest">&larr; 記事一覧に戻る</a>
                <a href="/ai-consulting/" class="mono text-[10px] text-slate-400 hover:text-blue-600 transition">AIコンサルの相談はこちら &rarr;</a>
            </div>
        </section>

        <footer class="section-border py-16 bg-white px-6 text-center">
            <p class="mono text-[9px] opacity-40 tracking-widest lowercase">© 2026 corota ai lab. akita nikaho jpn</p>
        </footer>
    </main>
</body>
</html>
"""

CARD_TEMPLATE = """                    <a href="/articles/{slug}/" class="article-card block border border-slate-100 rounded-sm p-8">
                        <p class="mono text-[9px] text-slate-400 mb-3 tracking-widest">{date} &middot; {category}</p>
                        <h3 class="text-base font-medium mb-2">{title}</h3>
                        <p class="text-xs text-slate-400 leading-relaxed">{excerpt}</p>
                    </a>"""

PLACEHOLDER_CARD = """                    <div class="article-card border border-dashed border-slate-200 rounded-sm p-8 flex flex-col justify-center items-center text-center min-h-[220px]">
                        <p class="mono text-[10px] text-slate-300 tracking-widest uppercase mb-3">Coming Soon</p>
                        <p class="text-sm text-slate-400">記事は準備中です。近日公開予定。</p>
                    </div>"""

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-12M9E3R39H"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', 'G-12M9E3R39H');
    </script>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>記事 | Corota AI Lab.</title>
    <meta name="description" content="Corota AI Lab.が発信する、AI活用のヒントや地域でのAI導入事例に関する記事一覧。">
    <link rel="canonical" href="https://corota-ai-lab.com/articles/">
    <meta property="og:type" content="website">
    <meta property="og:locale" content="ja_JP">
    <meta property="og:site_name" content="Corota AI Lab.">
    <meta property="og:title" content="記事 | Corota AI Lab.">
    <meta property="og:description" content="AI活用のヒントや地域でのAI導入事例に関する記事一覧。">
    <meta property="og:url" content="https://corota-ai-lab.com/articles/">
    <meta property="og:image" content="https://corota-ai-lab.com/favicon.png">
    <meta name="twitter:card" content="summary">
    <link rel="icon" type="image/png" href="/favicon.png">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Noto+Serif+JP:wght@600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{ --paper: #fcfcfc; --ink: #111111; --accent: #2563eb; }}
        body {{
            background-color: var(--paper); color: var(--ink);
            font-family: 'Inter', 'Noto Sans JP', sans-serif;
            background-image: radial-gradient(#e5e7eb 0.5px, transparent 0.5px);
            background-size: 40px 40px;
        }}
        .serif {{ font-family: 'Noto Serif JP', serif; }}
        .mono  {{ font-family: 'JetBrains Mono', monospace; }}
        .section-border {{ border-top: 1px solid rgba(0,0,0,0.08); }}
        .btn-main {{
            background: var(--ink); color: #fff; padding: 0.75rem 2rem; font-size: 0.75rem;
            letter-spacing: 0.1em; transition: all 0.3s; border-radius: 2px;
        }}
        .btn-main:hover {{ background: var(--accent); transform: translateY(-2px); }}
        .article-card {{ transition: all 0.3s; }}
        .article-card:hover {{ border-color: #2563eb; transform: translateY(-2px); }}
    </style>
</head>
<body class="antialiased">

    <header class="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-black/5">
        <div class="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
            <div class="flex items-center gap-4">
                <a href="/" class="mono text-[10px] text-slate-400 hover:text-blue-600 transition">&larr; Corota AI Lab.</a>
                <h1 class="font-bold text-lg tracking-tighter hidden md:block">記事</h1>
            </div>
            <nav class="hidden md:flex items-center space-x-10">
                <a href="/cases/" class="mono text-[10px] tracking-widest uppercase hover:text-blue-600 transition">Cases</a>
                <a href="/ai-consulting/" class="mono text-[10px] tracking-widest uppercase hover:text-blue-600 transition">Consulting</a>
                <a href="/#contact" class="btn-main px-6 py-2">Contact</a>
            </nav>
        </div>
    </header>

    <main class="pt-16">

        <section class="max-w-7xl mx-auto px-6 py-24 md:py-32">
            <div class="max-w-2xl">
                <div class="flex items-center gap-2 mb-8">
                    <span class="w-8 h-[1px] bg-blue-600"></span>
                    <span class="mono text-[10px] text-blue-600 font-bold uppercase tracking-[0.3em]">Articles</span>
                </div>
                <h2 class="serif text-4xl md:text-6xl leading-[1.2] mb-10">
                    AI活用の<br><span class="italic font-normal">ヒント</span>と記録。
                </h2>
                <p class="text-slate-500 text-sm md:text-base max-w-md leading-relaxed">
                    AIセミナーの様子、地域企業でのAI導入事例、開発の裏側などを記事として発信していきます。
                </p>
            </div>
        </section>

        <!-- ===== 記事一覧 =====
             このセクションは scripts/build_articles.py によって自動生成されます。
             記事を追加・編集する場合は、D:/develop/SR/Business/articles/ に
             Markdownファイルを追加・編集してから build_articles.py を再実行してください。
             このHTMLを直接手編集しても、次回のビルドで上書きされます。
        -->
        <section class="section-border bg-white py-24 px-6">
            <div class="max-w-7xl mx-auto">
                <div class="article-list grid md:grid-cols-2 gap-8">
{cards_html}
                </div>
            </div>
        </section>

        <footer id="contact" class="section-border py-32 bg-[#fcfcfc] px-6">
            <div class="max-w-7xl mx-auto text-center">
                <h2 class="serif text-4xl md:text-5xl italic mb-10 text-slate-800">気になることがあれば、お気軽にどうぞ。</h2>
                <p class="mono text-[10px] text-slate-400 tracking-[0.5em] mb-16 uppercase">Akita / Nikaho — Data Science &amp; AI</p>
                <div class="inline-block border border-black p-1">
                    <a href="mailto:corota.ai.lab@gmail.com" class="btn-main block px-12 py-4 rounded-none">corota.ai.lab@gmail.com</a>
                </div>
                <div class="mt-32 pt-12 border-t border-slate-100 flex flex-col md:flex-row justify-between items-center gap-6">
                    <p class="mono text-[9px] opacity-40 tracking-widest lowercase">© 2026 corota ai lab. akita nikaho jpn</p>
                    <div class="flex space-x-8 mono text-[9px] opacity-40 uppercase tracking-widest">
                        <a href="/" class="hover:opacity-100 transition">Home</a>
                        <a href="/cases/" class="hover:opacity-100 transition">Cases</a>
                        <a href="/privacy.html" class="hover:opacity-100 transition">Privacy Policy</a>
                    </div>
                </div>
            </div>
        </footer>
    </main>
</body>
</html>
"""


def parse_article(md_path: pathlib.Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"{md_path.name}: フロントマターが見つかりません")
    meta = yaml.safe_load(m.group(1)) or {}
    body_md = m.group(2)
    for key in ("slug", "title", "date", "category", "excerpt"):
        if key not in meta:
            raise ValueError(f"{md_path.name}: フロントマターに '{key}' がありません")
    html_body = markdown.markdown(
        body_md, extensions=["extra", "sane_lists", "toc"]
    )
    meta["date"] = str(meta["date"])
    meta["content_html"] = html_body
    return meta


def build(src_dir: pathlib.Path, out_dir: pathlib.Path) -> None:
    articles = []
    md_files = sorted(src_dir.glob("*.md"))
    if not md_files:
        print(f"警告: {src_dir} にMarkdownファイルが見つかりませんでした。")

    for md_path in md_files:
        meta = parse_article(md_path)
        articles.append(meta)

        article_dir = out_dir / meta["slug"]
        article_dir.mkdir(parents=True, exist_ok=True)
        html = ARTICLE_TEMPLATE.format(
            title=meta["title"],
            date=meta["date"],
            category=meta["category"],
            excerpt=meta["excerpt"],
            slug=meta["slug"],
            content_html=meta["content_html"],
        )
        (article_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"生成: /articles/{meta['slug']}/index.html")

    articles.sort(key=lambda a: a["date"], reverse=True)

    if articles:
        cards_html = "\n\n".join(
            CARD_TEMPLATE.format(
                slug=a["slug"], date=a["date"], category=a["category"],
                title=a["title"], excerpt=a["excerpt"],
            )
            for a in articles
        )
    else:
        cards_html = PLACEHOLDER_CARD

    index_html = INDEX_TEMPLATE.format(cards_html=cards_html)
    (out_dir / "index.html").write_text(index_html, encoding="utf-8")
    print(f"生成: /articles/index.html ({len(articles)}件の記事)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Markdown記事をHTMLにビルドする")
    parser.add_argument("--src", type=pathlib.Path, default=SRC_DIR_DEFAULT)
    parser.add_argument("--out", type=pathlib.Path, default=OUT_DIR_DEFAULT)
    args = parser.parse_args()
    build(args.src, args.out)
