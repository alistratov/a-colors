"""
Generate cards pairs.
"""
import random
import webbrowser
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from colors import RGBDisplay, HSV, HLS
from colors import (
    rgbd_to_rgbl,
    rgb_to_yiq,
    rgb_to_hsv,
    hsv_to_rgbd,
    hsv_to_rgbl,
    rgb_to_hls,
    hls_to_rgbd,
    hls_to_rgbl,
    rgb_to_lab76,
    rgb_to_lab2k,
)


def create_html(pairs) -> str:
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <title>Color pairs preview</title>
    <style>
    body {
      font-family: sans-serif;
      background: #f0f0f0;
      margin: 20px;
    }
    .pair {
      display: flex;
      align-items: center;
      margin-bottom: 8px;
    }
    .swatch {
      width: 120px;
      height: 60px;
      border: 1px solid #ccc;
    }
    .hex {
      width: 100px;
      text-align: center;
      margin: 0 8px;
      font-family: monospace;
    }
    </style>
    </head>
    <body>
    <h2>Color pairs</h2>
    """

    for i, (c1, c2) in enumerate(pairs, 1):
        html += f"""
    <div class="pair">
      <div class="swatch" style="background:{c1}"></div>
      <div class="hex">{c1}</div>
      <div class="swatch" style="background:{c2}"></div>
      <div class="hex">{c2}</div>
    </div>
    """
    html += "</body></html>"
    return html


def generate():
    cards = [
        # Identical yellow
        (RGBDisplay.from_8bit(255, 215, 0), RGBDisplay.from_8bit(255, 215, 0)),
        # Identical brown
        (RGBDisplay.from_8bit(150, 70, 0), RGBDisplay.from_8bit(150, 70, 0)),
        # Identical green
        (RGBDisplay.from_8bit(20, 150, 10), RGBDisplay.from_8bit(20, 150, 10)),
        # Black and White
        (RGBDisplay.from_8bit(0, 0, 0), RGBDisplay.from_8bit(255, 255, 255)),
        # Red and Cyan
        (RGBDisplay.from_8bit(255, 0, 0), RGBDisplay.from_8bit(0, 255, 255)),
        # UA Blue and Yellow
        (RGBDisplay.from_8bit(0, 87, 183), RGBDisplay.from_8bit(255, 215, 0)),
        # Grays
        (RGBDisplay(0.1, 0.1, 0.1), RGBDisplay(0.9, 0.9, 0.9)),
        (RGBDisplay(0.2, 0.2, 0.2), RGBDisplay(0.8, 0.8, 0.8)),
        (RGBDisplay(0.3, 0.3, 0.3), RGBDisplay(0.7, 0.7, 0.7)),
        (RGBDisplay(0.4, 0.4, 0.4), RGBDisplay(0.6, 0.6, 0.6)),
        # International Klein Blue and St. Patrick's blue
        (RGBDisplay.from_8bit(0, 47, 167), RGBDisplay.from_8bit(0, 0, 92)),
        # Fuchsia and Phlox
        (RGBDisplay.from_8bit(255, 0, 255), RGBDisplay.from_8bit(223, 0, 255)),
        # Cardinal and Heliotrope
        (RGBDisplay.from_8bit(196, 30, 58), RGBDisplay.from_8bit(223, 115, 255)),
        # Khaki and Dark Khaki
        (RGBDisplay.from_8bit(195, 176, 145), RGBDisplay.from_8bit(189, 183, 107)),
        # Olive and Olivine
        (RGBDisplay.from_8bit(128, 128, 0), RGBDisplay.from_8bit(154, 185, 115)),
        # Turquoise and Light green
        (RGBDisplay.from_8bit(64, 224, 208), RGBDisplay.from_8bit(153, 255, 153)),
        # Coral and Rust
        (RGBDisplay.from_8bit(255, 127, 80), RGBDisplay.from_8bit(183, 65, 14)),
        # Brown and Tan
        (RGBDisplay.from_8bit(150, 75, 0), RGBDisplay.from_8bit(210, 180, 140)),
        # Navy and Sapphire
        (RGBDisplay.from_8bit(0, 0, 128), RGBDisplay.from_8bit(15, 82, 186)),
        # Cosmic latte and Cream
        (RGBDisplay.from_8bit(255, 248, 231), RGBDisplay.from_8bit(255, 253, 208)),
        # Mint and Mint cream
        (RGBDisplay.from_8bit(189, 252, 201), RGBDisplay.from_8bit(245, 255, 250)),
        # Lavender and Thistle
        (RGBDisplay.from_8bit(230, 230, 250), RGBDisplay.from_8bit(216, 191, 216)),
        # Salmon and Light salmon
        (RGBDisplay.from_8bit(250, 128, 114), RGBDisplay.from_8bit(255, 160, 122)),
        # Cold and Ochre
        (RGBDisplay.from_8bit(255, 215, 0), RGBDisplay.from_8bit(204, 119, 34)),
        # Lime and Selective yellow
        (RGBDisplay.from_8bit(192, 255, 0), RGBDisplay.from_8bit(255, 186, 0)),
        # HSV
        # Different hue, same saturation and value
        (
            hsv_to_rgbd(HSV(0.0, 1.0, 1.0)),
            hsv_to_rgbd(HSV(0.5, 1.0, 1.0)),
        ),
        (
            hsv_to_rgbd(HSV(0.0, 0.5, 1.0)),
            hsv_to_rgbd(HSV(0.3, 0.5, 1.0)),
        ),
        (
            hsv_to_rgbd(HSV(0.6, 0.8, 0.9)),
            hsv_to_rgbd(HSV(0.9, 0.8, 0.9)),
        ),
        # Different saturation, same hue and value
        (
            hsv_to_rgbd(HSV(0.2, 1.0, 1.0)),
            hsv_to_rgbd(HSV(0.2, 0.2, 1.0)),
        ),
        (
            hsv_to_rgbd(HSV(0.7, 1.0, 0.8)),
            hsv_to_rgbd(HSV(0.7, 0.3, 0.8)),
        ),
        (
            hsv_to_rgbd(HSV(0.4, 0.9, 0.7)),
            hsv_to_rgbd(HSV(0.4, 0.4, 0.7)),
        ),
        (hsv_to_rgbd(HSV(0.55, 0.2, 0.8)), hsv_to_rgbd(HSV(0.55, 1.0, 0.8))),
        (hsv_to_rgbd(HSV(0.9, 0.1, 0.7)), hsv_to_rgbd(HSV(0.9, 0.8, 0.7))),
        # Different value, same hue and saturation
        (
            hsv_to_rgbd(HSV(0.4, 1.0, 1.0)),
            hsv_to_rgbd(HSV(0.4, 1.0, 0.3)),
        ),
        (
            hsv_to_rgbd(HSV(0.9, 0.8, 0.9)),
            hsv_to_rgbd(HSV(0.9, 0.8, 0.4)),
        ),
        (
            hsv_to_rgbd(HSV(0.1, 0.7, 0.8)),
            hsv_to_rgbd(HSV(0.1, 0.7, 0.2)),
        ),
        (hsv_to_rgbd(HSV(0.1, 0.8, 0.9)), hsv_to_rgbd(HSV(0.1, 0.8, 0.5))),
        (hsv_to_rgbd(HSV(0.6, 0.6, 0.9)), hsv_to_rgbd(HSV(0.6, 0.6, 0.4))),
        # HSV all different
        (hsv_to_rgbd(HSV(0.1, 0.9, 0.8)), hsv_to_rgbd(HSV(0.3, 0.5, 0.6))),
        (hsv_to_rgbd(HSV(0.6, 0.4, 0.5)), hsv_to_rgbd(HSV(0.9, 0.8, 0.9))),
        # Close
        (RGBDisplay.from_8bit(120, 120, 120), RGBDisplay.from_8bit(130, 130, 130)),
        (RGBDisplay.from_8bit(240, 240, 230), RGBDisplay.from_8bit(250, 250, 240)),
        # ...
        # RGB distance 0.86
        (RGBDisplay(0.0, 0.1, 0.0), RGBDisplay(0.9, 1.0, 0.9)),
        # HSV distance 0.85
        (hsv_to_rgbd(HSV(0.2, 0.07, 0.07)), hsv_to_rgbd(HSV(0.7, 0.9, 0.9))),
        # HSV distance 0.75
        (RGBDisplay.from_8bit(73, 72, 84), RGBDisplay.from_8bit(171, 246, 13)),
        # Lab76 distance 0.89
        (RGBDisplay.from_8bit(26, 240, 0), RGBDisplay.from_8bit(11, 9, 242)),
        # Lab76 distance 0.8
        # (RGBDisplay.from_8bit(101, 5, 239), RGBDisplay.from_8bit(31, 211, 14)),
        (RGBDisplay.from_8bit(203, 0, 214), RGBDisplay.from_8bit(7, 235, 29)),
        # Lab76 distance 0.7
        (RGBDisplay.from_8bit(185, 134, 2), RGBDisplay.from_8bit(73, 4, 228)),
    ]
    print("Total cards:", len(cards))
    # for idx, (color1, color2) in enumerate(cards):
    #     print("%02d: %s  <->  %s" % (idx + 1, color1.to_hex(), color2.to_hex()))

    # Analyze distances
    rgb_dist = []
    hsv_dist = []
    lab76_dist = []
    for color1, color2 in cards:
        rgbl1 = rgbd_to_rgbl(color1)
        rgbl2 = rgbd_to_rgbl(color2)
        rgb_dist.append(rgbl1.distance(rgbl2))

        hsv1 = rgb_to_hsv(color1)
        hsv2 = rgb_to_hsv(color2)
        hsv_dist.append(hsv1.distance(hsv2))

        lab76_1 = rgb_to_lab76(color1)
        lab76_2 = rgb_to_lab76(color2)
        lab76_dist.append(lab76_1.distance(lab76_2))

    # Show distance stats
    # print(lab76_dist)
    # plt.figure(figsize=(8,4))
    # plt.hist(rgb_dist, bins=200, alpha=0.5, label='RGB-L', density=True)
    # plt.hist(hsv_dist, bins=200, alpha=0.5, label='HSV', density=True)
    # plt.hist(lab76_dist, bins=200, alpha=0.5, label='Lab76', density=True)
    # plt.legend()
    # plt.xlabel("Distance / ΔE")
    # plt.ylabel("Density")
    # plt.title("Distribution of color distances for random color pairs")
    # plt.grid(alpha=0.3)
    # plt.tight_layout()
    # plt.show()

    # Write to temporary HTML and open in browser
    def write_to_html():
        html = create_html([(c1.to_hex(), c2.to_hex()) for c1, c2 in cards])
        with tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".html", encoding="utf-8"
        ) as f:
            f.write(html)
            temp_html_path = Path(f.name)
            webbrowser.open_new_tab(temp_html_path.as_uri())
    write_to_html()

    def write_to_js():
        js_lines = []
        js_lines.append("const PREDEFINED = [")
        for c1, c2 in cards:
            js_lines.append(f"  ['{c1.to_hex()}', '{c2.to_hex()}'],")
        js_lines.append("];")
        js_code = "\n".join(js_lines)
        with tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".js", encoding="utf-8"
        ) as f:
            f.write(js_code)
            temp_js_path = Path(f.name)
            webbrowser.open_new_tab(temp_js_path.as_uri())
    # write_to_js()

if __name__ == '__main__':
    generate()
