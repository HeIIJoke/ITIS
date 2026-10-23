"""Генерация единственного фонового изображения (море у берега)."""
from __future__ import annotations

import numpy as np
from PIL import Image

OUT = "img"
SS = 2


def _grid(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return xx / w, yy / h


def vgrad(h, w, stops):
    ys = np.linspace(0.0, 1.0, h, dtype=np.float32)
    out = np.zeros((h, 3), dtype=np.float32)
    for i in range(len(stops) - 1):
        y0, c0 = stops[i]
        y1, c1 = stops[i + 1]
        m = (ys >= y0) & (ys <= y1)
        if not m.any():
            continue
        t = ((ys[m] - y0) / max(y1 - y0, 1e-6))[:, None]
        out[m] = np.array(c0, np.float32) * (1 - t) + np.array(c1, np.float32) * t
    return np.repeat(out[:, None, :], w, axis=1)


def ridge(w, base, amp, seed, octaves=5):
    rng = np.random.default_rng(seed)
    x = np.linspace(0.0, 1.0, w, dtype=np.float32)
    y = np.zeros(w, dtype=np.float32)
    a = 1.0
    for o in range(octaves):
        f = 2 ** o
        y += a * np.sin(2 * np.pi * f * x + rng.uniform(0, 6.283))
        y += 0.45 * a * np.sin(2 * np.pi * f * 1.7 * x + rng.uniform(0, 6.283))
        a *= 0.5
    y = y / (np.abs(y).max() + 1e-9)
    return base + y * amp


def blend(img, mask, color, alpha=1.0):
    a = (mask.astype(np.float32) * alpha)[..., None]
    return img * (1 - a) + np.array(color, np.float32)[None, None, :] * a


def seascape(w, h, seed=1):
    W, H = w * SS, h * SS
    horizon = 0.62
    X, Y = _grid(W, H)

    sky = vgrad(H, W, [(0.0, (3, 11, 22)), (0.34, (6, 30, 46)), (0.62, (18, 78, 92))])
    water = vgrad(H, W, [(0.62, (14, 62, 76)), (0.82, (8, 38, 52)), (1.0, (2, 8, 16))])
    mask_water = (Y >= horizon)[..., None]
    img = sky * (1 - mask_water) + water * mask_water

    cx, cy = 0.70, 0.575
    rad = np.sqrt((X - cx) ** 2 + ((Y - cy) * 1.7) ** 2)
    img += np.exp(-(rad / 0.42) ** 2)[..., None] * np.array((96, 232, 214), np.float32) * 0.55

    d = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
    disc = np.clip((0.019 - d) / (0.019 * 0.45), 0, 1) ** 0.8
    img = img * (1 - disc[..., None] * 0.9) + np.array((226, 255, 246), np.float32) * (disc[..., None] * 0.9)

    for dz, amp, sd, col, al in [(-0.030, 0.030, 2, (9, 40, 52), 0.85),
                                 (-0.016, 0.020, 7, (6, 27, 37), 0.95)]:
        ry = ridge(W, horizon + dz, amp, sd)
        m = (Y >= ry[None, :]) & (Y < horizon + 0.012)
        img = blend(img, m, col, al)

    wmask = (Y > horizon).astype(np.float32)
    depth = np.clip((Y - horizon) / (1 - horizon), 0, 1)
    wob = 0.055 + 0.16 * depth
    col = np.exp(-(((X - cx) / wob) ** 2) * 1.9)
    streaks = 0.45 + 0.55 * np.abs(np.sin(depth * 120 + 3.0 * np.sin(X * 9.0)))
    img += (col * streaks * wmask * depth ** 0.6)[..., None] * np.array((96, 232, 214), np.float32) * 0.72

    for dz, amp, f, ph, colr, al in [(0.045, 0.006, 3.0, 0.4, (10, 52, 66), 0.55),
                                     (0.115, 0.009, 2.2, 1.7, (7, 38, 50), 0.60),
                                     (0.230, 0.013, 1.6, 3.1, (4, 24, 34), 0.70),
                                     (0.420, 0.018, 1.1, 5.0, (2, 15, 23), 0.80)]:
        yy = horizon + dz + amp * np.sin(2 * np.pi * f * X + ph)
        img = blend(img, Y >= yy, colr, al)

    haze = np.exp(-(((Y - horizon) / 0.05) ** 2))
    img += (haze * 0.13)[..., None] * np.array((96, 232, 214), np.float32)

    rng = np.random.default_rng(seed)
    img = img + rng.normal(0.0, 2.4, (H, W)).astype(np.float32)[..., None]

    d = np.sqrt(((X - 0.5) * 1.15) ** 2 + ((Y - 0.5) * 1.0) ** 2) / 0.72
    img = img * (1.0 - 0.5 * np.clip(d, 0, 1) ** 2.2)[..., None]

    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").resize((w, h), Image.LANCZOS)


if __name__ == "__main__":
    seascape(1920, 1080, seed=1).save(f"{OUT}/sea.png")
    print("ok sea.png")
