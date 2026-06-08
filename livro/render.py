#!/usr/bin/env python3
"""Renderiza o HTML do livro como PNG (preview) ou PDF (final)."""
from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent


def render(html_path: Path, out: Path, mode: str = "png") -> None:
    file_url = f"file://{html_path.resolve()}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 794, "height": 1123})  # A4 @ 96 DPI
        page.goto(file_url, wait_until="networkidle")
        if mode == "pdf":
            page.pdf(
                path=str(out),
                width="210mm",
                height="297mm",
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                print_background=True,
                prefer_css_page_size=True,
            )
        else:  # png — escala 2x pra preview nítido
            page.set_viewport_size({"width": 1588, "height": 2246})
            page.evaluate("document.body.style.zoom = '2'")
            page.screenshot(path=str(out), full_page=True, omit_background=False)
        browser.close()
    print(f"✓ {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    html = ROOT / "template.html"
    mode = sys.argv[1] if len(sys.argv) > 1 else "png"
    out = ROOT / ("preview.png" if mode == "png" else "livro.pdf")
    render(html, out, mode)
