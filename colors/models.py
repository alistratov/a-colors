import math

# Validators
def check01(value: float) -> float:
    if value < 0.0 or value > 1.0:
        raise ValueError("Value must be in [0..1], got: {}".format(value))
    return value


# DEFAULT_TOLERANCE = 1 / 256.0
DEFAULT_TOLERANCE = 1 / 512.0


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
        if type(self) is not type(other):
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
        dn = d / math.sqrt(3.0)  # normalize to 0..1
        return check01(dn)


class RGBDisplay(CubeModel):
    """
    sRGB (gamma-corrected), components in [0..1].
    This is "as on screen".
    """
    def __init__(self, r: float, g: float, b: float):
        self.r = check01(r)
        self.g = check01(g)
        self.b = check01(b)

    def components(self) -> tuple:
        return self.r, self.g, self.b

    @classmethod
    def from_8bit(cls, r: int, g: int, b: int) -> "RGBDisplay":
        return cls(r / 255.0, g / 255.0, b / 255.0)

    @classmethod
    def from_hex(cls, hex_str: str) -> "RGBDisplay":
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

    def distance(self, other: "RGBDisplay") -> float:
        if not isinstance(other, RGBDisplay):
            raise TypeError("RGBDisplay.distance expects RGBDisplay")
        # Naive Euclidean metric directly in gamma-corrected sRGB
        return self.euclidean_distance(
            self.r, self.g, self.b,
            other.r, other.g, other.b,
        )


class RGBLinear(RGBDisplay):
    """
    Actually, this is the same model as RGBDisplay, but without gamma correction.
    The methods and calculations are the same, but we need to distinguish them semantically.
    Components in [0..1].
    """
    def distance(self, other: "RGBLinear") -> float:
        if not isinstance(other, RGBLinear):
            raise TypeError("RGBLinear.distance expects RGBLinear")
        return self.euclidean_distance(
            self.r, self.g, self.b,
            other.r, other.g, other.b,
        )


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
        if not isinstance(other, YIQ):
            raise TypeError("YIQ.distance expects YIQ")
        return self.euclidean_distance(
            self.y, self.i, self.q,
            other.y, other.i, other.q,
        )


class CylindricalModel(AbstractColor):
    """
    Abstract base class for colors represented in a cylindrical color space (like HSV).
    """
    def cylindrical_distance(self,
                             a1: float, a2: float, a3: float,
                             b1: float, b2: float, b3: float,
                             ) -> float:
        # a1, b1 are angular (hue), a2, b2 and a3, b3 are linear (saturation, value)
        dh = abs(a1 - b1)
        dh = min(dh, 1.0 - dh)  # shortest arc, 0..0.5
        ds = a2 - b2
        dv = a3 - b3
        d = math.sqrt(dh ** 2 + ds ** 2 + dv ** 2)
        dn = d / math.sqrt(3.0)  # normalize to 0..1
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
        if not isinstance(other, HSV):
            raise TypeError("HSV.distance expects HSV")
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
        if not isinstance(other, HLS):
            raise TypeError("HLS.distance expects HLS")
        return self.cylindrical_distance(
            self.h, self.l, self.s,
            other.h, other.l, other.s,
        )
