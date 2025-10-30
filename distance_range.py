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

"""
N = 10_000_000
RGBD Distance Stats:Min: 0.000, Max: 1.000, Avg: 0.382, StdDev: 0.144, Mean: 0.382, Skew: 0.000, ExcessKurtosis: -0.503
RGBL Distance Stats:Min: 0.000, Max: 1.000, Avg: 0.381, StdDev: 0.161, Mean: 0.381, Skew: 0.000, ExcessKurtosis: -0.627
Lab76 Distance Stats:Min: 0.000, Max: 258.683, Avg: 65.370, StdDev: 34.405, Mean: 65.370, Skew: 0.000, ExcessKurtosis: 0.348
Lab2k Distance Stats:Min: 0.000, Max: 128.299, Avg: 40.853, StdDev: 22.157, Mean: 40.853, Skew: 0.000, ExcessKurtosis: 0.109
HSV Distance Stats:Min: 0.000, Max: 0.866, Avg: 0.280, StdDev: 0.108, Mean: 0.280, Skew: 0.000, ExcessKurtosis: -0.171
HLS Distance Stats:Min: 0.000, Max: 0.866, Avg: 0.267, StdDev: 0.102, Mean: 0.267, Skew: 0.000, ExcessKurtosis: -0.115
YIQ Distance Stats:Min: 0.000, Max: 0.726, Avg: 0.258, StdDev: 0.106, Mean: 0.258, Skew: 0.000, ExcessKurtosis: -0.388
"""


