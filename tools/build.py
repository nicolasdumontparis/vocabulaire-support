#!/usr/bin/env python3
"""Builds the static support and privacy pages of "Vocabulaire avec Renardo" in 13 languages.

    python3 tools/build.py

Writes index.html (language chooser), <lang>/index.html (support) and <lang>/privacy.html
at the root of the repository, served by GitHub Pages. The texts live in content_a.py and
content_b.py; edit them there, then rebuild.
"""
import html
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from content_a import L as A  # noqa: E402
from content_b import L as B  # noqa: E402

BASE = "https://nicolasdumontparis.github.io/vocabulaire-support/"
EMAIL = "nicolas@sent.com"
ORDER = ["en", "fr", "es", "pt", "zh-hans", "hi", "ar", "ru", "de", "ja", "ko", "it", "id"]
LANGS = {**A, **B}
assert sorted(LANGS) == sorted(ORDER), sorted(LANGS)
NB = " "


def fr_typo(text):
    """French spacing: no-break space before : ; ! ? » and after «."""
    text = re.sub(r" ([:;!?»])", NB + r"\1", text)
    return text.replace("« ", "«" + NB)


def localized(code):
    lang = dict(LANGS[code])
    if code == "fr":
        for key, value in list(lang.items()):
            if isinstance(value, str) and key not in ("html", "dir", "native"):
                lang[key] = fr_typo(value)
            elif isinstance(value, list):
                lang[key] = [tuple(fr_typo(x) for x in item) if isinstance(item, tuple) else fr_typo(item) for item in value]
    return lang


e = html.escape


def head(lang, title, description, page, depth):
    up = "../" * depth
    alternates = "\n".join(
        f'  <link rel="alternate" hreflang="{LANGS[c]["html"]}" href="{BASE}{c}/{page}">' for c in ORDER)
    return f"""<!doctype html>
<html lang="{lang['html']}" dir="{lang['dir']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="canonical" href="{BASE}{lang['code']}/{page}">
{alternates}
  <link rel="alternate" hreflang="x-default" href="{BASE}">
  <link rel="icon" href="{up}favicon.png">
  <link rel="apple-touch-icon" href="{up}apple-touch-icon.png">
  <link rel="stylesheet" href="{up}styles.css">
</head>"""


def picker(lang, page):
    items = "\n".join(
        f'          <li><a href="../{c}/{page}" hreflang="{LANGS[c]["html"]}" lang="{LANGS[c]["html"]}"'
        + (' aria-current="true"' if c == lang["code"] else "") + f'>{e(LANGS[c]["native"])}</a></li>'
        for c in ORDER)
    return f"""      <details class="lang">
        <summary><span aria-hidden="true">🌐</span> {e(lang['native'])}<span class="visually-hidden"> · {e(lang['language'])}</span></summary>
        <ul>
{items}
        </ul>
      </details>"""


def header(lang, page):
    return f"""  <header class="top">
    <a class="brand" href="./"><img src="../icon.jpg" alt="" width="44" height="44"><span>{e(lang['name'])}</span></a>
{picker(lang, page)}
  </header>"""


def footer(lang, page):
    current = ' aria-current="page"'
    return f"""  <footer>
    <nav>
      <a href="./"{current if page == "" else ""}>{e(lang['support'])}</a>
      <a href="privacy.html"{current if page == "privacy.html" else ""}>{e(lang['privacy'])}</a>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
    </nav>
    <p>© 2026 Nicolas Dumont</p>
  </footer>"""


def support_page(code):
    lang = localized(code)
    lang["code"] = code
    facts = "\n".join(f"          <li>{e(f)}</li>" for f in lang["facts"])
    faq = "\n".join(
        f"""        <details class="qa"{' open' if i == 0 else ''}>
          <summary>{e(q)}</summary>
          <p>{e(a)}</p>
        </details>""" for i, (q, a) in enumerate(lang["faq"]))
    title = f"{lang['name']} — {lang['support']}"
    return f"""{head(lang, title, lang['about'], '', 1)}
<body>
<div class="shell">
{header(lang, '')}
  <main>
    <section class="hero">
      <img src="../icon.jpg" alt="" width="168" height="168">
      <div>
        <h1>{e(lang['name'])}</h1>
        <p class="lede">{e(lang['tagline'])}</p>
      </div>
    </section>
    <section class="card about" aria-labelledby="about">
      <h2 id="about">{e(lang['about_h'])}</h2>
      <p>{e(lang['about'])}</p>
      <ul class="facts">
{facts}
      </ul>
    </section>
    <section class="faq" aria-labelledby="faq">
      <h2 id="faq">{e(lang['faq_h'])}</h2>
{faq}
    </section>
    <section class="card contact" aria-labelledby="contact">
      <h2 id="contact">{e(lang['contact_h'])}</h2>
      <p>{e(lang['contact'])} <a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p class="tip">{e(lang['contact_tip'])}</p>
    </section>
  </main>
{footer(lang, '')}
</div>
</body>
</html>
"""


