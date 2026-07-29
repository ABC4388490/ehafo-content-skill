#!/usr/bin/env python3
"""Reject Remotion information graphics with excessive empty vertical space."""

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


def inspect(path: Path, threshold: int) -> dict[str, float | int | str]:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    background = background_from_corners(image)

    rows: list[int] = []
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            if max(abs(pixel[i] - background[i]) for i in range(3)) >= threshold:
                rows.append(y)
                break

    if not rows:
        raise ValueError("未检测到有效内容")

    top = min(rows)
    bottom = max(rows)
    return {
        "file": str(path),
        "width": width,
        "height": height,
        "content_height_ratio": (bottom - top + 1) / height,
        "top_blank_ratio": top / height,
        "bottom_blank_ratio": (height - 1 - bottom) / height,
        "bottom_blank_px": height - 1 - bottom,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument("--threshold", type=int, default=20)
    parser.add_argument("--min-content-height", type=float, default=0.72)
    parser.add_argument("--max-top-blank", type=float, default=0.15)
    parser.add_argument("--max-bottom-blank", type=float, default=0.08)
    parser.add_argument("--max-bottom-blank-px", type=int, default=48)
    args = parser.parse_args()

    failed = False
    for path in args.images:
        try:
            result = inspect(path, args.threshold)
        except (OSError, ValueError) as error:
            print(f"FAIL {path}: {error}")
            failed = True
            continue

        reasons = []
        if result["content_height_ratio"] < args.min_content_height:
            reasons.append("有效内容纵向占比不足")
        if result["top_blank_ratio"] > args.max_top_blank:
            reasons.append("顶部空白过多")
        if result["bottom_blank_ratio"] > args.max_bottom_blank:
            reasons.append("底部空白过多")
        if result["bottom_blank_px"] > args.max_bottom_blank_px:
            reasons.append("底部空白像素过多")

        status = "FAIL" if reasons else "PASS"
        print(
            f"{status} {path}: "
            f"content={result['content_height_ratio']:.1%}, "
            f"top={result['top_blank_ratio']:.1%}, "
            f"bottom={result['bottom_blank_ratio']:.1%} "
            f"({result['bottom_blank_px']}px)"
            + (f"；{'；'.join(reasons)}" if reasons else "")
        )
        failed = failed or bool(reasons)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
