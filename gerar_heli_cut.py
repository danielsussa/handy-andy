#!/usr/bin/env python3
"""Gera um helicóptero estilo cutaway (Stephen Biesty) do zero.
Vai substituir o aviao-08 (página 16) — mantém o nome `aviao-08`
pra não ter que mexer em pages.json.
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
    "A detailed graphite pencil CUTAWAY illustration on warm cream paper "
    "of a SIKORSKY CH-53 SEA STALLION military transport helicopter "
    "(USA, late 1960s) — shown in side profile with portions of the "
    "fuselage CUT AWAY to reveal the INTERNAL MECHANICS. Style: vintage "
    "encyclopedia / Stephen Biesty pencil-cutaway aesthetic. "
    "\n\n"
    "Composition: helicopter shown in SIDE VIEW from the left, nose to the "
    "left, tail to the right. The main rotor blades stretch across the top "
    "of the canvas. The fuselage skin is removed in patches to expose: "
    "(1) the COCKPIT with seats and pilots' controls visible through a "
    "cutaway in the nose; (2) the MAIN CARGO BAY interior with ribbed "
    "structural frames; (3) the TURBOSHAFT ENGINES on top of the fuselage "
    "behind the rotor mast — visible turbine blades and exhaust ducts; "
    "(4) the MAIN ROTOR MAST and TRANSMISSION GEARBOX below the rotor — "
    "showing meshed gears, drive shaft; (5) the FUEL TANK in the lower "
    "fuselage; (6) the TAIL ROTOR drive shaft running along the tail "
    "boom. Each cutaway section reveals 3D internal detail in pencil "
    "shading. Subtle DASHED LINES connect cutaway windows to suggest "
    "you're seeing inside. "
    "\n\n"
    "CRITICAL composition: helicopter sits LOW on the canvas — the main "
    "rotor blades should be roughly at the VERTICAL CENTER (around 50% "
    "from the top), NOT at the very top. The body of the helicopter "
    "occupies the LOWER HALF (50-90% vertical). The TOP 35% of the "
    "canvas must stay MOSTLY EMPTY cream paper / soft sky (reserved for "
    "title text). No dense elements in the upper portion. Even the rotor "
    "blades should not reach near the top edge — leave airy space above. "
    "\n\n"
    "Style: graphite pencil on warm cream paper, visible pencil strokes, "
    "soft tonal shading, technical-illustration precision. Hatching "
    "and crosshatching for shadows. NO color, NO painterly textures, "
    "NO photographic elements, NO number labels, NO text labels. Match "
    "a vintage encyclopedia cutaway aesthetic — think the Stephen Biesty "
    "fire-truck cutaway elsewhere in this book. "
    "\n\n"
    "Landscape 1.5:1 (1536x1024). No text, no border, no frame, no "
    "watermark, no signature, no labels."
)


def main() -> None:
    out_dir = ROOT / "imagens" / "outpainted-breathe"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "aviao-08.png"

    print(f"→ generate Sikorsky CH-53 cutaway → {out_path.name}")
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