def privacy_page(code):
    lang = localized(code)
    lang["code"] = code
    sections = []
    for i, (h, p) in enumerate(lang["sections"]):
        last = i == len(lang["sections"]) - 1
        body = f'{e(p)} <a href="mailto:{EMAIL}">{EMAIL}</a>' if last else e(p)
        sections.append(f"""    <section class="card">
      <h2>{e(h)}</h2>
      <p>{body}</p>
    </section>""")
    title = f"{lang['name']} — {lang['privacy_h']}"
    return f"""{head(lang, title, lang['sections'][0][1], 'privacy.html', 1)}
<body>
<div class="shell">
{header(lang, 'privacy.html')}
  <main class="policy">
    <h1>{e(lang['privacy_h'])}</h1>
    <p class="date">{e(lang['updated'])}</p>
{chr(10).join(sections)}
  </main>
{footer(lang, 'privacy.html')}
</div>
</body>
</html>
"""


def chooser():
    cards = "\n".join(
        f'      <li><a href="{c}/" hreflang="{LANGS[c]["html"]}" lang="{LANGS[c]["html"]}" dir="{LANGS[c]["dir"]}">'
        f'<strong>{e(LANGS[c]["native"])}</strong><span>{e(LANGS[c]["name"])}</span></a></li>'
        for c in ORDER)
    codes = ", ".join(f'"{c}"' for c in ORDER)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>Vocabulaire avec Renardo — Support</title>
  <meta name="description" content="Support and privacy policy of Vocabulaire avec Renardo, a language-learning app for children aged 6 to 8, in 13 languages.">
  <link rel="canonical" href="{BASE}">
  <link rel="icon" href="favicon.png">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">
  <link rel="stylesheet" href="styles.css">
  <script>
    // Opens the page in the browser's language; "?choose" keeps this chooser.
    (function () {{
      if (location.search.indexOf("choose") >= 0) return;
      var codes = [{codes}];
      var wanted = (navigator.languages || [navigator.language || "en"]);
      for (var i = 0; i < wanted.length; i++) {{
        var w = String(wanted[i]).toLowerCase();
        var code = /^zh-(hans|cn|sg|my)/.test(w) || w === "zh" ? "zh-hans" : w.split("-")[0];
        if (codes.indexOf(code) >= 0) {{ location.replace(code + "/"); return; }}
      }}
    }})();
  </script>
</head>
<body>
<div class="shell">
  <main class="chooser">
    <section class="hero">
      <img src="icon.jpg" alt="" width="168" height="168">
      <div>
        <h1>Vocabulaire avec Renardo</h1>
        <p class="lede">Support · Assistance · Privacy · Confidentialité</p>
      </div>
    </section>
    <ul class="languages">
{cards}
    </ul>
  </main>
  <footer><p>© 2026 Nicolas Dumont · <a href="mailto:{EMAIL}">{EMAIL}</a></p></footer>
</div>
</body>
</html>
"""


def not_found():
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Vocabulaire avec Renardo</title>
  <link rel="stylesheet" href="/vocabulaire-support/styles.css">
</head>
<body>
<div class="shell">
  <main class="policy">
    <h1>404</h1>
    <p><a href="/vocabulaire-support/?choose">Vocabulaire avec Renardo — Support</a></p>
  </main>
</div>
</body>
</html>
"""


def main():
    for code in ORDER:
        folder = ROOT / code
        folder.mkdir(exist_ok=True)
        (folder / "index.html").write_text(support_page(code), encoding="utf-8")
        (folder / "privacy.html").write_text(privacy_page(code), encoding="utf-8")
    (ROOT / "index.html").write_text(chooser(), encoding="utf-8")
    (ROOT / "404.html").write_text(not_found(), encoding="utf-8")
    print(f"{len(ORDER)} languages × 2 pages, index.html and 404.html written in {ROOT}")


if __name__ == "__main__":
    main()
