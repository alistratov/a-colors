"""
Generate cards pairs.
"""
import random
import webbrowser
import tempfile
from pathlib import Path

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
        # Black and White
        (RGBDisplay.from_8bit(0, 0, 0), RGBDisplay.from_8bit(255, 255, 255)),
        # Red and Cyan
        (RGBDisplay.from_8bit(255, 0, 0), RGBDisplay.from_8bit(0, 255, 255)),
        # UA Blue and Yellow
        (RGBDisplay.from_8bit(0, 87, 183), RGBDisplay.from_8bit(255, 215, 0)),
    ]
    print("Total cards:", len(cards))
    # for idx, (color1, color2) in enumerate(cards):
    #     print("%02d: %s  <->  %s" % (idx + 1, color1.to_hex(), color2.to_hex()))

    html = create_html([(c1.to_hex(), c2.to_hex()) for c1, c2 in cards])
    with tempfile.NamedTemporaryFile(
        "w", delete=False, suffix=".html", encoding="utf-8"
    ) as f:
        f.write(html)
        temp_html_path = Path(f.name)
        webbrowser.open_new_tab(temp_html_path.as_uri())


if __name__ == '__main__':
    generate()
