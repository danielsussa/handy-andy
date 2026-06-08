#!/usr/bin/env python3
"""Blur gaussian — transforma a vintage AI em mancha de cor pra usar
como base do overlay multiply. 3 intensidades pra comparar."""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent


def blur(input_path: Path, output_path: Path, radius: int) -> None:
    with Image.open(input_path) as im:
        blurred = im.filter(ImageFilter.GaussianBlur(radius=radius))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        blurred.save(output_path, optimize=True)
    print(f"✓ {output_path.name} blur r={radius}  ({output_path.stat().st_size // 1024} KB)")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: blur.py <input.png>")
    input_path = Path(sys.argv[1])
    if not input_path.is_absolute():
        input_path = ROOT / input_path

    out_dir = ROOT / "imagens" / "vintage-blur"
    for r in (20, 50, 100):
        out_name = f"{input_path.stem}_r{r}.png"
        blur(input_path, out_dir / out_name, r)


if __name__ == "__main__":
    main()
