import numpy as np
import matplotlib.pyplot as plt

def srgb_to_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

RES = 32  # количество кубиков по каждой оси (9 → 729 вокселей)
vals = np.linspace(0, 1, RES)

# создаём 3D решётку координат
R, G, B = np.meshgrid(vals, vals, vals, indexing='ij')

# цвета в линейном пространстве
colors_linear = srgb_to_linear(np.stack([R, G, B], axis=-1))
colors_srgb = np.clip(colors_linear, 0, 1)

# булева маска, где нужно рисовать воксель (все True)
filled = np.ones(R.shape, dtype=bool)

fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(111, projection='3d')

# отрисовка плотного куба
ax.voxels(filled, facecolors=colors_srgb, edgecolor=None)

ax.set_xlabel("R")
ax.set_ylabel("G")
ax.set_zlabel("B")
ax.set_box_aspect((1, 1, 1))
ax.set_xlim(0, RES)
ax.set_ylim(0, RES)
ax.set_zlim(0, RES)
ax.set_title("Плотный RGB-куб (линейное пространство, без зазоров)")

plt.tight_layout()
plt.show()
