"""
Generate cards pairs.
"""
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
        # Suspicious ratings
        # (RGBDisplay.from_8bit(216, 191, 216), RGBDisplay.from_8bit(230, 230, 250)),
        # (RGBDisplay.from_8bit(0, 0, 128), RGBDisplay.from_8bit(15, 82, 186)),
        # (RGBDisplay.from_8bit(250, 128, 114), RGBDisplay.from_8bit(255, 160, 122)),
        # (RGBDisplay.from_8bit(203, 255, 0), RGBDisplay.from_8bit(244, 255, 204)),
        # (RGBDisplay.from_8bit(17, 178, 82), RGBDisplay.from_8bit(107, 178, 135)),
        # High stddev
        (RGBDisplay.from_8bit(192, 255, 0), RGBDisplay.from_8bit(255, 186, 0)),
        (RGBDisplay.from_8bit(178, 35, 121), RGBDisplay.from_8bit(178, 160, 171)),
        (RGBDisplay.from_8bit(128, 128, 0), RGBDisplay.from_8bit(154, 185, 115)),
        (RGBDisplay.from_8bit(76, 76, 76), RGBDisplay.from_8bit(178, 178, 178)),
        (RGBDisplay.from_8bit(51, 51, 51), RGBDisplay.from_8bit(204, 204, 204)),
        (RGBDisplay.from_8bit(40, 0, 204), RGBDisplay.from_8bit(155, 142, 204)),
    ]
    print("Total cards:", len(cards))

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

if __name__ == '__main__':
    generate()
