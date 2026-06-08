#!/usr/bin/env python3
"""Gera CR450 Fuxing do zero (text-to-image) — última página técnica
antes do andy-fim. Estilo lápis grafite, paisagem 1.5:1, com safe zone
no topo-esquerdo pro título.
"""
from __future__ import annotations

import base64
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
ENV = dotenv_values(ROOT / ".env")
API_KEY = ENV.get("OPENAPI_KEY") or ENV.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("Falta OPENAPI_KEY no .env")

client = OpenAI(api_key=API_KEY)

PROMPT = (
    "A detailed graphite pencil illustration on warm cream paper of the "
    "CHINESE CR450 FUXING high-speed bullet train — the fastest commercial "
    "train in the world (450 km/h). "
    "\n\n"
    "Train characteristics: extremely long, sleek aerodynamic body. The "
    "FRONT NOSE is the iconic feature — long, sharply tapered, "
    "fish-mouth or duck-bill shaped, almost like a needle, designed to "
    "cut through air. The body is matte white-silver with a single bold "
    "horizontal accent stripe along its side. Smooth, seamless panel "
    "joints. Tinted forward windshield wrapping around the nose. The "
    "train is shown in PROFILE VIEW (side), with the nose to the right, "
    "and one or two cars trailing visibly. "
    "\n\n"
    "Setting: the train sits on or glides along a modern Chinese "
    "high-speed concrete viaduct/rail (visible elevated track beneath). "
    "Behind: a sleek modern Chinese landscape — futuristic city skyline "
    "in the far distance (modern skyscrapers, faintly drawn), some "
    "pylons of modern slim design, soft horizon haze. The vibe is "
    "FUTURISTIC, fast, optimistic — like 2026 China. "
    "\n\n"
    "CRITICAL composition: the train and viaduct occupy the LOWER-RIGHT "
    "60% of the canvas. The TOP-LEFT 22% width × 18% height MUST stay "
    "MOSTLY EMPTY cream paper / soft sky (reserved for title text). No "
    "dense scenery or train parts in the upper-left corner. "
    "\n\n"
    "Style: graphite pencil on warm cream paper, visible pencil strokes, "
    "soft tonal shading, technical-illustration precision. NO color, NO "
    "painterly textures, NO photographic elements. Match a vintage "
    "encyclopedia pencil-drawing aesthetic. "
    "\n\n"
    "Landscape 1.5:1 (1536x1024). No text, no border, no frame, no "
    "watermark, no labels."
)


def main() -> None:
    out_dir = ROOT / "imagens" / "outpainted-breathe"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "trem-cr450.png"

    print(f"→ generate CR450 Fuxing → {out_path.name}")
    resp = client.images.generate(
        model="gpt-image-1",
        prompt=PROMPT,
        size="1536x1024",
        quality="high",
        n=1,
    )
    b64 = resp.data[0].b64_json
    if not b64:
        raise SystemExit("Sem b64_json")
    out_path.write_bytes(base64.b64decode(b64))
    print(f"✓ {out_path} ({out_path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
