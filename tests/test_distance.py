import unittest

from colors import RGBDisplay
from colors import (
    rgbd_to_rgbl,
    rgb_to_yiq,
    rgb_to_hsv,
    rgb_to_hls,
    rgb_to_lab76,
    rgb_to_lab2k,
)


class TestDistance(unittest.TestCase):
    def test_black_and_white(self):
        white = RGBDisplay(1.0, 1.0, 1.0)
        black = RGBDisplay(0.0, 0.0, 0.0)

        d_rgbd = white.distance(black)
        self.assertAlmostEqual(d_rgbd, 1.0)

        d_rgbl = rgbd_to_rgbl(white).distance(rgbd_to_rgbl(black))
        self.assertAlmostEqual(d_rgbl, 1.0)

        d_yiq = rgb_to_yiq(white).distance(rgb_to_yiq(black))
        self.assertAlmostEqual(d_yiq, 0.577, places=3)

        d_hsv = rgb_to_hsv(white).distance(rgb_to_hsv(black))
        self.assertAlmostEqual(d_hsv, 0.577, places=3)

        d_hls = rgb_to_hls(white).distance(rgb_to_hls(black))
        self.assertAlmostEqual(d_hls, 0.577, places=3)

        d_lab76 = rgb_to_lab76(white).distance(rgb_to_lab76(black))
        self.assertAlmostEqual(d_lab76, 1.0)

        d_lab2k = rgb_to_lab2k(white).distance(rgb_to_lab2k(black))
        self.assertAlmostEqual(d_lab2k, 1.0)

    def test_identical(self):
        for color in [
            (0.0, 0.0, 0.0),
            (1.0, 1.0, 1.0),
            (0.5, 0.5, 0.5),
            (0.2, 0.4, 0.6),
            (0.9, 0.1, 0.3),
        ]:
            a = RGBDisplay(*color)
            b = RGBDisplay(*color)

            d_rgbd = a.distance(b)
            self.assertAlmostEqual(d_rgbd, 0.0)

            d_rgbl = rgbd_to_rgbl(a).distance(rgbd_to_rgbl(b))
            self.assertAlmostEqual(d_rgbl, 0.0)

            d_yiq = rgb_to_yiq(a).distance(rgb_to_yiq(b))
            self.assertAlmostEqual(d_yiq, 0.0)

            d_hsv = rgb_to_hsv(a).distance(rgb_to_hsv(b))
            self.assertAlmostEqual(d_hsv, 0.0)

            d_hls = rgb_to_hls(a).distance(rgb_to_hls(b))
            self.assertAlmostEqual(d_hls, 0.0)

            d_lab76 = rgb_to_lab76(a).distance(rgb_to_lab76(b))
            self.assertAlmostEqual(d_lab76, 0.0)

            d_lab2k = rgb_to_lab2k(a).distance(rgb_to_lab2k(b))
            self.assertAlmostEqual(d_lab2k, 0.0)

    def test_samples(self):
        # Lab76: https://colormine.org/delta-e-calculator
        # Lab2k: https://colormine.org/delta-e-calculator/Cie2000

        a = RGBDisplay.from_8bit(0, 87, 183)
        b = RGBDisplay.from_8bit(255, 215, 0)

        d_rgbd = a.distance(b)
        self.assertAlmostEqual(d_rgbd, 0.767, places=3)

        # 152.9533
        d_lab76 = rgb_to_lab76(a).distance(rgb_to_lab76(b))
        self.assertAlmostEqual(d_lab76, 1.0)

        # 75.2134
        d_lab2k = rgb_to_lab2k(a).distance(rgb_to_lab2k(b))
        self.assertAlmostEqual(d_lab2k, 0.642, places=3)
