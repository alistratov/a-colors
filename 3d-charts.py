import random

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

def generate():
    for x in range(256):
        for y in range(256):
            for z in range(256):
                rgbd = RGBDisplay.from_8bit(x, y, z)


    plt.show()


if __name__ == '__main__':
    generate()