def generate():
    rgbd_values = []
    rgbl_values = []
    lab76_values = []
    lab76l_values = []
    lab2k_values = []
    lab2kl_values = []
    hsv_values = []
    # hsvl_values = []
    hls_values = []
    # hlsl_values = []
    # yiq_values = []

    def measure(a, b):
        d_rgbd = a.distance(b)
        rgbd_values.append(d_rgbd)

        al = rgbd_to_rgbl(a)
        bl = rgbd_to_rgbl(b)

        d_rgbl = al.distance(bl)
        rgbl_values.append(d_rgbl)

        # Lab
        d_lab76 = rgb_to_lab76(a).distance(rgb_to_lab76(b))
        lab76_values.append(d_lab76)
        d_lab76l = rgb_to_lab76(al).distance(rgb_to_lab76(bl))
        lab76l_values.append(d_lab76l)

        d_lab2k = rgb_to_lab2k(a).distance(rgb_to_lab2k(b))
        lab2k_values.append(d_lab2k)
        d_lab2kl = rgb_to_lab2k(al).distance(rgb_to_lab2k(bl))
        lab2kl_values.append(d_lab2kl)

        # HSV, HSL
        d_hsv = rgb_to_hsv(a).distance(rgb_to_hsv(b))
        hsv_values.append(d_hsv)
        # d_hsvl = rgb_to_hsv(al).distance(rgb_to_hsv(bl))
        # hsvl_values.append(d_hsvl)

        d_hls = rgb_to_hls(a).distance(rgb_to_hls(b))
        hls_values.append(d_hls)
        # d_hlsl = rgb_to_hls(al).distance(rgb_to_hls(bl))
        # hlsl_values.append(d_hlsl)

        # d_yiq = rgb_to_yiq(a).distance(rgb_to_yiq(b))
        # yiq_values.append(d_yiq)

    # Same colors
    measure(RGBDisplay(0.0, 0.0, 0.0), RGBDisplay(0.0, 0.0, 0.0))
    measure(RGBDisplay(1.0, 1.0, 1.0), RGBDisplay(1.0, 1.0, 1.0))

    # Black and white
    measure(RGBDisplay(0.0, 0.0, 0.0), RGBDisplay(1.0, 1.0, 1.0))
    measure(RGBDisplay(1.0, 1.0, 1.0), RGBDisplay(0.0, 0.0, 0.0))

    # Primary colors
    measure(RGBDisplay(1.0, 0.0, 0.0), RGBDisplay(0.0, 1.0, 0.0))
    measure(RGBDisplay(0.0, 1.0, 0.0), RGBDisplay(0.0, 0.0, 1.0))

    # Opposite hue but same lightness and saturation
    # measure(RGBDisplay(1.0, 0.0, 0.0), RGBDisplay(0.0, 1.0, 1.0))
    # measure(RGBDisplay(0.0, 1.0, 0.0), RGBDisplay(1.0, 0.0, 1.0))
    # measure(RGBDisplay(0.0, 0.0, 1.0), RGBDisplay(1.0, 1.0, 0.0))
    measure(hsv_to_rgbl(HSV(0.0, 1.0, 1.0)), hsv_to_rgbl(HSV(0.5, 0.0, 0.0)))
    measure(hls_to_rgbl(HLS(0.0, 0.0, 0.0)), hls_to_rgbl(HLS(0.5, 0.0, 0.0)))
    hsv_values.append(HSV(0.0, 1.0, 1.0).distance(HSV(0.5, 0.0, 0.0)))
    hls_values.append(HLS(0.0, 1.0, 1.0).distance(HLS(0.5, 0.0, 0.0)))

    # Very close colors
    measure(RGBDisplay(0.5, 0.5, 0.5), RGBDisplay(0.5001, 0.5001, 0.5001))
    measure(RGBDisplay(0.2, 0.3, 0.4), RGBDisplay(0.2001, 0.3001, 0.4001))

    # And random
    passes = 100_000
    for npass in range(passes):
        if npass % 10_000 == 0:
            print(f"Percent complete: {npass / passes:.2%}", end='\r')

        a = RGBDisplay(
            random.uniform(0.0, 1.0),
            random.uniform(0.0, 1.0),
            random.uniform(0.0, 1.0),
        )
        b = RGBDisplay(
            random.uniform(0.0, 1.0),
            random.uniform(0.0, 1.0),
            random.uniform(0.0, 1.0),
        )
        measure(a, b)

    # Show statistics: min, max, avg
    def stats(values):
        mn = min(values)
        mx = max(values)
        avg = sum(values) / len(values)
        std_dev = np.std(values)
        mean = np.mean(values)
        skew = (3 * (mean - avg)) / std_dev if std_dev != 0 else 0.0
        excess_kurtosis = (np.mean((values - mean) ** 4) / (std_dev ** 4)) - 3 if std_dev != 0 else 0.0
        return f"Min: {mn:.3f}, Max: {mx:.3f}, Avg: {avg:.3f}, StdDev: {std_dev:.3f}, Mean: {mean:.3f}, Skew: {skew:.3f}, ExcessKurtosis: {excess_kurtosis:.3f}"

    print("RGBD:" + stats(rgbd_values))
    print("RGBL:" + stats(rgbl_values))
    print("Lab76:" + stats(lab76_values))
    print("Lab76-L:" + stats(lab76l_values))
    print("Lab2k:" + stats(lab2k_values))
    print("Lab2k-L:" + stats(lab2kl_values))
    print("HSV:" + stats(hsv_values))
    # print("HSV-L:" + stats(hsvl_values))
    print("HLS:" + stats(hls_values))
    # print("HLS-L:" + stats(hlsl_values))
    # print("YIQ Distance Stats:" + stats(yiq_values))

    plt.figure(figsize=(8,4))
    # plt.hist(rgbd_values, bins=200, alpha=0.5, label='RGBD', density=True)
    # plt.hist(rgbl_values, bins=200, alpha=0.5, label='RGBL', density=True)
    # plt.hist(hsv_values, bins=200, alpha=0.5, label='HSV', density=True)
    # plt.hist(hls_values, bins=200, alpha=0.5, label='HLS', density=True)
    # plt.hist(hsvl_values, bins=200, alpha=0.5, label='HSV-L', density=True)
    # plt.hist(hlsl_values, bins=200, alpha=0.5, label='HLS-L', density=True)
    # plt.hist(lab76_values, bins=200, alpha=0.5, label='ΔE76', density=True)
    plt.hist(lab76l_values, bins=200, alpha=0.5, label='ΔE76-L', density=True)
    # plt.hist(lab2k_values, bins=200, alpha=0.5, label='ΔE2000', density=True)
    plt.hist(lab2kl_values, bins=200, alpha=0.5, label='ΔE2000-L', density=True)
    plt.legend()
    plt.xlabel("Distance / ΔE")
    plt.ylabel("Density")
    plt.title("Distribution of color distances for random color pairs")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    generate()
