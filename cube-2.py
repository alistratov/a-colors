import numpy as np
import matplotlib.pyplot as plt

from colors import hsv_to_rgbl, HSV, lab76_to_rgbl, Lab76, rgb_to_lab76

def linear_to_srgb(c: float) -> float:
    # Linear light to gamma
    # Inverse of IEC 61966-2-1 sRGB EOTF
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1/2.4)) - 0.055

def srgb_to_linear(c: float) -> float:
    # Gamma to linear light
    # IEC 61966-2-1 sRGB EOTF
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def get_color(x, y, z):
    # hsv = HSV(x, y, z)
    # hsv = HSV(z, y, x)
    # rgbl = hsv_to_rgbl(hsv)
    # return (rgbl.r, rgbl.g, rgbl.b)

    l = x * 100
    a = y * 255 - 128
    b = z * 255 - 128
    lab = Lab76(l, a, b)
    rgbl = lab76_to_rgbl(lab)
    return (rgbl.r, rgbl.g, rgbl.b)

    # print(x, y, z)
    # return (x, y, z)
    # return (linear_to_srgb(x), linear_to_srgb(y), linear_to_srgb(z))
    # return (srgb_to_linear(x), srgb_to_linear(y), srgb_to_linear(z))


# --- Параметры ---
RES = 31  # куб 11×11×11
edges = np.linspace(0.0, 1.0, RES + 1)  # координаты рёбер от 0 до 1 с шагом 0.1
# edges = np.linspace(0, 1, RES + 1) * 0.9

# --- Булева маска для всех вокселей (всё заполнено) ---
filled = np.ones((RES, RES, RES), dtype=bool)

# ---- Сетка центров вокселей ----
# Центр каждого кубика находится посередине между рёбрами
centers = (edges[:-1] + edges[1:]) / 2
Xc, Yc, Zc = np.meshgrid(centers, centers, centers, indexing="ij")

# --- Цвета (пока все белые) ---
# facecolors = np.ones(filled.shape + (4,), dtype=float)  # RGBA
# facecolors[..., :3] = 1.0  # RGB = белый
# facecolors[..., 3] = 1.0   # alpha = 1 (непрозрачно)
facecolors = np.ones(filled.shape + (4,), dtype=float)
for i in range(RES):
    for j in range(RES):
        for k in range(RES):
            facecolors[i, j, k, :3] = get_color(Xc[i, j, k], Yc[i, j, k], Zc[i, j, k])
facecolors[..., 3] = 1.0  # непрозрачность

# --- Создаём сетку координат вокселей ---
X, Y, Z = np.meshgrid(edges, edges, edges, indexing="ij")

# --- Построение ---
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection="3d")

# ax.voxels(X, Y, Z, filled, facecolors=facecolors, edgecolor="k")
ax.voxels(X, Y, Z, filled, facecolors=facecolors, edgecolor=None, linewidth=0, shade=False)

# --- Настройка осей ---
ticks = np.linspace(0.0, 1.0, RES)
sparse_ticks = ticks[::2]

ax.set_xticks(sparse_ticks)
ax.set_yticks(sparse_ticks)
ax.set_zticks(sparse_ticks)
ax.set_xticklabels([f"{t:.1f}" for t in sparse_ticks])
ax.set_yticklabels([f"{t:.1f}" for t in sparse_ticks])
ax.set_zticklabels([f"{t:.1f}" for t in sparse_ticks])

ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_zlim(0, 1)
ax.set_box_aspect((1, 1, 1))
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")

# --- Поворот: чтобы вершина (1,1,1) была обращена к наблюдателю ---
ax.view_init(elev=22, azim=35)

# --- Отметим вершину (1,1,1) ---
# ax.scatter([1], [1], [1], s=60, c="red")
# ax.text(1, 1, 1, " (1,1,1)", color="red")

ax.set_title("11×11×11 voxel cube on [0,1]³ (corner (1,1,1) facing viewer)")
plt.tight_layout()
plt.rcParams['lines.antialiased'] = False
plt.show()
