#!/usr/bin/env python3
"""Alinha a versão colorida (AI vintage) com o original (lápis) via
feature matching SIFT + homography. Resultado: a colorização "encaixa"
nas linhas do lápis, o overlay multiply fica nítido.
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent


def align(color_path: Path, ref_path: Path, output_path: Path) -> None:
    color = cv2.imread(str(color_path), cv2.IMREAD_COLOR)
    ref = cv2.imread(str(ref_path), cv2.IMREAD_COLOR)
    if color is None or ref is None:
        sys.exit(f"Falha ao abrir: {color_path} ou {ref_path}")
    h, w = ref.shape[:2]
    if color.shape[:2] != (h, w):
        color = cv2.resize(color, (w, h), interpolation=cv2.INTER_LANCZOS4)

    color_g = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
    ref_g = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create(nfeatures=5000)
    kp1, des1 = sift.detectAndCompute(ref_g, None)
    kp2, des2 = sift.detectAndCompute(color_g, None)
    print(f"Features detectadas: ref={len(kp1)} color={len(kp2)}")

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des2, des1, k=2)
    good = []
    for pair in matches:
        if len(pair) < 2:
            continue
        m, n = pair
        if m.distance < 0.75 * n.distance:
            good.append(m)
    print(f"Matches bons (Lowe ratio 0.75): {len(good)}")
    if len(good) < 12:
        sys.exit("Matches insuficientes — alinhamento não confiável.")

    src = np.float32([kp2[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst = np.float32([kp1[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    inliers = int(mask.sum()) if mask is not None else 0
    print(f"Inliers RANSAC: {inliers}/{len(good)}")

    aligned = cv2.warpPerspective(color, H, (w, h), flags=cv2.INTER_LANCZOS4)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), aligned)
    print(f"✓ {output_path.name} ({output_path.stat().st_size // 1024} KB)")


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit("Uso: align.py <color.png> <reference_orig.png>")
    color_path = Path(sys.argv[1])
    ref_path = Path(sys.argv[2])
    if not color_path.is_absolute():
        color_path = ROOT / color_path
    if not ref_path.is_absolute():
        ref_path = ROOT / ref_path
    out_dir = ROOT / "imagens" / "vintage-aligned"
    output_path = out_dir / color_path.name
    align(color_path, ref_path, output_path)


if __name__ == "__main__":
    main()
