#!/usr/bin/env python3
"""Andy versão CARTOONIZADA — ainda lápis grafite mas com proporções
estilizadas (cabeça maior, simplificações), vibe children's book
illustration ao invés de portrait realista.

Uso:
    python gerar_andy_cartoon.py [variante]   # variante = a | b | c | all
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
ENV = dotenv_values(ROOT / ".env")
API_KEY = ENV.get("OPENAPI_KEY") or ENV.get("OPENAI_API_KEY")
if not API_KEY:
    sys.exit("Falta OPENAPI_KEY no .env")

client = OpenAI(api_key=API_KEY)

# Núcleo comum — descreve o Andy
ANDY_LOOK = (
    "Andy is a 5-6 year old boy with tousled brown hair under a soft "
    "newsboy/flat cap, light freckles across the nose, big curious eyes, "
    "a small smudge of grease on one cheek, a hint of a friendly smile. "
    "He wears classic vintage 1940s mechanic outfit: denim bib overalls "
    "over a buttoned shirt with sleeves rolled to the elbows. He holds a "
    "big chunky wrench that's almost too big for him (adds charm). Sturdy "
    "little work boots. Standing full body, slight 3/4 angle, weight on "
    "one leg, wrench casually on his shoulder. White paper background."
)

VARIANTS = {
    # A — clean illustrative cartoon: proporções de criança "cartoon", cabeça
    # maior, traços simples mas ainda em lápis (não vetorial)
    "a": (
        "A pencil-drawn ILLUSTRATIVE CARTOON character of a young boy named "
        "Andy, in the style of a modern children's picture book. Drawn with "
        "graphite pencil on warm white paper — visible pencil strokes and "
        "soft shading — but with STYLIZED PROPORTIONS: head slightly larger "
        "than realistic (about 1/5 of body height), eyes a bit bigger and "
        "rounder than realistic, simplified anatomy, smooth flowing contours "
        "(not photographic). Friendly, charming, picture-book quality — "
        "think Quentin Blake meets a graphite pencil. NOT photorealistic, "
        "NOT line-art coloring page, NOT flat cartoon vector. Hand-drawn "
        "feel preserved. " + ANDY_LOOK
    ),

    # B — chibi-ish: mais "fofo", cabeça bem maior, corpo menorzinho
    "b": (
        "A pencil-drawn CHIBI / CUTE CHARACTER illustration of a young boy "
        "named Andy. Drawn with graphite pencil on warm white paper "
        "(visible pencil strokes, soft shading), but with CUTE STYLIZED "
        "PROPORTIONS: head is large relative to body (about 1/4 of total "
        "height, almost chibi-like), big round eyes, soft round cheeks, "
        "short stubby limbs, very child-like and adorable. Simplified "
        "features. The pencil texture and hand-drawn feel are preserved — "
        "this is NOT digital cartoon, NOT vector, NOT photorealistic. "
        "Think a Studio Ghibli child re-drawn in graphite. " + ANDY_LOOK
    ),

    # C — meio do caminho: realista MAS com estilização infantil
    "c": (
        "A pencil drawing of a young boy named Andy with a SOFTLY STYLIZED, "
        "STORYBOOK QUALITY. Realistic enough to feel like a true pencil "
        "illustration (graphite on warm white paper, visible strokes, "
        "tonal shading), but with the gentle stylization of a children's "
        "book character: slightly larger eyes than photo-real, smoother "
        "and rounder face, simpler features, expressive rather than "
        "anatomically exact. Between portrait realism and children's "
        "illustration — leans toward illustration. NOT cartoon flat. NOT "
        "photorealistic. Hand-drawn pencil feel essential. " + ANDY_LOOK
    ),
}


def generate(variant_key: str) -> Path:
    prompt = VARIANTS[variant_key]
    print(f"→ andy-cartoon-{variant_key}")
    resp = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1536",
        quality="high",
        n=1,
    )
    b64 = resp.data[0].b64_json
    if not b64:
        sys.exit("Sem b64_json")
    out_dir = ROOT / "imagens" / "andy"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"andy-cartoon-{variant_key}.png"
    out_path.write_bytes(base64.b64decode(b64))
    print(f"✓ {out_path.name} ({out_path.stat().st_size // 1024} KB)")
    return out_path


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    if arg == "all":
        for k in VARIANTS:
            generate(k)
    elif arg in VARIANTS:
        generate(arg)
    else:
        sys.exit(f"Variante inválida: {arg}. Use: {' | '.join(VARIANTS)} ou all")


if __name__ == "__main__":
    main()
