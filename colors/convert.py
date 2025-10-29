from .models import RGBDisplay, RGBLinear, YIQ, HSV, HLS

# --- RGB -----------------------------------------------------------
def srgb_to_linear(c: float) -> float:
    # Gamma to linear light
    # IEC 61966-2-1 sRGB EOTF
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    # Linear light to gamma
    # Inverse of IEC 61966-2-1 sRGB EOTF
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1/2.4)) - 0.055


def rgb_display_to_linear(rgb: RGBDisplay) -> RGBLinear:
    r_lin = srgb_to_linear(rgb.r)
    g_lin = srgb_to_linear(rgb.g)
    b_lin = srgb_to_linear(rgb.b)
    return RGBLinear(r_lin, g_lin, b_lin)


def rgb_linear_to_display(rgb: RGBLinear) -> RGBDisplay:
    r_srgb = linear_to_srgb(rgb.r)
    g_srgb = linear_to_srgb(rgb.g)
    b_srgb = linear_to_srgb(rgb.b)
    return RGBDisplay(r_srgb, g_srgb, b_srgb)


# --- YIQ -----------------------------------------------------------
def rgb_to_yiq(rgb: RGBLinear | RGBDisplay) -> YIQ:
    r, g, b = rgb.r, rgb.g, rgb.b
    y = 0.299 * r + 0.587 * g + 0.114 * b
    i = 0.596 * r - 0.274 * g - 0.322 * b
    q = 0.211 * r - 0.523 * g + 0.312 * b
    return YIQ(y, i, q)


def _yiq_to_rgb(yiq: YIQ) -> tuple[float, float, float]:
    y, i, q = yiq.y, yiq.i, yiq.q
    r = y + 0.956 * i + 0.621 * q
    g = y - 0.272 * i - 0.647 * q
    b = y - 1.106 * i + 1.703 * q
    r = max(0.0, min(1.0, r))
    g = max(0.0, min(1.0, g))
    b = max(0.0, min(1.0, b))
    return r, g, b


def yiq_to_rgb_display(yiq: YIQ) -> RGBDisplay:
    return RGBDisplay(*_yiq_to_rgb(yiq))


def yiq_to_rgb_linear(yiq: YIQ) -> RGBLinear:
    return RGBLinear(*_yiq_to_rgb(yiq))

# --- HSV -----------------------------------------------------------
def rgb_to_hsv(rgb: RGBDisplay | RGBLinear) -> HSV:
    r, g, b = rgb.r, rgb.g, rgb.b
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

def _hsv_to_rgb(hsv: HSV) -> tuple[float, float, float]:
    h = (hsv.h % 1.0) * 6.0
    i = int(h)  # sector
    f = h - i
    p = hsv.v * (1.0 - hsv.s)
    q = hsv.v * (1.0 - hsv.s * f)
    t = hsv.v * (1.0 - hsv.s * (1.0 - f))
    if i == 0:
        r, g, b = hsv.v, t, p
    elif i == 1:
        r, g, b = q, hsv.v, p
    elif i == 2:
        r, g, b = p, hsv.v, t
    elif i == 3:
        r, g, b = p, q, hsv.v
    elif i == 4:
        r, g, b = t, p, hsv.v
    else:
        r, g, b = hsv.v, p, q
    return r, g, b

def hsv_to_rgb_display(hsv: HSV) -> RGBDisplay:
    return RGBDisplay(*_hsv_to_rgb(hsv))

def hsv_to_rgb_linear(hsv: HSV) -> RGBLinear:
    return RGBLinear(*_hsv_to_rgb(hsv))

# --- HLS -----------------------------------------------------------
ONE_THIRD = 1.0 / 3.0
ONE_SIXTH = 1.0 / 6.0
TWO_THIRD = 2.0 / 3.0

def _v(m1, m2, hue):
    hue = hue % 1.0
    if hue < ONE_SIXTH:
        return m1 + (m2 - m1) * hue * 6.0
    if hue < 0.5:
        return m2
    if hue < TWO_THIRD:
        return m1 + (m2 - m1) * (TWO_THIRD - hue) * 6.0
    return m1


def rgb_to_hls(rgb: RGBDisplay | RGBLinear) -> HLS:
    r, g, b = rgb.r, rgb.g, rgb.b
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mn + mx) / 2.0
    if mn == mx:
        return HLS(0.0, l, 0.0)
    if l <= 0.5:
        s = (mx - mn) / (mx + mn)
    else:
        s = (mx - mn) / (2.0 - mx - mn)
    d = mx - mn
    # H
    if mx == r:
        h = ((g - b) / d) % 6.0
    elif mx == g:
        h = (b - r) / d + 2.0
    else:
        h = (r - g) / d + 4.0
    h = (h / 6.0) % 1.0
    return HLS(h, l, s)


def _hls_to_rgb(hls: HLS) -> tuple[float, float, float]:
    h, l, s = hls.h, hls.l, hls.s
    if s == 0.0:
        return l, l, l
    if l <= 0.5:
        m2 = l * (1.0 + s)
    else:
        m2 = l + s - (l * s)
    m1 = 2.0 * l - m2
    return (
        _v(m1, m2, h + ONE_THIRD),
        _v(m1, m2, h),
        _v(m1, m2, h - ONE_THIRD),
    )


def hls_to_rgb_display(hls: HLS) -> RGBDisplay:
    return RGBDisplay(*_hls_to_rgb(hls))


def hls_to_rgb_linear(hls: HLS) -> RGBLinear:
    return RGBLinear(*_hls_to_rgb(hls))
