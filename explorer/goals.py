"""Objetivos, condiciones de victoria y marcas impresas de los 21 niveles.

Un nivel se cumple cuando todos los parámetros del Operador están dentro de su
tolerancia y se mantienen así durante HOLD_SECONDS segundos.
draw_targets() dibuja sobre el lienzo las piezas impresas que usa cada nivel.
"""
import cv2
import numpy as np

HOLD_SECONDS = 2.0

# {(juego, nivel): {'targets': {clave: (valor, tolerancia)}, 'reveal': texto al ganar}}
GOALS = {
    (1, 0): {'targets': {'zoom': (6.0, 1.0), 'cx': (-0.75, 0.03), 'cy': (0.10, 0.03)},
             'reveal': 'Código revelado: 4 - 2 - 7'},
    (1, 1): {'targets': {'zoom': (20.0, 3.0), 'cx': (-0.7436, 0.02), 'cy': (0.1318, 0.02)},
             'reveal': 'Detalle puntual encontrado'},
    (1, 2): {'targets': {'zoom': (12.0, 2.0), 'cx': (-0.5, 0.05), 'cy': (0.0, 0.05), 'iter': (120, 15)},
             'reveal': 'Relieve alineado con el contorno'},
    (2, 0): {'targets': {'x': (-0.70, 0.05), 'y': (0.27, 0.05)},
             'reveal': 'Cerradura abierta'},
    (2, 1): {'targets': {'x': (-0.7269, 0.01), 'y': (0.1889, 0.01), 'iter': (100, 20)},
             'reveal': 'Encaje de alta precisión'},
    (2, 2): {'targets': {'x': (-0.40, 0.05), 'y': (0.60, 0.05), 'iter': (60, 20)},
             'reveal': 'Bloques esquivados'},
    (3, 0): {'targets': {'depth': (1, 0.5)}, 'reveal': 'Las 3 marcas están cubiertas'},
    (3, 1): {'targets': {'depth': (2, 0.5)}, 'reveal': '9 puntos de luz destapados'},
    (3, 2): {'targets': {'depth': (3, 0.5), 'escala': (0.9, 0.03)}, 'reveal': 'Zonas de peligro evitadas'},
    (4, 0): {'targets': {'n': (2, 0.5), 'largo': (1.0, 0.05)}, 'reveal': 'Puente unido'},
    (4, 1): {'targets': {'n': (3, 0.5), 'largo': (1.2, 0.05)}, 'reveal': 'Roca esquivada'},
    (4, 2): {'targets': {'n': (4, 0.5), 'largo': (1.0, 0.02)}, 'reveal': 'Puente de máxima precisión'},
    (5, 0): {'targets': {'depth': (4, 0.5), 'angulo': (0.6, 0.05)}, 'reveal': '2 dianas tocadas'},
    (5, 1): {'targets': {'depth': (5, 0.5), 'angulo': (0.45, 0.03)}, 'reveal': '3 dianas tocadas'},
    (5, 2): {'targets': {'depth': (6, 0.5), 'angulo': (0.35, 0.02)}, 'reveal': 'Dianas tocadas sin chocar con los muros'},
    (6, 0): {'targets': {'dobleces': (4, 0.5)}, 'reveal': 'Ruta corta completada'},
    (6, 1): {'targets': {'dobleces': (8, 0.5)}, 'reveal': 'Ruta media completada'},
    (6, 2): {'targets': {'dobleces': (16, 0.5)}, 'reveal': 'Sector vacío cableado'},
    (7, 0): {'targets': {'velocidad': (1.0, 0.2), 'sigma': (10.0, 0.5), 'rho': (28.0, 0.5)},
             'reveal': 'Aro grande atravesado'},
    (7, 1): {'targets': {'velocidad': (1.5, 0.2), 'sigma': (10.0, 0.5), 'rho': (28.0, 0.5)},
             'reveal': 'Dos aros enhebrados'},
    (7, 2): {'targets': {'velocidad': (2.2, 0.2), 'sigma': (10.0, 0.5), 'rho': (28.0, 0.3)},
             'reveal': 'Aros estrechos enhebrados'},
}


def check(game_id, level, params):
    """True si todos los parámetros del nivel están dentro de tolerancia."""
    spec = GOALS.get((game_id, level))
    if spec is None:
        return False
    for key, (target, tol) in spec['targets'].items():
        if key not in params or abs(float(params[key]) - target) > tol:
            return False
    return True


def reveal_text(game_id, level):
    spec = GOALS.get((game_id, level))
    return spec['reveal'] if spec else ''


def _sier_centers(depth):
    """Centros de las piezas del triángulo de Sierpinski (mismos vértices que renderers)."""
    tris = [(np.array([160.0, 16.0]), np.array([16.0, 304.0]), np.array([304.0, 304.0]))]
    for _ in range(depth):
        nxt = []
        for a, b, c in tris:
            ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
            nxt += [(a, ab, ca), (ab, b, bc), (ca, bc, c)]
        tris = nxt
    return [(a + b + c) / 3 for a, b, c in tris]


def _pt(p):
    return (int(p[0]), int(p[1]))


def draw_targets(img, game_id, level):
    """Devuelve una copia del lienzo con las piezas impresas de ese nivel dibujadas."""
    out = img.copy()
    if game_id == 2:
        cv2.circle(out, (160, 110), 35, (0, 255, 0), 2)
        cv2.rectangle(out, (150, 140), (170, 230), (0, 255, 0), 2)
        if level == 2:
            cv2.rectangle(out, (30, 60), (90, 120), (0, 0, 255), -1)
            cv2.rectangle(out, (230, 200), (290, 260), (0, 0, 255), -1)
    elif game_id == 3:
        if level == 0:
            for v in [(160, 16), (16, 304), (304, 304)]:
                cv2.circle(out, v, 10, (0, 255, 0), 2)
        elif level == 1:
            for c in _sier_centers(2):
                cv2.circle(out, _pt(c), 5, (255, 255, 255), -1)
        else:
            for c in _sier_centers(1):
                cv2.circle(out, _pt(c), 18, (0, 0, 255), 2)
    elif game_id == 4:
        cv2.line(out, (40, 120), (40, 200), (0, 255, 0), 4)
        cv2.line(out, (280, 120), (280, 200), (0, 255, 0), 4)
        if level >= 1:
            cv2.circle(out, (160, 250), 20, (128, 128, 128), -1)
    elif game_id == 5:
        dianas = [(80, 60), (160, 40), (240, 70)]
        for i, d in enumerate(dianas):
            if level == 0 and i == 2:
                continue
            cv2.circle(out, d, 12, (0, 0, 255), 2)
        if level == 2:
            cv2.rectangle(out, (120, 100), (130, 200), (128, 128, 128), -1)
            cv2.rectangle(out, (200, 120), (210, 220), (128, 128, 128), -1)
    elif game_id == 7:
        rings = [(160, 120, 40)] if level == 0 else [(100, 120, 35), (220, 120, 35)]
        if level == 2:
            rings = [(100, 120, 22), (220, 120, 22)]
        for x, y, r in rings:
            cv2.circle(out, (x, y), r, (255, 255, 255), 2)
    return out
