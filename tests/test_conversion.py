import unittest
import colorsys

from colors import *


class TestConversion(unittest.TestCase):
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
                    rgbd = RGBDisplay.from_8bit(r, g, b)

                    rgbl = rgbd_to_rgbl(rgbd)
                    rgbd2 = rgbl_to_rgbd(rgbl)
                    self.assertTrue(rgbd.almost_equal(rgbd2))

                    # YIQ
                    yiq = rgb_to_yiq(rgbd)
                    rgbd2 = yiq_to_rgbd(yiq)
                    self.assertTrue(rgbd.almost_equal(rgbd2))
                    our = yiq.components()
                    std = colorsys.rgb_to_yiq(*rgbd.components())
                    cmp_std(our, std)

                    # HSV
                    hsv = rgb_to_hsv(rgbd)
                    rgbd2 = hsv_to_rgbd(hsv)
                    self.assertTrue(rgbd.almost_equal(rgbd2))
                    our = hsv.components()
                    std = colorsys.rgb_to_hsv(*rgbd.components())
                    cmp_std(our, std)

                    # HLS
                    hls = rgb_to_hls(rgbd)
                    rgbd2 = hls_to_rgbd(hls)
                    self.assertTrue(rgbd.almost_equal(rgbd2))
                    our = hls.components()
                    std = colorsys.rgb_to_hls(*rgbd.components())
                    cmp_std(our, std)

                    # Lab76
                    lab = rgb_to_lab76(rgbd)
                    rgbd2 = lab76_to_rgbd(lab)
                    self.assertTrue(rgbd.almost_equal(rgbd2))

                    # Lab2k
                    lab2k = rgb_to_lab2k(rgbd)
                    rgbd2 = lab2k_to_rgbd(lab2k)
                    self.assertTrue(rgbd.almost_equal(rgbd2))
