#!/usr/bin/env python3
"""Tritone/quadritone vintage — mapeia luminância do original (grayscale)
pra uma paleta vintage 1940. Como a cor é derivada do próprio pixel do
original, o alinhamento é perfeito por construção: nada de fantasma."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent

# Paletas vintage — cada uma é uma lista de (luminância, RGB) ordenada de
# 0 (preto absoluto) a 1 (branco absoluto). Os pontos intermediários
# interpolam linearmente.
PALETAS: dict[str, list[tuple[float, tuple[int, int, int]]]] = {
    # Verde militar quente — vibe field manual de 1944
    "olive": [
        (0.00, (28, 32, 22)),
        (0.30, (75, 78, 50)),
        (0.55, (140, 130, 85)),
        (0.80, (215, 200, 155)),
        (1.00, (248, 242, 220)),
    ],
    # Sépia amplo — mais marrom, tipo livro velho
    "sepia": [
        (0.00, (30, 22, 16)),
        (0.30, (90, 65, 45)),
        (0.60, (180, 140, 95)),
        (0.85, (235, 215, 175)),
        (1.00, (250, 240, 215)),
    ],
    # Azul-acinzentado militar com olhos quentes no claro
    "duotone-cool": [
        (0.00, (25, 30, 35)),
        (0.35, (70, 85, 90)),
        (0.65, (155, 150, 130)),
        (1.00, (245, 235, 210)),
    ],
    # Mais saturado, vibe pôster de guerra
    "vivid": [
        (0.00, (35, 28, 18)),
        (0.25, (95, 78, 38)),
        (0.55, (175, 135, 70)),
        (0.85, (230, 200, 145)),
        (1.00, (250, 240, 215)),
    ],
}


def tritone(input_path: Path, palette_name: str) -> Path:
    pal = PALETAS[palette_name]
    img = Image.open(input_path).convert("L")
    arr = np.asarray(img, dtype=np.float32) / 255.0  # (h, w) in [0,1]

    stops = np.array([s for s, _ in pal], dtype=np.float32)
    colors = np.array([c for _, c in pal], dtype=np.float32)  # (n, 3)

    h, w = arr.shape
    out = np.zeros((h, w, 3), dtype=np.float32)
    # Interpolação linear segmentada
    for i in range(len(pal) - 1):
        s1, s2 = stops[i], stops[i + 1]
        c1, c2 = colors[i], colors[i + 1]
        if i == len(pal) - 2:
            mask = (arr >= s1) & (arr <= s2)
        else:
            mask = (arr >= s1) & (arr < s2)
        t = (arr[mask] - s1) / max(s2 - s1, 1e-6)
        out[mask] = c1 * (1.0 - t)[:, None] + c2 * t[:, None]

    out = np.clip(out, 0, 255).astype(np.uint8)
    # Permite escolher subdir via env, default "tritone"
    import os
    subdir = os.environ.get("TRITONE_OUT", "tritone")
    out_dir = ROOT / "imagens" / subdir / palette_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / input_path.name
    Image.fromarray(out).save(out_path, optimize=True)
    print(f"✓ {palette_name:14s} {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return out_path


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: tritone.py <input.png> [palette]\nPalettes: " + ", ".join(PALETAS))
    input_path = Path(sys.argv[1])
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    palettes = [sys.argv[2]] if len(sys.argv) > 2 else list(PALETAS)
    for p in palettes:
        if p not in PALETAS:
            sys.exit(f"Paleta desconhecida: {p}. Disponíveis: {', '.join(PALETAS)}")
        tritone(input_path, p)


if __name__ == "__main__":
    main()
