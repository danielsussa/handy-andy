#!/usr/bin/env python3
"""Gera metadata cronológica + narrativa conectada pra todas as páginas do
livro usando GPT-4o (vision) + GPT-4.

Pipeline:
1. Vision: vê cada imagem, identifica modelo/país/ano
2. Sort por ano
3. Narrativa: escreve body conectado contando a evolução das máquinas

Output: livro/pages.json (id, title, sub, body, year, quote opcional)
"""
from __future__ import annotations

import base64
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
ENV = dotenv_values(ROOT / ".env")
API_KEY = ENV.get("OPENAPI_KEY") or ENV.get("OPENAI_API_KEY")
if not API_KEY:
    raise SystemExit("Falta OPENAPI_KEY no .env")

client = OpenAI(api_key=API_KEY)

# Páginas a processar — id + path da melhor versão (tritone-andy-scene se tiver,
# tritone-duo se for merge, senão tritone-breathe). Paleta sepia como ref.
PAGES = [
    # Tanques
    {"id": "tanque-02", "path": "imagens/tritone-breathe/sepia/tanque-02.png", "hint": "Tank from curadoria notes: possibly T-34 USSR 1940"},
    {"id": "tanque-06", "path": "imagens/tritone-breathe/sepia/tanque-06.png", "hint": "Tank"},
    # Caminhões
    {"id": "caminhao-02", "path": "imagens/tritone-andy-scene/sepia/caminhao-02.png", "hint": "Dodge Power Wagon, USA ~1946"},
    {"id": "caminhao-11", "path": "imagens/tritone-breathe/sepia/caminhao-11.png", "hint": "ZIL truck, USSR"},
    {"id": "caminhao-14", "path": "imagens/tritone-breathe/sepia/caminhao-14.png", "hint": "Chevy truck"},
    {"id": "caminhao-21", "path": "imagens/tritone-breathe/sepia/caminhao-21.png", "hint": "Chevy Silverado, USA"},
    # Motos
    {"id": "moto-04", "path": "imagens/tritone-andy-scene/sepia/moto-04.png", "hint": "Cafe Racer motorcycle"},
    {"id": "moto-14", "path": "imagens/tritone-breathe/sepia/moto-14.png", "hint": "Harley custom"},
    {"id": "moto-17", "path": "imagens/tritone-breathe/sepia/moto-17.png", "hint": "Harley Road King"},
    # Aviões
    {"id": "aviao-turbina", "path": "imagens/tritone-duo/sepia/aviao-turbina.png", "hint": "Airbus A320 + jet turbine cutaway (Europa 1988)"},
    {"id": "aviao-02", "path": "imagens/tritone-breathe/sepia/aviao-02.png", "hint": "Cessna 172, USA ~1956"},
    {"id": "aviao-05", "path": "imagens/tritone-breathe/sepia/aviao-05.png", "hint": "Focke-Wulf Fw 190, Germany WW2 ~1941"},
    {"id": "aviao-08", "path": "imagens/tritone-breathe/sepia/aviao-08.png", "hint": "helicopter"},
    {"id": "aviao-12", "path": "imagens/tritone-breathe/sepia/aviao-12.png", "hint": "Boeing 747"},
    # Tratores
    {"id": "trator-01", "path": "imagens/tritone-breathe/sepia/trator-01.png", "hint": "T-150 tractor, USSR Kharkov 1976"},
    {"id": "trator-cuts", "path": "imagens/tritone-duo/sepia/trator-cuts.png", "hint": "Oliver tractor cutaway + exploded view"},
    {"id": "trator-engine", "path": "imagens/tritone-duo/sepia/trator-engine.png", "hint": "vintage tractor + engine cutaway"},
    # Bombeiros
    {"id": "bombeiro-cut", "path": "imagens/tritone-andy-scene/sepia/bombeiro-cut.png", "hint": "Stephen Biesty fire truck cutaway"},
    {"id": "bombeiro2-02", "path": "imagens/tritone-breathe/sepia/bombeiro2-02.png", "hint": "Ural fire truck Pripyat USSR 1986"},
    # Polícia
    {"id": "policia-07", "path": "imagens/tritone-breathe/sepia/policia-07.png", "hint": "Dodge Diplomat 1980s USA police"},
    # Guindastes
    {"id": "guindaste-01", "path": "imagens/tritone-breathe/sepia/guindaste-01.png", "hint": "Titanus V-Max crane"},
    {"id": "guindaste-02", "path": "imagens/tritone-breathe/sepia/guindaste-02.png", "hint": "3D crane"},
    # Escavadeiras
    {"id": "escavadeira", "path": "imagens/tritone-breathe/sepia/escavadeira.png", "hint": "excavator sketch"},
    {"id": "caminhao-17", "path": "imagens/tritone-breathe/sepia/caminhao-17.png", "hint": "excavator pencil"},
    # Motor
    {"id": "motor-v8-cut", "path": "imagens/tritone-andy-scene/sepia/motor-v8-cut.png", "hint": "V8 engine blueprint cutaway"},
    # Trens (adicionados)
    {"id": "trem-vapor", "path": "imagens/tritone-trem/sepia/trem-vapor.png", "hint": "steam locomotive vintage ~1880s-1900s"},
    {"id": "trem-moderno", "path": "imagens/tritone-trem/sepia/trem-moderno.png", "hint": "modern high-speed electric train ~2000s"},
    {"id": "trem-corte", "path": "imagens/tritone-trem/sepia/trem-corte.png", "hint": "steam train cutaway ~1900s"},
    # Andy de despedida (sempre por último, year=9999 pra ficar no fim)
    {"id": "andy-fim", "path": "imagens/tritone-trem/sepia/andy-fim.png", "hint": "Andy mascot waving farewell — ALWAYS LAST PAGE, year=9999"},
]


