import math

# Validators
def check01(value: float) -> float:
    if value < 0.0 or value > 1.0:
        raise ValueError("Value must be in [0..1], got: {}".format(value))
    return value


# Tolerance for "almost equal" comparisons
DEFAULT_TOLERANCE = 1 / 512.0

# Precomputed constants
SQRT3 = math.sqrt(3.0)


class AbstractColor:
    """
    Abstract base class for color models.
    """
    def distance(self, other: "AbstractColor") -> float:
        """
        Calculate the distance between this color and another color.
        Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement distance method")

    def components(self) -> tuple[float, ...]:
        """
        Return the color components as a tuple.
        Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement components method")

    # Colors are comparable (within the same model) for equality, and hashable.
    # The tuple of components is used for that.
    def __eq__(self, other: object) -> bool:
        # Compare only with the exactly same type
        if type(other) is not type(self):
            # return NotImplemented
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
        assert isinstance(other, AbstractColor)
        return self.components() == other.components()

    def __hash__(self) -> int:
        return hash(self.components())

    def almost_equal(self, other: object, tol: float = DEFAULT_TOLERANCE) -> bool:
        """
        Check if this color is almost equal to another color within a tolerance.
        """
        if type(self) is not type(other):
            raise TypeError(f"Cannot compare {type(self)} with {type(other)}")
        assert isinstance(other, AbstractColor)
        res = all(abs(a - b) <= tol for a, b in zip(self.components(), other.components()))
        return res

    def __str__(self) -> str:
        return f"{self.__class__.__name__}{self.components()}"


class CubeModel(AbstractColor):
    """
    Abstract base class for colors represented in a cubic color space (like RGB or YIQ).
    """
    def euclidean_distance(self,
                           a1: float, a2: float, a3: float,
                           b1: float, b2: float, b3: float,
                           ) -> float:
        d = math.sqrt((a1 - b1) ** 2 + (a2 - b2) ** 2 + (a3 - b3) ** 2)
        dn = d / SQRT3  # normalize to 0..1
        return check01(dn)


class CylindricalModel(AbstractColor):
    """
    Abstract base class for colors represented in a cylindrical color space (like HSV).
    """
    def cylindrical_distance(self,
                             a1: float, a2: float, a3: float,
                             b1: float, b2: float, b3: float,
                             ) -> float:
        # The only difference from Euclidean is in the first component (angle),
        # which wraps around.  So we compute the shortest arc distance.
        dh = abs(a1 - b1)
        dh = min(dh, 1.0 - dh)  # shortest arc, 0..0.5
        d = math.sqrt(dh ** 2 + (a2 - b2) ** 2 + (a3 - b3) ** 2)  # Max is sqrt(0.5^2 + 1^2 + 1^2) = sqrt(2.25) = 1.5
        dn = d / 1.5  # normalize to 0..1
        return check01(dn)


class RGB(CubeModel):
    """
    RGB, components in [0..1].
    """
    def __init__(self, r: float, g: float, b: float):
        self.r = check01(r)
        self.g = check01(g)
        self.b = check01(b)

    def components(self) -> tuple:
        return self.r, self.g, self.b

    @classmethod
    def from_8bit(cls, r: int, g: int, b: int) -> "RGB":
        return cls(r / 255.0, g / 255.0, b / 255.0)

    @classmethod
    def from_hex(cls, hex_str: str) -> "RGB":
        if hex_str.startswith('#'):
            hex_str = hex_str[1:]
        if len(hex_str) != 6:
            raise ValueError("Hex string must be 6 characters long")
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        return cls.from_8bit(r, g, b)

    def to_8bit(self) -> tuple[int, int, int]:
        return int(self.r * 255), int(self.g * 255), int(self.b * 255)

    def to_hex(self) -> str:
        r, g, b = self.to_8bit()
        return f"#{r:02X}{g:02X}{b:02X}"

    def distance(self, other: "RGB") -> float:
        if type(other) is not type(self):
            raise TypeError(f"Type mismatch: {type(self)} vs {type(other)}")
        return self.euclidean_distance(
            self.r, self.g, self.b,
            other.r, other.g, other.b,
        )


