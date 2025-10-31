import unittest
import colorsys

from colors import *

"""
Delta R caluclators:
 - https://colormine.org/delta-e-calculator
 - https://colormine.org/delta-e-calculator/Cie2000
 
Colors:
 RGB(255, 215, 0), #FFD700 - UA Yellow
 RGB(0, 87, 183), #0057B7 - UA Blue
 
Convertors:
 - https://www.rapidtables.com/convert/color/rgb-to-hsv.html
 - https://colordesigner.io/convert/rgbtohsv
 - https://colormine.org/color-converter
 - https://colormine.org/convert/rgb-to-lab
"""

class TestConversion(unittest.TestCase):
    def test_samples(self):
        ua_yellow = RGBLinear.from_8bit(255, 215, 0)
        ua_blue = RGBLinear.from_8bit(0, 87, 183)

        # HSV
        hsv_yellow = rgb_to_hsv(ua_yellow)
        hsv_blue = rgb_to_hsv(ua_blue)
        self.assertAlmostEqual(hsv_yellow.h * 360, 50.588235294117645)
        self.assertAlmostEqual(hsv_yellow.s, 1.0)
        self.assertAlmostEqual(hsv_yellow.v, 1.0)
        self.assertAlmostEqual(hsv_blue.h * 360, 211.47540983606558)
        self.assertAlmostEqual(hsv_blue.s, 1.0)
        self.assertAlmostEqual(hsv_blue.v, 0.7176470588235294)

        # HLS
        hls_yellow = rgb_to_hls(ua_yellow)
        hls_blue = rgb_to_hls(ua_blue)
        self.assertAlmostEqual(hls_yellow.h * 360, 50.588235294117645)
        self.assertAlmostEqual(hls_yellow.l, 0.5)
        self.assertAlmostEqual(hls_yellow.s, 1.0)
        self.assertAlmostEqual(hls_blue.h * 360, 211.47540983606558)
        self.assertAlmostEqual(hls_blue.l, 0.3588235294117647)
        self.assertAlmostEqual(hls_blue.s, 1.0)

        # L*ab
        # See https://colormine.org/convert/rgb-to-lab, which uses sRGB
        lab_yellow = rgb_to_lab76(rgbd_to_rgbl(ua_yellow))
        lab_blue = rgb_to_lab76(rgbd_to_rgbl(ua_blue))
        self.assertAlmostEqual(lab_yellow.l, 86.9285847161576, delta=0.01)
        self.assertAlmostEqual(lab_yellow.a, -1.9242149651027551, delta=0.01)
        self.assertAlmostEqual(lab_yellow.b, 87.1371576065337, delta=0.01)
        self.assertAlmostEqual(lab_blue.l, 38.26144272027819, delta=0.01)
        self.assertAlmostEqual(lab_blue.a, 16.636374714070477, delta=0.01)
        self.assertAlmostEqual(lab_blue.b, -56.67426141344636, delta=0.01)

    def test_all_conversions(self):
        """
        Test creation of all RGB colors and conversion round-trips.
        """

        # All 8-bit values make 16 million tests.
        # values = list(range(0, 256))

        # Reduced set for faster testing
        values = list(range(0, 256, 16)) + [255]
        # print(values)

        def cmp_std(a, b):
            # Compare with standard library (colorsys) results
            for s, o in zip(a, b):
                self.assertAlmostEqual(s, o, places=2)

        for r in values:
            # print(r)
            for g in values:
                for b in values:
                    rgb = RGBLinear.from_8bit(r, g, b)

                    disp = rgbl_to_rgbd(rgb)
                    back = rgbd_to_rgbl(disp)
                    self.assertTrue(rgb.almost_equal(back))

                    # YIQ
                    yiq = rgb_to_yiq(rgb)
                    back = yiq_to_rgbl(yiq)
                    self.assertTrue(rgb.almost_equal(back))
                    our = yiq.components()
                    std = colorsys.rgb_to_yiq(*rgb.components())
                    cmp_std(our, std)

                    # HSV
                    hsv = rgb_to_hsv(rgb)
                    back = hsv_to_rgbl(hsv)
                    self.assertTrue(rgb.almost_equal(back))
                    our = hsv.components()
                    std = colorsys.rgb_to_hsv(*rgb.components())
                    cmp_std(our, std)

                    # HLS
                    hls = rgb_to_hls(rgb)
                    back = hls_to_rgbl(hls)
                    self.assertTrue(rgb.almost_equal(back))
                    our = hls.components()
                    std = colorsys.rgb_to_hls(*rgb.components())
                    cmp_std(our, std)

                    # Lab76
                    lab = rgb_to_lab76(rgb)
                    back = lab76_to_rgbl(lab)
                    self.assertTrue(rgb.almost_equal(back))

                    # Lab2k
                    lab2k = rgb_to_lab2k(rgb)
                    back = lab2k_to_rgbl(lab2k)
                    self.assertTrue(rgb.almost_equal(back))
