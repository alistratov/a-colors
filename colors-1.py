from __future__ import annotations
from dataclasses import dataclass
import math

# -----------------------------------------------------------
# ВСПОМОГАТЕЛЬНОЕ: clamp и sRGB гамма-кривые (IEC 61966-2-1)
# -----------------------------------------------------------

def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

def srgb_to_linear(c: float) -> float:
    # гамма -> линейный свет
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def linear_to_srgb(c: float) -> float:
    # линейный свет -> гамма
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1/2.4)) - 0.055

# -----------------------------------------------------------
# КЛАССЫ ЦВЕТОВ
# -----------------------------------------------------------

@dataclass(frozen=True)
class RGBDisplay:
    """
    sRGB (гаммированный), компоненты [0..1].
    Это «как на экране». Наивная метрика здесь — демонстрация несовершенства.
    """
    r: float; g: float; b: float
    def __post_init__(self):
        object.__setattr__(self, "r", clamp01(self.r))
        object.__setattr__(self, "g", clamp01(self.g))
        object.__setattr__(self, "b", clamp01(self.b))

    def distance(self, other: "RGBDisplay") -> float:
        if not isinstance(other, RGBDisplay):
            raise TypeError("RGBDisplay.distance ожидает RGBDisplay")
        # Наивная евклидова метрика прямо в гаммированном sRGB (специально «плохо»)
        d = math.sqrt((self.r - other.r)**2 + (self.g - other.g)**2 + (self.b - other.b)**2)
        return d / math.sqrt(3.0)  # нормируем к 0..1

@dataclass(frozen=True)
class RGBLinear:
    """
    Линейный RGB (после снятия гаммы), компоненты [0..1].
    Для физических/арифметических расчётов.
    """
    r: float; g: float; b: float
    def __post_init__(self):
        object.__setattr__(self, "r", clamp01(self.r))
        object.__setattr__(self, "g", clamp01(self.g))
        object.__setattr__(self, "b", clamp01(self.b))

    def distance(self, other: "RGBLinear") -> float:
        if not isinstance(other, RGBLinear):
            raise TypeError("RGBLinear.distance ожидает RGBLinear")
        d = math.sqrt((self.r - other.r)**2 + (self.g - other.g)**2 + (self.b - other.b)**2)
        return d / math.sqrt(3.0)

@dataclass(frozen=True)
class HSV:
    """
    HSV с h,s,v в [0..1]; h цикличен (0 == 1).
    """
    h: float; s: float; v: float
    def __post_init__(self):
        object.__setattr__(self, "h", self.h % 1.0)
        object.__setattr__(self, "s", clamp01(self.s))
        object.__setattr__(self, "v", clamp01(self.v))

    def distance(self, other: "HSV") -> float:
        if not isinstance(other, HSV):
            raise TypeError("HSV.distance ожидает HSV")
        # Евклидова метрика с учётом цикличности hue (короткая дуга)
        dh = abs(self.h - other.h)
        dh = min(dh, 1.0 - dh)  # 0..0.5
        ds = abs(self.s - other.s)
        dv = abs(self.v - other.v)
        d = math.sqrt(dh*dh + ds*ds + dv*dv)
        return d / math.sqrt(3.0)

@dataclass(frozen=True)
class Lab:
    """
    CIE L*a*b* (D65): L∈[0..100], a,b ~ [-128..127].
    Для простоты используем ΔE76 (евклидово) и нормируем /100.
    """
    L: float; a: float; b: float

    def distance(self, other: "Lab") -> float:
        if not isinstance(other, Lab):
            raise TypeError("Lab.distance ожидает Lab")
        d = math.sqrt((self.L - other.L)**2 + (self.a - other.a)**2 + (self.b - other.b)**2)
        return min(1.0, d / 100.0)

# -----------------------------------------------------------
# ЯВНЫЕ ФУНКЦИИ ПРЕОБРАЗОВАНИЙ (никакого поиска маршрутов)
# -----------------------------------------------------------

# sRGB(display)  <->  RGB(linear)

def rgbd_to_linearrgb(c: RGBDisplay) -> RGBLinear:
    return RGBLinear(
        srgb_to_linear(c.r),
        srgb_to_linear(c.g),
        srgb_to_linear(c.b),
    )

def linearrgb_to_rgbd(c: RGBLinear) -> RGBDisplay:
    return RGBDisplay(
        clamp01(linear_to_srgb(c.r)),
        clamp01(linear_to_srgb(c.g)),
        clamp01(linear_to_srgb(c.b)),
    )

# RGB(display) <-> HSV  (ручные формулы; без colorsys)

def rgbd_to_hsv(c: RGBDisplay) -> HSV:
    r, g, b = c.r, c.g, c.b
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    # H
    if d == 0:
        h = 0.0
    elif mx == r:
        h = ((g - b) / d) % 6.0
    elif mx == g:
        h = (b - r) / d + 2.0
    else:
        h = (r - g) / d + 4.0
    h = (h / 6.0) % 1.0
    # S
    s = 0.0 if mx == 0 else d / mx
    v = mx
    return HSV(h, s, v)

