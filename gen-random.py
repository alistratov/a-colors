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


def generate():
    target_distance = 0.7
    tolerance = 0.01
    found = None


    max_iter = 1_000_000
    for ps in range(max_iter):
        c1 = RGBDisplay(
            random.random(),
            random.random(),
            random.random(),
        )
        c2 = RGBDisplay(
            random.random(),
            random.random(),
            random.random(),
        )
        # hsv1 = rgb_to_hsv(c1)
        # hsv2 = rgb_to_hsv(c2)
        # hsv_dist = (hsv1.distance(hsv2))
        # if abs(hsv_dist - target_distance) <= tolerance:
        #     found = (c1, c2)
        #     break
        lab1 = rgb_to_lab76(c1)
        lab2 = rgb_to_lab76(c2)
        dist = (lab1.distance(lab2))
        if abs(dist - target_distance) <= tolerance:
            found = (c1, c2)
            break

    print(f"Found pair after {ps} tries with distance {dist:.4f}")
    print(f"Color 1: {found[0].to_8bit()}")
    print(f"Color 2: {found[1].to_8bit()}")


if __name__ == '__main__':
    generate()
