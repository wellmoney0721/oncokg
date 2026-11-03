"""Inject the pipeline's own output into the dashboard template.

The page never carries hand-typed numbers. Every figure on it is read out of the
artefacts the pipeline wrote, so a stale dashboard is impossible: it is either
rebuilt from the current run or it does not build.

Two outputs:
  web/dashboard.html   fragment form, for publishing as an artifact
  web/index.html       standalone document, for opening from the repository
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

TEMPLATE = C.WEB / "template.html"
FRAGMENT = C.WEB / "dashboard.html"
STANDALONE = C.WEB / "index.html"

WRAPPER_HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{color-scheme:light}body{margin:0;font:14px system-ui,sans-serif}
img{max-width:100%}[hidden]{display:none!important}</style>
"""
WRAPPER_TAIL = "\n</body>\n</html>\n"


def main() -> None:
    payload_path = C.WEB / "data.json"
    if not payload_path.exists():
        sys.exit("web/data.json missing - run make_dashboard_data.py first")
    payload = payload_path.read_text(encoding="utf-8")
    # keep the JSON from terminating the script element it lives in
    payload = payload.replace("</", "<\\/")

    html = TEMPLATE.read_text(encoding="utf-8")
    if "__PAYLOAD__" not in html:
        sys.exit("template.html has no __PAYLOAD__ placeholder")
    html = html.replace("__PAYLOAD__", payload)

    FRAGMENT.write_text(html, encoding="utf-8")

    head_end = html.index("</style>") + len("</style>")
    STANDALONE.write_text(
        WRAPPER_HEAD + html[:head_end] + "\n</head>\n<body>\n"
        + html[head_end:] + WRAPPER_TAIL, encoding="utf-8")

    for p in (FRAGMENT, STANDALONE):
        print(f"-> {p.relative_to(C.ROOT)}  ({p.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