class RGBDisplay(RGB):
    """
    sRGB (gamma-corrected), components in [0..1].
    This is "as on screen".
    """
    pass
    # def __init__(self, r: float, g: float, b: float):
    #     self.r = check01(r)
    #     self.g = check01(g)
    #     self.b = check01(b)
    #
    # def components(self) -> tuple:
    #     return self.r, self.g, self.b
    #
    # @classmethod
    # def from_8bit(cls, r: int, g: int, b: int) -> "RGBDisplay":
    #     return cls(r / 255.0, g / 255.0, b / 255.0)
    #
    # @classmethod
    # def from_hex(cls, hex_str: str) -> "RGBDisplay":
    #     if hex_str.startswith('#'):
    #         hex_str = hex_str[1:]
    #     if len(hex_str) != 6:
    #         raise ValueError("Hex string must be 6 characters long")
    #     r = int(hex_str[0:2], 16)
    #     g = int(hex_str[2:4], 16)
    #     b = int(hex_str[4:6], 16)
    #     return cls.from_8bit(r, g, b)
    #
    # def to_8bit(self) -> tuple[int, int, int]:
    #     return int(self.r * 255), int(self.g * 255), int(self.b * 255)
    #
    # def to_hex(self) -> str:
    #     r, g, b = self.to_8bit()
    #     return f"#{r:02X}{g:02X}{b:02X}"
    #
    # def distance(self, other: "RGBDisplay") -> float:
    #     if not isinstance(other, RGBDisplay):
    #         raise TypeError("RGBDisplay.distance expects RGBDisplay")
    #     # Naive Euclidean metric directly in gamma-corrected sRGB
    #     return self.euclidean_distance(
    #         self.r, self.g, self.b,
    #         other.r, other.g, other.b,
    #     )


class RGBLinear(RGB):
    """
    Actually, this is the same model as RGBDisplay, but without gamma correction.
    The methods and calculations are the same, but we need to distinguish them semantically.
    Components in [0..1].
    """
    pass
    # def distance(self, other: "RGBLinear") -> float:
    #     if not isinstance(other, RGBLinear):
    #         raise TypeError("RGBLinear.distance expects RGBLinear")
    #     return self.euclidean_distance(
    #         self.r, self.g, self.b,
    #         other.r, other.g, other.b,
    #     )


class YIQ(CubeModel):
    """
    YIQ color model, components in [0..1].
    Y: Luminance, I: In-phase, Q: Quadrature
    See https://en.wikipedia.org/wiki/YIQ
    """
    def __init__(self, y: float, i: float, q: float):
        self.y = check01(y)
        # if i < -0.5957 or i > 0.5957:
        #     raise ValueError("I component must be in [-0.5957..0.5957], got: {}".format(i))
        if i < -0.5961 or i > 0.5961:
            raise ValueError("I component must be in [-0.5961..0.5961], got: {}".format(i))
        # if q < -0.5226 or q > 0.5226:
        #     raise ValueError("Q component must be in [-0.5226..0.5226], got: {}".format(q))
        if q < -0.523 or q > 0.523:
            raise ValueError("Q component must be in [-0.523..0.523], got: {}".format(q))
        self.i = i
        self.q = q

    def components(self) -> tuple:
        return self.y, self.i, self.q

    def distance(self, other: "YIQ") -> float:
        if type(other) is not type(self):
            raise TypeError(f"Type mismatch: {type(self)} vs {type(other)}")
        # Theoretically max distance is sqrt(1^2 + (0.5961*2)^2 + (0.523*2)^2)
        # = sqrt(1 + 1.4213 + 1.0925)
        # = sqrt(3.5138)
        # = 1.8746
        # return self.euclidean_distance(
        #     self.y, self.i, self.q,
        #     other.y, other.i, other.q,
        # )
        d = math.sqrt((self.y - other.y) ** 2 + (self.i - other.i) ** 2 + (self.q - other.q) ** 2)
        dn = d / 1.875  # normalize to 0..1
        return check01(dn)


class HSV(CylindricalModel):
    """
    HSV color model, components in [0..1].
    H: Hue, S: Saturation, V: Value (Brightness)
    """
    def __init__(self, h: float, s: float, v: float):
        self.h = check01(h)
        self.s = check01(s)
        self.v = check01(v)

    def components(self) -> tuple:
        return self.h, self.s, self.v

    @classmethod
    def from_degrees(cls, h_deg: float, s: float, v: float) -> "HSV":
        """
        Create HSV from hue in degrees, and saturation, value in percentage 0..100.
        """
        h = (h_deg % 360) / 360.0
        s = s / 100.0
        v = v / 100.0
        return cls(h, s, v)

    def to_degrees_int(self) -> tuple[int, int, int]:
        """
        Convert HSV to (hue in degrees, saturation in percentage, value in percentage).
        """
        h_deg = int(round(self.h * 360)) % 360
        s_pct = int(round(self.s * 100))
        v_pct = int(round(self.v * 100))
        return h_deg, s_pct, v_pct

    def distance(self, other: "HSV") -> float:
        if type(other) is not type(self):
            raise TypeError(f"Type mismatch: {type(self)} vs {type(other)}")
        return self.cylindrical_distance(
            self.h, self.s, self.v,
            other.h, other.s, other.v,
        )


class HLS(CylindricalModel):
    """
    HLS color model, components in [0..1].
    H: Hue, L: Luminance, S: Saturation
    """
    def __init__(self, h: float, l: float, s: float):
        self.h = check01(h)
        self.l = check01(l)
        self.s = check01(s)

    def components(self) -> tuple:
        return self.h, self.l, self.s

    def distance(self, other: "HLS") -> float:
        if type(other) is not type(self):
            raise TypeError(f"Type mismatch: {type(self)} vs {type(other)}")
        return self.cylindrical_distance(
            self.h, self.l, self.s,
            other.h, other.l, other.s,
        )


