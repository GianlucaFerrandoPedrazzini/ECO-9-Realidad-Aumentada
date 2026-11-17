"""Objetivos, condiciones de victoria y piezas impresas de los 21 niveles.

Fuente unica de verdad: tools/generate_sheets.py (GAMES).
Las hojas impresas y el Explorador usan los mismos valores.

Un nivel se cumple cuando todos los parametros del Operador estan dentro de su
tolerancia y se mantienen asi durante HOLD_SECONDS segundos.
draw_targets() dibuja sobre el lienzo las piezas impresas de ese nivel.
"""
import cv2
import numpy as np

from tools.generate_sheets import GAMES

HOLD_SECONDS = 2.0
CANVAS = 320
SX = CANVAS / 19.0
SY = CANVAS / 16.0

# Tolerancia por parametro (margen de error permitido al Operador).
TOL = {
    'depth': 0.5, 'zoom': 0.3, 'angle': 3.0, 'angulo': 0.06,
    'cx': 0.03, 'cy': 0.03, 'c_re': 0.02, 'c_im': 0.02,
    'ratio': 0.03, 'sigma': 0.5, 'rho': 1.0, 'beta': 0.1,
    'iter': 1.0, 'x': 0.02, 'y': 0.02, 'n': 0.5, 'largo': 0.05,
    'dobleces': 0.5, 'velocidad': 0.2, 'escala': 0.05,
}

REVEAL = {
    (1, 0): 'Nivel 1 completado',
    (1, 1): 'Detalle puntual encontrado',
    (1, 2): 'Contorno alineado',
    (2, 0): 'Cerradura abierta',
    (2, 1): 'Bloques esquivados',
    (2, 2): 'Encaje de alta precisión',
    (3, 0): 'Las 3 marcas están cubiertas',
    (3, 1): '9 puntos de luz destapados',
    (3, 2): 'Zonas de peligro evitadas',
    (4, 0): 'Puente unido',
    (4, 1): 'Roca esquivada',
    (4, 2): 'Puente de máxima precisión',
    (5, 0): '2 dianas tocadas',
    (5, 1): '3 dianas tocadas',
    (5, 2): 'Dianas tocadas sin chocar con los muros',
    (6, 0): 'Ruta corta completada',
    (6, 1): 'Ruta media completada',
    (6, 2): 'Ruta larga completada',
    (7, 0): 'Aro grande atravesado',
    (7, 1): 'Dos aros enhebrados',
    (7, 2): 'Aros estrechos enhebrados',
}

GOALS = {}
for _gid, _game in GAMES.items():
    for _i, _lvl in enumerate(_game['levels']):
        GOALS[(_gid, _i)] = {
            'targets': {k: (v, TOL.get(k, 0.05)) for k, v in _lvl['target'].items()},
            'reveal': REVEAL.get((_gid, _i), ''),
        }


def check(game_id, level, params):
    """True si todos los parametros del nivel estan dentro de tolerancia."""
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


def _px(x, y):
    return (int(x * SX), int(y * SY))


def _r(r):
    return max(1, int(r * (SX + SY) / 2))


def draw_targets(img, game_id, level):
    """Devuelve una copia del lienzo con las piezas impresas de ese nivel."""
    out = img.copy()
    game = GAMES.get(game_id)
    if game is None or not 0 <= level < len(game['levels']):
        return out

    green, red, white = (0, 255, 0), (0, 0, 255), (255, 255, 255)
    for p in game['levels'][level]['pieces']:
        kind = p[0]
        if kind == 'circle':
            _, x, y, r, _w = p
            cv2.circle(out, _px(x, y), _r(r), green, 2)
        elif kind == 'disk':
            _, x, y, r = p
            cv2.circle(out, _px(x, y), _r(r), white, -1)
        elif kind == 'rect':
            _, x, y, w, h = p
            cv2.rectangle(out, _px(x, y), _px(x + w, y + h), green, 2)
        elif kind == 'block':
            _, x, y, w, h = p
            cv2.rectangle(out, _px(x, y), _px(x + w, y + h), red, -1)
        elif kind == 'cross':
            _, x, y, w, h = p
            cv2.rectangle(out, _px(x, y), _px(x + w, y + h), red, 2)
            cv2.line(out, _px(x, y), _px(x + w, y + h), red, 1)
            cv2.line(out, _px(x, y + h), _px(x + w, y), red, 1)
        elif kind == 'poly':
            pts = np.array([_px(x, y) for x, y in p[1]], dtype='int32')
            cv2.polylines(out, [pts], True, green, 2)

        # 'text' y 'code' son solo para leer en la hoja; no se dibujan en el lienzo.
    return out