"""Dibuja cada fractal como imagen y la proyecta sobre el marcador ArUco."""
import math

import cv2
import numpy as np

from config import CANVAS_SIZE
from shared import series

# ---------- Mandelbrot y Julia ----------

def _grid(cx, cy, span):
    """Malla compleja centrada en (cx, cy) con el ancho indicado."""
    xs = np.linspace(cx - span / 2, cx + span / 2, CANVAS_SIZE)
    ys = np.linspace(cy - span / 2, cy + span / 2, CANVAS_SIZE)
    X, Y = np.meshgrid(xs, ys)
    return X + 1j * Y

def _escape_map(Z, C, max_iter):
    """Iteración vectorizada de z = z^2 + c. Devuelve la iteración de escape por píxel."""
    esc = np.full(Z.shape, float(max_iter))
    for i in range(max_iter):
        Z = Z * Z + C
        out = (np.abs(Z) > 2) & (esc == max_iter)
        esc[out] = i
        Z = np.where(np.abs(Z) > 2, 2 + 0j, Z)
    return esc

def _to_color(esc, max_iter):
    """Convergencia (acotada) = oscuro. Divergencia rápida = brillante."""
    img = (255 * (1 - esc / max_iter)).astype(np.uint8)
    return cv2.applyColorMap(img, cv2.COLORMAP_INFERNO)

def mandelbrot(p):
    it = int(p["iter"])
    C = _grid(p["cx"], p["cy"], 3.0 / p["zoom"])
    return _to_color(_escape_map(np.zeros_like(C), C, it), it)

def julia(p):
    it = int(p["iter"])
    Z = _grid(0.0, 0.0, 3.0)
    C = np.full(Z.shape, complex(p["x"], p["y"]))
    return _to_color(_escape_map(Z, C, it), it)

# ---------- Sierpinski ----------

def sierpinski(p):
    size = CANVAS_SIZE
    img = np.zeros((size, size, 3), np.uint8)
    margin = size * (1 - p["escala"]) / 2
    a = np.array([size / 2, margin])
    b = np.array([margin, size - margin])
    c = np.array([size - margin, size - margin])

    def rec(a, b, c, d):
        if d == 0:
            cv2.fillConvexPoly(img, np.round([a, b, c]).astype(np.int32), (0, 200, 255))
            return
        ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
        rec(a, ab, ca, d - 1)
        rec(ab, b, bc, d - 1)
        rec(ca, bc, c, d - 1)

    rec(a, b, c, int(p["depth"]))
    return img

# ---------- Koch ----------

def _koch_edge(a, b, n):
    """Puntos de inicio de un lado del copo de Koch tras n iteraciones."""
    if n == 0:
        return [a]
    d = (b - a) / 3
    p, q = a + d, a + 2 * d
    t = p + d * complex(math.cos(-math.pi / 3), math.sin(-math.pi / 3))
    return _koch_edge(a, p, n - 1) + _koch_edge(p, t, n - 1) + _koch_edge(t, q, n - 1) + _koch_edge(q, b, n - 1)

def koch(p):
    size = CANVAS_SIZE
    n, scale = int(p["n"]), p["largo"]
    verts = [complex(math.cos(math.pi / 2 + 2 * math.pi * k / 3),
                     math.sin(math.pi / 2 + 2 * math.pi * k / 3)) for k in range(3)]
    pts = []
    for k in range(3):
        pts += _koch_edge(verts[k], verts[(k + 1) % 3], n)
    xy = np.array([[size / 2 + z.real * 0.42 * scale * size,
                    size / 2 - z.imag * 0.42 * scale * size] for z in pts], np.int32)
    img = np.zeros((size, size, 3), np.uint8)
    cv2.polylines(img, [xy.reshape(-1, 1, 2)], True, (255, 255, 0), 1, cv2.LINE_AA)
    return img

# ---------- Pitágoras ----------

def _branch(img, x, y, length, angle, depth, spread):
    if depth == 0 or length < 1.5:
        return
    x2 = x + length * math.cos(angle)
    y2 = y - length * math.sin(angle)
    cv2.line(img, (int(x), int(y)), (int(x2), int(y2)), (80, 255, 80), 2, cv2.LINE_AA)
    for sign in (1, -1):
        _branch(img, x2, y2, length * 0.7, angle + sign * spread, depth - 1, spread)

def pythagoras(p):
    size = CANVAS_SIZE
    img = np.zeros((size, size, 3), np.uint8)
    _branch(img, size / 2, size - 10, size * 0.22, math.pi / 2, int(p["depth"]), p["angulo"])
    return img

# ---------- Dragón ----------

def dragon(p):
    size = CANVAS_SIZE
    turns = series.dragon_turns(5)[:int(p["dobleces"])]
    x, y, dx, dy = 0.0, 0.0, 1.0, 0.0
    pts = [(x, y)]
    for t in turns:
        x, y = x + dx, y + dy
        pts.append((x, y))
        dx, dy = (dy, -dx) if t == "R" else (-dy, dx)
    x, y = x + dx, y + dy
    pts.append((x, y))
    P = np.array(pts)
    mn, mx = P.min(axis=0), P.max(axis=0)
    span = max((mx - mn).max(), 1e-9)
    P = (P - (mn + mx) / 2) / span * size * 0.8 + size / 2
    img = np.zeros((size, size, 3), np.uint8)
    cv2.polylines(img, [P.astype(np.int32).reshape(-1, 1, 2)], False, (255, 128, 255), 2, cv2.LINE_AA)
    return img

# ---------- Lorenz (dinámico) ----------

_lorenz_cache = {}

def _lorenz_path(sigma, rho, beta, steps=6000, dt=0.005):
    key = (round(sigma, 3), round(rho, 3), round(beta, 3))
    if key not in _lorenz_cache:
        x, y, z = 0.1, 0.0, 0.0
        pts = []
        for _ in range(steps):
            x, y, z = series.lorenz_step(x, y, z, sigma, rho, beta, dt)
            pts.append((x, z))
        _lorenz_cache.clear()
        _lorenz_cache[key] = np.array(pts)
    return _lorenz_cache[key]

def lorenz(p, frame_idx):
    size = CANVAS_SIZE
    P = _lorenz_path(p["sigma"], p["rho"], p["beta"])
    px = size / 2 + P[:, 0] / 25 * size * 0.45
    py = size * 0.95 - P[:, 1] / 50 * size * 0.9
    pts = np.stack([px, py], axis=1).astype(np.int32)
    head = int(frame_idx * p["velocidad"] * 5) % len(pts)
    img = np.zeros((size, size, 3), np.uint8)
    start = max(0, head - 800)
    if head - start > 1:
        cv2.polylines(img, [pts[start:head + 1].reshape(-1, 1, 2)], False, (0, 200, 255), 1, cv2.LINE_AA)
    cv2.circle(img, (int(pts[head][0]), int(pts[head][1])), 4, (255, 255, 255), -1)
    return img

# ---------- Despacho ----------

RENDERERS = {1: mandelbrot, 2: julia, 3: sierpinski, 4: koch, 5: pythagoras, 6: dragon}

def render(game_id, params, frame_idx=0):
    """Devuelve la imagen BGR del juego indicado con sus parámetros actuales."""
    if game_id == 7:
        return lorenz(params, frame_idx)
    return RENDERERS[game_id](params)
