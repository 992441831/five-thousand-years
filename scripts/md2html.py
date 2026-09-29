#!/usr/bin/env python3
"""Convert series markdown files to HTML with the consistent starfield theme."""
import argparse
import re
import sys
from pathlib import Path

import markdown

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
    :root {{
        --bg-deep: #070a14;
        --bg-card: rgba(20, 25, 45, 0.62);
        --border-card: rgba(140, 160, 255, 0.14);
        --text-main: #e8eaf0;
        --text-dim: #b0b6c3;
        --accent-blue: #1e80ff;
        --accent-purple: #a855f7;
        --shadow-card: 0 2px 12px rgba(0, 0, 0, 0.35);
        --shadow-hover: 0 10px 32px rgba(0, 0, 0, 0.55), 0 0 20px rgba(88, 100, 255, 0.12);
    }}

    * {{ box-sizing: border-box; }}

    html, body {{
        margin: 0;
        padding: 0;
        min-height: 100vh;
    }}

    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "微软雅黑", sans-serif;
        line-height: 1.8;
        color: var(--text-main);
        background: var(--bg-deep);
        background-image:
            radial-gradient(900px 620px at 10% -12%, rgba(88, 64, 190, 0.32), transparent 65%),
            radial-gradient(860px 640px at 94% 4%, rgba(30, 128, 255, 0.18), transparent 65%),
            radial-gradient(780px 580px at 80% 90%, rgba(156, 62, 176, 0.16), transparent 65%),
            radial-gradient(640px 520px at 28% 112%, rgba(38, 96, 210, 0.14), transparent 65%);
        background-attachment: fixed;
        overflow-x: hidden;
    }}

    #starfield {{
        position: fixed;
        inset: 0;
        z-index: 0;
        pointer-events: none;
    }}

    .container {{
        position: relative;
        z-index: 1;
        max-width: 860px;
        margin: 0 auto;
        padding: 2rem 1.5rem 3rem;
    }}

    .glass-card {{
        background: var(--bg-card);
        border: 1px solid var(--border-card);
        border-radius: 16px;
        box-shadow: var(--shadow-card);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        padding: 2rem 2.25rem;
        transition: box-shadow 0.3s ease;
    }}

    .glass-card:hover {{
        box-shadow: var(--shadow-hover);
    }}

    .back-link {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        color: var(--accent-blue);
        text-decoration: none;
        font-weight: 500;
        margin-bottom: 1rem;
        transition: color 0.2s ease;
    }}

    .back-link:hover {{
        color: var(--accent-purple);
    }}

    .article-body {{
        color: var(--text-dim);
    }}

    .article-body h1 {{
        font-size: 2rem;
        background: linear-gradient(90deg, var(--text-main) 0%, var(--accent-blue) 70%, var(--accent-purple) 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        border-bottom: 1px solid var(--border-card);
        padding-bottom: 0.6rem;
        margin-top: 0;
    }}

    .article-body h2, .article-body h3, .article-body h4, .article-body h5, .article-body h6 {{
        color: var(--text-main);
        margin-top: 2rem;
        margin-bottom: 1rem;
    }}

    .article-body a {{
        color: var(--accent-blue);
        text-decoration: none;
    }}

    .article-body a:hover {{
        text-decoration: underline;
    }}

    .article-body strong {{
        color: var(--text-main);
    }}

    .article-body code {{
        background: rgba(255, 255, 255, 0.08);
        padding: 0.15em 0.4em;
        border-radius: 4px;
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        font-size: 0.9em;
        color: var(--accent-purple);
    }}

    .article-body pre {{
        background: rgba(0, 0, 0, 0.25);
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
        border: 1px solid var(--border-card);
    }}

    .article-body pre code {{
        background: transparent;
        padding: 0;
        color: var(--text-main);
    }}

    .article-body blockquote {{
        border-left: 3px solid var(--accent-blue);
        margin: 1.5rem 0;
        padding: 0.75rem 1rem;
        background: rgba(30, 128, 255, 0.06);
        border-radius: 0 8px 8px 0;
        color: var(--text-dim);
    }}

    .article-body table {{
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
        border: 1px solid var(--border-card);
    }}

    .article-body th, .article-body td {{
        border: 1px solid var(--border-card);
        padding: 0.6rem 0.8rem;
    }}

    .article-body th {{
        background: rgba(140, 160, 255, 0.1);
        color: var(--text-main);
    }}

    .article-body img {{
        max-width: 100%;
        height: auto;
        border-radius: 8px;
    }}

    .article-body ul, .article-body ol {{
        padding-left: 1.5rem;
    }}

    .article-body li {{
        margin: 0.4rem 0;
    }}

    .article-body hr {{
        border: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-card), transparent);
        margin: 2rem 0;
    }}

    .footer-hint {{
        text-align: center;
        color: var(--text-dim);
        font-size: 0.85rem;
        opacity: 0.7;
        margin-top: 2rem;
    }}

    @media (max-width: 640px) {{
        .container {{ padding: 1.5rem 1rem 2.5rem; }}
        .glass-card {{ padding: 1.5rem; }}
        .article-body h1 {{ font-size: 1.6rem; }}
    }}