def b64_image(path: Path) -> str:
    with path.open("rb") as f:
        return base64.b64encode(f.read()).decode()


def identify(page: dict) -> dict:
    """GPT-4o vision identifica modelo, país, ano."""
    img_path = ROOT / page["path"]
    if not img_path.exists():
        return {**page, "model": "unknown", "country": "unknown", "year": 2000, "year_note": "image not found"}

    prompt = (
        "You are looking at a pencil illustration of a vehicle/machine for a children's book. "
        "Identify it as precisely as possible. Use the hint provided but VERIFY with the image. "
        f"\n\nHint: {page.get('hint', 'none')}"
        "\n\nRespond ONLY with strict JSON:"
        '{"model": "<name>", "country": "<country>", "year": <introduction or relevant year as integer>, "year_note": "<brief why this year>"}'
        '\n\nIf the image shows a cutaway/diagram, give the year of the original machine type.'
        '\nIf truly unidentifiable, guess plausibly based on style and respond with your best estimate.'
    )

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image(img_path)}", "detail": "low"}},
            ],
        }],
        max_tokens=200,
        temperature=0.3,
    )
    raw = resp.choices[0].message.content.strip()
    # Strip markdown json fence se houver
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print(f"!  {page['id']}: JSON inválido: {raw[:100]}", file=sys.stderr)
        return {**page, "model": "?", "country": "?", "year": 2000, "year_note": "parse error"}
    print(f"✓ {page['id']:30s} {data.get('model','?')[:30]:30s} {data.get('year','?')}")
    return {**page, **data}


def narrate(items: list[dict]) -> list[dict]:
    """GPT-4 escreve a narrativa conectada com os items em ordem cronológica."""
    items_summary = "\n".join(
        f'{i+1}. {it["id"]} — {it["model"]} ({it["country"]}, {it["year"]}) [{it.get("hint","")}]'
        for i, it in enumerate(items)
    )
    prompt = (
        "You are writing the body text for each page of a children's picture book called "
        "'Handy Andy and the Big Machines'. The book is in ENGLISH. "
        "The pages are ordered CHRONOLOGICALLY — from oldest machine to newest — to tell the "
        "EVOLUTION OF MACHINES as a connected story.\n\n"
        "For each page, write:\n"
        "- title: short uppercase-friendly title in English (e.g., 'T-34 Tank', 'Steam Locomotive')\n"
        "- sub: 'Country · year' format (e.g., 'Soviet Union · 1940')\n"
        "- body: 2-3 short sentences in English, child-appropriate but with real history. "
        "EACH body should CONNECT with the previous/next entries when natural — referencing 'before', "
        "'after', 'around the same time', 'while', etc. Build a sense of progression. "
        "Keep tight (~40-60 words).\n"
        "- quote: OPTIONAL short italic-style poetic one-liner in English. Include only on truly "
        "iconic pages (3-5 across the book max).\n\n"
        "SPECIAL CASE — 'andy-fim': this is the FAREWELL page (last page). Title 'Goodbye for Now' "
        "or similar. Body: short heartfelt wrap-up referencing how machines change but the spirit "
        "of building/fixing stays. ~30 words.\n\n"
        f"The pages in chronological order:\n{items_summary}\n\n"
        "Respond ONLY with strict JSON array, one object per page, in the SAME ORDER as the input:\n"
        '[{"id": "...", "title": "...", "sub": "...", "body": "...", "quote": "..." or null}, ...]'
    )
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
        temperature=0.7,
    )
    raw = resp.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1].lstrip("json").strip()
    return json.loads(raw)


def main() -> None:
    print(f"Identificando {len(PAGES)} páginas via GPT-4o vision...\n")
    with ThreadPoolExecutor(max_workers=8) as pool:
        identified = list(pool.map(identify, PAGES))
    identified.sort(key=lambda x: x.get("year", 9999))
    print(f"\nOrdenado por ano. Range: {identified[0].get('year')} → {identified[-1].get('year')}")
    print(f"\nGerando narrativa conectada via GPT-4o...\n")
    narrated = narrate(identified)
    # Merge: usar year de identified, conteúdo de narrated
    final = []
    by_id = {n["id"]: n for n in narrated}
    for it in identified:
        n = by_id.get(it["id"], {})
        final.append({
            "id": it["id"],
            "year": it["year"],
            "title": n.get("title", it["model"]),
            "sub": n.get("sub", f'{it["country"]} · {it["year"]}'),
            "body": n.get("body", ""),
            "quote": n.get("quote"),
        })
    out_path = ROOT / "livro" / "pages.json"
    out_path.write_text(json.dumps(final, ensure_ascii=False, indent=2))
    print(f"\n✓ {out_path} ({len(final)} páginas)")


if __name__ == "__main__":
    main()
