#!/usr/bin/env python3
"""Renderiza o livro em PDF de impressão (280×187mm landscape, 1.5:1).

Estratégia OTIMIZADA (não trava o PC):
1. Carrega o HTML em modo print
2. PARA CADA página (capa + 31 cards + contracapa): scroll-into-view,
   espera SOMENTE a imagem daquela página carregar, tira screenshot.
3. Monta o PDF final no Pillow (multipage).

Cada momento só 1 imagem grande está realmente carregada no Chromium —
memória estável, sem travar.
"""
from __future__ import annotations

import asyncio
import io
import sys
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent
HTML_URL = "http://localhost:8765/livro/livro-completo.html?print"
PDF_OUT = ROOT / "livro" / "handy-andy.pdf"

# Tamanho do PDF: 280×187mm landscape @ 300 DPI = 3307×2209 px (padrão HP Indigo)
DPI = 300
PAGE_WIDTH_PX = int(280 / 25.4 * DPI)
PAGE_HEIGHT_PX = int(187 / 25.4 * DPI)


async def main() -> None:
    PDF_OUT.parent.mkdir(parents=True, exist_ok=True)
    print(f"→ rendering PDF ({DPI} DPI, {PAGE_WIDTH_PX}×{PAGE_HEIGHT_PX}px) from {HTML_URL}")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": PAGE_WIDTH_PX, "height": PAGE_HEIGHT_PX},
            device_scale_factor=1,
        )
        page = await ctx.new_page()

        page.on("pageerror", lambda e: print(f"  [pageerror] {e}"))
        page.on("requestfailed", lambda r: print(f"  [reqfail] {r.url}"))

        await page.goto(HTML_URL, wait_until="domcontentloaded", timeout=60_000)
        print("  DOM loaded.")

        # espera o render() popular
        await page.wait_for_function(
            "document.querySelectorAll('main#livro .card').length > 25",
            timeout=60_000,
        )
        print("  cards rendered.")

        # Coleta TODAS as páginas em ORDEM DE DOCUMENTO (capa → cards → contracapa)
        page_selectors = await page.evaluate(
            """() => {
                const sels = [];
                document.querySelectorAll('section.capa-wrap .page, main#livro .card .page').forEach((el, i) => {
                    el.dataset.printIdx = 'p-' + i;
                    sels.push('[data-print-idx="p-' + i + '"]');
                });
                return sels;
            }"""
        )
        print(f"  {len(page_selectors)} pages to render.")

        # Aplica estilo de print pra cada .page ficar com width/height fixos
        await page.evaluate(
            f"""() => {{
                const style = document.createElement('style');
                style.textContent = `
                    .page, .page.capa, .page.contracapa {{
                        width: {PAGE_WIDTH_PX}px !important;
                        height: {PAGE_HEIGHT_PX}px !important;
                        aspect-ratio: auto !important;
                        box-shadow: none !important;
                        margin: 0 !important;
                    }}
                `;
                document.head.appendChild(style);
                // força todas as imagens a eager (já vão carregar quando entram no viewport)
                document.querySelectorAll('img').forEach(i => i.loading = 'eager');
            }}"""
        )

        screenshots = []
        for idx, sel in enumerate(page_selectors):
            locator = page.locator(sel)
            await locator.scroll_into_view_if_needed()
            # Espera só a imagem dessa página carregar (se tiver)
            try:
                await page.wait_for_function(
                    f"""() => {{
                        const el = document.querySelector('{sel}');
                        if (!el) return false;
                        const imgs = el.querySelectorAll('img');
                        return [...imgs].every(img => img.complete && img.naturalWidth > 0);
                    }}""",
                    timeout=90_000,
                )
            except Exception as e:
                print(f"  [{idx+1}/{len(page_selectors)}] WARN: timeout on {sel}: {e}")
            png_bytes = await locator.screenshot(type="jpeg", quality=92, scale="device")
            screenshots.append(png_bytes)
            sz = len(png_bytes) // 1024
            print(f"  [{idx+1}/{len(page_selectors)}] {sel} → {sz} KB")

        await browser.close()

    # Monta PDF multipage
    print(f"\n→ assembling multipage PDF...")
    images = [Image.open(io.BytesIO(b)).convert("RGB") for b in screenshots]
    # Garante que todas tenham o mesmo tamanho
    target = (PAGE_WIDTH_PX, PAGE_HEIGHT_PX)
    images = [im if im.size == target else im.resize(target, Image.LANCZOS) for im in images]
    images[0].save(
        str(PDF_OUT),
        save_all=True,
        append_images=images[1:],
        resolution=float(DPI),
        format="PDF",
        quality=92,
    )
    kb = PDF_OUT.stat().st_size // 1024
    print(f"✓ {PDF_OUT} ({kb} KB, {kb // 1024} MB · {len(images)} pages)")


if __name__ == "__main__":
    asyncio.run(main())
