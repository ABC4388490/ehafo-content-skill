#!/usr/bin/env python3
"""Reject article images whose meaningful content is too narrow for WeChat body display."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image


def background_from_corners(image: Image.Image) -> tuple[int, int, int]:
    width, height = image.size
    points = (
        image.getpixel((0, 0)),
        image.getpixel((width - 1, 0)),
        image.getpixel((0, height - 1)),
        image.getpixel((width - 1, height - 1)),
    )
    return tuple(sorted(point[channel] for point in points)[1] for channel in range(3))


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    index = round((len(ordered) - 1) * quantile)
    return ordered[index]


def inspect(path: Path, threshold: int, row_quantile: float) -> dict[str, float | int | str]:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    background = background_from_corners(image)
    pixels = image.load()
    row_spans: list[float] = []

    for y in range(height):
        active = [
            x
            for x in range(width)
            if max(abs(pixels[x, y][channel] - background[channel]) for channel in range(3))
            >= threshold
        ]
        if active:
            row_spans.append((max(active) - min(active) + 1) / width)

    if not row_spans:
        raise ValueError("未检测到有效内容")

    return {
        "file": str(path),
        "width": width,
        "height": height,
        "effective_width_ratio": percentile(row_spans, row_quantile),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument("--threshold", type=int, default=20)
    parser.add_argument("--row-quantile", type=float, default=0.90)
    parser.add_argument("--min-effective-width", type=float, default=0.75)
    parser.add_argument("--viewport-width", type=int, default=390)
    args = parser.parse_args()

    failed = False
    for path in args.images:
        try:
            result = inspect(path, args.threshold, args.row_quantile)
        except (OSError, ValueError) as error:
            print(f"FAIL {path}: {error}")
            failed = True
            continue

        ratio = float(result["effective_width_ratio"])
        projected_width = ratio * args.viewport_width
        reasons = []
        if ratio < args.min_effective_width:
            reasons.append("典型有效行横向内容占比不足")

        status = "FAIL" if reasons else "PASS"
        print(
            f"{status} {path}: "
            f"effective_width={ratio:.1%}, "
            f"projected_content={projected_width:.0f}px/{args.viewport_width}px"
            + (f"；{'；'.join(reasons)}" if reasons else "")
        )
        failed = failed or bool(reasons)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
