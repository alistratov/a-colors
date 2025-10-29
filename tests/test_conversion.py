import unittest

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

        for r in values:
            print(r)
            for g in values:
                for b in values:
                    rgbd = RGBDisplay.from_8bit(r, g, b)

                    rgbl = rgb_display_to_linear(rgbd)
                    rgbd2 = rgb_linear_to_display(rgbl)
                    self.assertTrue(rgbd.almost_equal(rgbd2))

                    # YIQ
                    yiq = rgb_to_yiq(rgbd)
                    rgbd2 = yiq_to_rgb_display(yiq)
                    self.assertTrue(rgbd.almost_equal(rgbd2))

                    # HSV
                    hsv = rgb_to_hsv(rgbd)
                    rgbd2 = hsv_to_rgb_display(hsv)
                    self.assertTrue(rgbd.almost_equal(rgbd2))

                    # HLS
                    hls = rgb_to_hls(rgbd)
                    rgbd2 = hls_to_rgb_display(hls)
                    self.assertTrue(rgbd.almost_equal(rgbd2))