</style>
</head>
<body>
    <canvas id="starfield"></canvas>

    <div class="container">
        <a class="back-link" href="../index.html">← 返回目录</a>
        <section class="glass-card article-body">
{content}
        </section>
        <p class="footer-hint">✦ 在星空下阅读五千年 ✦</p>
    </div>

    <script>
        (function () {{
            const canvas = document.getElementById('starfield');
            const ctx = canvas.getContext('2d');
            let width, height;
            const stars = [];
            const STAR_COUNT = 180;

            function resize() {{
                width = window.innerWidth;
                height = window.innerHeight;
                canvas.width = width;
                canvas.height = height;
            }}

            function random(min, max) {{
                return Math.random() * (max - min) + min;
            }}

            function initStars() {{
                stars.length = 0;
                for (let i = 0; i < STAR_COUNT; i++) {{
                    stars.push({{
                        x: random(0, width),
                        y: random(0, height),
                        r: random(0.3, 1.6),
                        alpha: random(0.2, 0.9),
                        speed: random(0.005, 0.02),
                        direction: Math.random() > 0.5 ? 1 : -1
                    }});
                }}
            }}

            function draw() {{
                ctx.clearRect(0, 0, width, height);
                for (const s of stars) {{
                    s.alpha += s.speed * s.direction;
                    if (s.alpha >= 0.95 || s.alpha <= 0.15) {{
                        s.direction *= -1;
                    }}
                    ctx.beginPath();
                    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(210, 220, 255, ${{s.alpha}})`;
                    ctx.fill();
                }}
                requestAnimationFrame(draw);
            }}

            window.addEventListener('resize', () => {{
                resize();
                initStars();
            }});

            resize();
            initStars();
            draw();
        }})();
    </script>
</body>
</html>
"""


def simple_numeric_slug(value: str, separator: str) -> str:
    """Generate _1, _2, ... slugs to match existing article style."""
    simple_numeric_slug.counter += 1
    return f"_{simple_numeric_slug.counter}"


simple_numeric_slug.counter = 0


def md_to_html(md_path: Path, html_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")

    # Extract title from first H1
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else md_path.stem

    # Reset counter per file
    simple_numeric_slug.counter = 0

    md = markdown.Markdown(
        extensions=["toc", "tables", "fenced_code"],
        extension_configs={
            "toc": {
                "slugify": simple_numeric_slug,
            }
        },
    )
    content = md.convert(text)

    # Indent content to sit nicely inside the section tag
    indented = "\n".join("            " + line for line in content.splitlines())

    html = HTML_TEMPLATE.format(title=title, content=indented)
    html_path.write_text(html, encoding="utf-8")
    print(f"Generated {html_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert markdown files to themed HTML.")
    parser.add_argument("files", nargs="+", help="Markdown files to convert")
    parser.add_argument("--out-dir", "-o", type=Path, help="Output directory (defaults to html/ next to md file)")
    args = parser.parse_args()

    for md_file in args.files:
        md_path = Path(md_file)
        if not md_path.exists():
            print(f"File not found: {md_path}", file=sys.stderr)
            continue

        out_dir = args.out_dir or md_path.parent.with_name("html")
        out_dir.mkdir(parents=True, exist_ok=True)
        html_path = out_dir / md_path.with_suffix(".html").name
        md_to_html(md_path, html_path)


if __name__ == "__main__":
    main()
