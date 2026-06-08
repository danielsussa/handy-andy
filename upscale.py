#!/usr/bin/env python3
"""Upscale 4x via real-ESRGAN ncnn (remacri-4x) seguido de downscale 2x
via Pillow LANCZOS — resultado final em 2048x3072 (~365 DPI no PDF A4).
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent
ESRGAN_DIR = ROOT / "tools" / "realesrgan-ncnn-vulkan-v0.2.0-macos"
ESRGAN_BIN = ESRGAN_DIR / "realesrgan-ncnn-vulkan"
MODELS = ESRGAN_DIR / "models"
MODEL_NAME = "remacri-4x"


def upscale(input_path: Path, output_path: Path) -> None:
    print(f"→ {input_path.name}")
    with tempfile.TemporaryDirectory() as tmp:
        big = Path(tmp) / "4x.png"
        subprocess.run(
            [
                str(ESRGAN_BIN),
                "-i", str(input_path),
                "-o", str(big),
                "-n", MODEL_NAME,
                "-s", "4",
                "-m", str(MODELS),
            ],
            check=True,
            capture_output=True,
        )
        with Image.open(big) as im:
            target = (im.width // 2, im.height // 2)
            im2 = im.resize(target, Image.LANCZOS)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            im2.save(output_path, optimize=True)
    kb = output_path.stat().st_size // 1024
    print(f"✓ {output_path.name} {output_path.parent.name} ({kb} KB)")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Uso: upscale.py [--out <subdir>] <input.png> [input2.png ...]")
    args = sys.argv[1:]
    out_subdir = "upscaled"
    if args and args[0] == "--out":
        out_subdir = args[1]
        args = args[2:]
    out_dir = ROOT / "imagens" / out_subdir
    for arg in args:
        p = Path(arg)
        if not p.is_absolute():
            p = ROOT / p
        upscale(p, out_dir / p.name)


if __name__ == "__main__":
    main()