def hsv_to_rgbd(c: HSV) -> RGBDisplay:
    h = (c.h % 1.0) * 6.0
    i = int(h)  # сектор
    f = h - i
    p = c.v * (1.0 - c.s)
    q = c.v * (1.0 - c.s * f)
    t = c.v * (1.0 - c.s * (1.0 - f))
    if i == 0:   r, g, b = c.v, t, p
    elif i == 1: r, g, b = q, c.v, p
    elif i == 2: r, g, b = p, c.v, t
    elif i == 3: r, g, b = p, q, c.v
    elif i == 4: r, g, b = t, p, c.v
    else:        r, g, b = c.v, p, q
    return RGBDisplay(clamp01(r), clamp01(g), clamp01(b))

# RGB(display) <-> Lab через XYZ (D65)
# Матрицы — стандартные для sRGB↔XYZ (D65).

_Xn, _Yn, _Zn = 95.047, 100.000, 108.883  # белая точка D65

def _f_xyz(t: float) -> float:
    delta = 6/29
    return t ** (1/3) if t > (delta**3) else t / (3*delta*delta) + 4/29

def _finv_xyz(t: float) -> float:
    delta = 6/29
    return t**3 if t > delta else 3*delta*delta*(t - 4/29)

def _rgbd_to_xyz(c: RGBDisplay) -> tuple[float, float, float]:
    # 1) снять гамму
    rl, gl, bl = srgb_to_linear(c.r), srgb_to_linear(c.g), srgb_to_linear(c.b)
    # 2) линейный RGB -> XYZ (D65)
    X = rl*0.4124564 + gl*0.3575761 + bl*0.1804375
    Y = rl*0.2126729 + gl*0.7151522 + bl*0.0721750
    Z = rl*0.0193339 + gl*0.1191920 + bl*0.9503041
    return (X*100.0, Y*100.0, Z*100.0)

def _xyz_to_rgbd(X: float, Y: float, Z: float) -> RGBDisplay:
    # XYZ(0..100) -> линейный RGB -> sRGB
    X, Y, Z = X/100.0, Y/100.0, Z/100.0
    rl =  3.2404542*X -1.5371385*Y -0.4985314*Z
    gl = -0.9692660*X +1.8760108*Y +0.0415560*Z
    bl =  0.0556434*X -0.2040259*Y +1.0572252*Z
    r = clamp01(linear_to_srgb(rl))
    g = clamp01(linear_to_srgb(gl))
    b = clamp01(linear_to_srgb(bl))
    return RGBDisplay(r, g, b)

def rgbd_to_lab(c: RGBDisplay) -> Lab:
    X, Y, Z = _rgbd_to_xyz(c)
    fx, fy, fz = _f_xyz(X/_Xn), _f_xyz(Y/_Yn), _f_xyz(Z/_Zn)
    L = 116*fy - 16
    a = 500*(fx - fy)
    b = 200*(fy - fz)
    return Lab(L, a, b)

def lab_to_rgbd(c: Lab) -> RGBDisplay:
    fy = (c.L + 16)/116
    fx = fy + c.a/500
    fz = fy - c.b/200
    X = _Xn * _finv_xyz(fx)
    Y = _Yn * _finv_xyz(fy)
    Z = _Zn * _finv_xyz(fz)
    return _xyz_to_rgbd(X, Y, Z)

# Удобные мосты Display<->Linear
def rgbd_to_linearlab_bridge(c: RGBDisplay) -> RGBLinear:
    """Пример: «снять гамму» явно, без HSV/Lab."""
    return rgbd_to_linearrgb(c)

def linearrgb_to_lab_via_display(c: RGBLinear) -> Lab:
    """Пример намеренно «кривого» маршрута для демонстрации — так делать не надо в проде."""
    return rgbd_to_lab(linearrgb_to_rgbd(c))

# -----------------------------------------------------------
# ДЕМО: сравнение «наивного» RGBDisplay.distance и Lab.distance
# -----------------------------------------------------------

if __name__ == "__main__":
    red_d  = RGBDisplay(1, 0, 0)
    green_d= RGBDisplay(0, 1, 0)
    blue_d = RGBDisplay(0, 0, 1)

    # Наивная метрика в sRGB (гамма) — то, что студентам надо показать как «плохо»
    print("Naive sRGB distance R-G:", red_d.distance(green_d))

    # Тот же цвет, но в линейном RGB — расстояние уже другое
    red_lin   = rgbd_to_linearrgb(red_d)
    green_lin = rgbd_to_linearrgb(green_d)
    print("Linear RGB distance R-G:", red_lin.distance(green_lin))

    # А в Lab (перцептивная модель) — ещё один ориентир (ΔE76/100)
    red_lab   = rgbd_to_lab(red_d)
    green_lab = rgbd_to_lab(green_d)
    print("Lab ΔE76 norm R-G:", red_lab.distance(green_lab))

    # Пара с разной яркостью, но похожим оттенком — наглядный контраст метрик
    c1 = RGBDisplay(0.2, 0.6, 0.2)  # тёмно-зелёный
    c2 = RGBDisplay(0.6, 0.9, 0.6)  # светло-зелёный
    print("Naive sRGB distance (green shades):", c1.distance(c2))
    print("Lab ΔE76 norm   (green shades):", rgbd_to_lab(c1).distance(rgbd_to_lab(c2)))
