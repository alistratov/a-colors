import unittest
import math

from colors.convert import _srgb_to_linear, _linear_to_srgb
from colors.models import RGBDisplay, RGBLinear


class TestRGB(unittest.TestCase):
    def test_constructors(self):
        for cls in (RGBDisplay, RGBLinear):
            a = cls(0.0, 0.0, 0.0)
            self.assertEqual(a.r, 0.0)
            self.assertEqual(a.g, 0.0)
            self.assertEqual(a.b, 0.0)

            a = cls(1.0, 1.0, 1.0)
            self.assertEqual(a.r, 1.0)
            self.assertEqual(a.g, 1.0)
            self.assertEqual(a.b, 1.0)

            a = cls(0.5, 0.5, 0.5)
            self.assertEqual(a.r, 0.5)
            self.assertEqual(a.g, 0.5)
            self.assertEqual(a.b, 0.5)

            # Test out-of-bounds values
            with self.assertRaises(ValueError):
                cls(-0.1, 0.0, 0.0)
            with self.assertRaises(ValueError):
                cls(0.0, 1.1, 0.0)
            with self.assertRaises(ValueError):
                cls(0.0, 0.0, 1.5)

            # To and from 8bit integers
            a = cls.from_8bit(20, 100, 200)
            self.assertIsInstance(a, cls)
            self.assertEqual(a.to_8bit(), (20, 100, 200))
            self.assertAlmostEqual(a.r, 20.0 / 255.0)
            self.assertAlmostEqual(a.g, 100 / 255.0)
            self.assertAlmostEqual(a.b, 200 / 255.0)

            h = a.to_hex()
            self.assertEqual(h, "#1464C8")

            b = cls.from_hex(h)
            self.assertIsInstance(b, cls)
            self.assertEqual(b.to_8bit(), (20, 100, 200))

    def test_equality(self):
        a = RGBDisplay(0.1, 0.2, 0.3)
        b = RGBDisplay(0.1, 0.2, 0.3)
        self.assertEqual(a, b)

        a = RGBDisplay(0.1, 0.2, 0.3000001)
        b = RGBDisplay(0.1, 0.2, 0.3)
        self.assertFalse(a == b)
        self.assertTrue(a.almost_equal(b))

        # Different types are not equal (not comparable), even if components match.
        rgbd = RGBDisplay(0.5, 0.5, 0.5)
        rgbl = RGBLinear(0.5, 0.5, 0.5)
        with self.assertRaises(TypeError):
            rgbd == rgbl

    def test_srgb_to_linear_and_back(self):
        # Test known values
        self.assertAlmostEqual(_srgb_to_linear(0.0), 0.0)
        self.assertAlmostEqual(_srgb_to_linear(0.04045), 0.0031308, places=6)
        self.assertAlmostEqual(_srgb_to_linear(1.0), 1.0)

        self.assertAlmostEqual(_linear_to_srgb(0.0), 0.0)
        self.assertAlmostEqual(_linear_to_srgb(0.0031308), 0.04045, places=6)
        self.assertAlmostEqual(_linear_to_srgb(1.0), 1.0)

        for i in range(0, 256):
            c = i / 255.0
            lin = _srgb_to_linear(c)
            srgb = _linear_to_srgb(lin)
            self.assertAlmostEqual(c, srgb, places=5)
            self.assertTrue(0.0 <= lin <= 1.0)

    def test_distance(self):
        for cls in (RGBDisplay, RGBLinear):
            a = cls(0.0, 0.0, 0.0)
            b = cls(1.0, 1.0, 1.0)
            self.assertAlmostEqual(a.distance(b), 1.0)

            a = cls(0.5, 0.5, 0.5)
            b = cls(0.5, 0.5, 0.5)
            self.assertAlmostEqual(a.distance(b), 0.0)

            a = cls(1.0, 0.0, 0.0)
            b = cls(0.0, 1.0, 0.0)
            self.assertAlmostEqual(a.distance(b), math.sqrt(2) / math.sqrt(3))

            # Known distance values
            a = cls(0.1, 0.3, 0.7)
            b = cls(0.5, 0.0, 0.1)
            self.assertAlmostEqual(a.distance(b), 0.4509249752822894)

            # By components
            for r in range(11):
                for g in range(11):
                    for b in range(11):
                        c1 = cls(r / 10.0, g / 10.0, b / 10.0)
                        c2 = cls((10 - r) / 10.0, (10 - g) / 10.0, (10 - b) / 10.0)
                        d = c1.distance(c2)
                        self.assertTrue(0.0 <= d <= 1.0)