class Lab(CubeModel):
    """
    CIE L*a*b* color model.
    """
    def __init__(self, l: float, a: float, b: float):
        self.l = l
        self.a = a
        self.b = b

    def components(self) -> tuple:
        return self.l, self.a, self.b


class Lab76(Lab):
    """
    CIE L*a*b* color model with CIEDE1976 distance metric.
    """
    def distance_not_normalized(self, other: "Lab76") -> float:
        # ΔE76 metric
        d = math.sqrt((self.l - other.l) ** 2 + (self.a - other.a) ** 2 + (self.b - other.b) ** 2)
        return d

    def distance(self, other: "Lab76") -> float:
        if type(other) is not type(self):
            raise TypeError(f"Type mismatch: {type(self)} vs {type(other)}")
        d = self.distance_not_normalized(other)
        dn = min(d / 258.0, 1.0)  # Normalize to 0..1, max ~ 255-260
        return check01(dn)


class Lab2k(Lab):
    """
    CIE L*a*b* color model with CIEDE2000 distance metric.
    """
    def _calc_distance(self, other: "Lab2k") -> float:
        # ΔE2000 metric
        # Implementation of the CIEDE2000 formula
        # Reference: https://en.wikipedia.org/wiki/Color_difference#CIEDE2000
        L1, a1, b1 = self.l, self.a, self.b
        L2, a2, b2 = other.l, other.a, other.b

        avg_L = (L1 + L2) / 2.0
        C1 = math.sqrt(a1 ** 2 + b1 ** 2)
        C2 = math.sqrt(a2 ** 2 + b2 ** 2)
        avg_C = (C1 + C2) / 2.0

        G = 1 - 0.5 * (avg_C ** 7) / (avg_C ** 7 + 25 ** 7)
        a1p = (1 + G) * a1
        a2p = (1 + G) * a2
        C1p = math.sqrt(a1p ** 2 + b1 ** 2)
        C2p = math.sqrt(a2p ** 2 + b2 ** 2)

        h1p = math.degrees(math.atan2(b1, a1p)) % 360
        h2p = math.degrees(math.atan2(b2, a2p)) % 360

        delta_Lp = L2 - L1
        delta_Cp = C2p - C1p

        if C1p * C2p == 0:
            delta_hp = 0.0
        else:
            dhp = h2p - h1p
            if abs(dhp) <= 180:
                delta_hp = dhp
            elif dhp > 180:
                delta_hp = dhp - 360
            else:
                delta_hp = dhp + 360

        delta_Hp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(delta_hp) / 2)
        avg_Lp = (L1 + L2) / 2.0
        avg_Cp = (C1p + C2p) / 2.0
        if C1p * C2p == 0:
            avg_hp = h1p + h2p
        else:
            dhp = abs(h1p - h2p)
            if dhp <= 180:
                avg_hp = (h1p + h2p) / 2.0
            elif (h1p + h2p) < 360:
                avg_hp = (h1p + h2p + 360) / 2.0
            else:
                avg_hp = (h1p + h2p - 360) / 2.0
        T = (1
                - 0.17 * math.cos(math.radians(avg_hp - 30))
                + 0.24 * math.cos(math.radians(2 * avg_hp))
                + 0.32 * math.cos(math.radians(3 * avg_hp +
                                             6))
                - 0.20 * math.cos(math.radians(4 * avg_hp - 63)))
        delta_ro = 30 * math.exp(-((avg_hp - 275) /
                                    25) ** 2)
        RC = 2 * math.sqrt((avg_Cp ** 7) /
                            (avg_Cp ** 7 + 25 ** 7))
        SL = 1 + ((0.015 * ((avg_Lp - 50) ** 2)) /
                    math.sqrt(20 + ((avg_Lp - 50) ** 2)))
        SC = 1 + 0.045 * avg_Cp
        SH = 1 + 0.015 * avg_Cp * T
        RT = -math.sin(math.radians(2 * delta_ro)) * RC
        delta_E = math.sqrt(
            (delta_Lp / SL) ** 2 +
            (delta_Cp / SC) ** 2 +
            (delta_Hp / SH) ** 2 +
            RT * (delta_Cp / SC) * (delta_Hp / SH)
        )
        return delta_E

    def distance_not_normalized(self, other: "Lab2k") -> float:
        return self._calc_distance(other)

    def distance(self, other: "Lab2k") -> float:
        if type(other) is not type(self):
            raise TypeError(f"Type mismatch: {type(self)} vs {type(other)}")

        d = self._calc_distance(other)
        dn = min(d / 128.0, 1.0)  # Normalize to 0..1, max ~ 128-129
        return check01(dn)
