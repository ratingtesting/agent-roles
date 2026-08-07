#!/usr/bin/env python3
"""Center-crop a screenshot to habr/vc cover size (780x440).

Usage: python scripts/crop_cover.py <screenshot.png> [out.png]
Default out: <screenshot_dir>/cover.png

Used after browser_vision confirms the HTML cover renders cleanly.
"""
import sys
from pathlib import Path
from PIL import Image

TW, TH = 780, 440

def main():
    if len(sys.argv) < 2:
        print("usage: crop_cover.py <screenshot.png> [out.png]")
        sys.exit(1)
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else src.parent / "cover.png"
    im = Image.open(src).convert("RGB")
    w, h = im.size
    left = max(0, (w - TW) // 2)
    top = max(0, (h - TH) // 2)
    crop = im.crop((left, top, left + TW, top + TH))
    crop.save(out)
    print(f"saved {out} {crop.size} (orig {im.size})")

if __name__ == "__main__":
    main()
