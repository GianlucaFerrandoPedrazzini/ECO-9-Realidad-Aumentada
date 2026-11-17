"""Genera las 21 hojas A4 imprimibles (7 juegos x 3 niveles).

Uso (desde la carpeta raiz del proyecto):
    python -m tools.generate_sheets

Salida:
    tools/hojas/juego{J}_nivel{N}.png  (300 dpi, imprimir al 100 %, sin ajustar)
    tools/hojas/valores.json           (valores objetivo, para goals.py)
"""
import json
import os
import textwrap

import cv2
from PIL import Image, ImageDraw, ImageFont

DPI = 300
PAGE_W_CM, PAGE_H_CM = 21.0, 29.7
BLACK, WHITE, GRAY = (0, 0, 0), (255, 255, 255), (150, 150, 150)
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hojas")
ARUCO_DICT = cv2.aruco.DICT_4X4_50
MARKER_CM = 4.0
AREA_X, AREA_Y = 1.0, 6.0
AREA_W, AREA_H = 19.0, 16.0

LABELS = {
    "depth": "profundidad", "zoom": "zoom", "angle": "angulo", "angulo": "angulo",
    "cx": "centro x", "cy": "centro y", "c_re": "c real", "c_im": "c imaginaria",
    "ratio": "factor de escala", "sigma": "sigma", "rho": "rho", "beta": "beta",
    "iter": "iteraciones", "x": "parametro x", "y": "parametro y",
    "n": "iteraciones", "largo": "largo", "dobleces": "dobleces",
    "velocidad": "velocidad", "escala": "escala",
}


def cm(v):
    return int(round(v * DPI / 2.54))


def P(x, y):
    """Convierte coordenadas del area de dibujo (cm) a pixeles de la hoja."""
    return (cm(AREA_X + x), cm(AREA_Y + y))


def load_font(px):
    for name in ("DejaVuSans.ttf", "Arial.ttf", "arial.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            pass
    return ImageFont.load_default(size=px)


F_TITLE = load_font(105)
F_TEXT = load_font(54)
F_SMALL = load_font(40)
F_DIGIT = load_font(120)


def grid(n, obstacles, danger):
    """Cuadricula n x n con obstaculos (relleno) y casillas de peligro (aspa)."""
    cell = AREA_H / n
    x0 = (AREA_W - n * cell) / 2
    out = []
    for r in range(n):
        for c in range(n):
            x, y = x0 + c * cell, r * cell
            out.append(("rect", x, y, cell, cell))
            if (c, r) in obstacles:
                out.append(("block", x + 0.1, y + 0.1, cell - 0.2, cell - 0.2))
            if (c, r) in danger:
                out.append(("cross", x + 0.1, y + 0.1, cell - 0.2, cell - 0.2))
    return out


TRIANGLE = [(9.5, 1.0), (1.5, 14.5), (17.5, 14.5)]
MARKS = [("disk", 9.5, 1.0, 0.25), ("disk", 1.5, 14.5, 0.25), ("disk", 17.5, 14.5, 0.25)]
POINTS9 = [("disk", x, y, 0.2) for x in (6.5, 9.5, 12.5) for y in (7.0, 9.5, 12.0)]

GAMES = {
    1: {"name": "Mandelbrot", "levels": [
        {"obj": "Ajusta zoom, centro X e iteraciones a los valores de la hoja.",
         "target": {"zoom": 4.0, "cx": -0.75, "iter": 60},
         "series": "Iteraciones: 2, 4, 8, 16 (se duplica en cada paso)",
         "pieces": [("text", 5.0, 6.0, "Zoom, centro X, iteraciones")]},
        {"obj": "Ajusta zoom, centro X y centro Y al detalle marcado.",
         "target": {"zoom": 8.0, "cx": -0.75, "cy": 0.10},
         "series": "Iteraciones: 2, 4, 8 (duplicacion en cada nivel de detalle)",
         "pieces": [("circle", 9.5, 8.0, 5.0, 0.15), ("text", 5.0, 14.2, "Zona de detalle")]},
        {"obj": "Los mismos valores del nivel 2 con mas zoom, antes de que se acabe el tiempo.",
         "target": {"zoom": 12.0, "cx": -0.75, "cy": 0.10},
         "series": "Iteraciones: 2, 4, 8, 16, 32",
         "pieces": [("text", 5.0, 6.0, "Igual al nivel 2, mas zoom")]},
    ]},
    2: {"name": "Julia", "levels": [
        {"obj": "Ajusta los parametros X e Y para encajar la cerradura.",
         "target": {"x": -0.80, "y": 0.15, "iter": 40},
         "series": "Serie de pasos: 1, 2, 4, 8 (el contorno se duplica por nivel)",
         "pieces": [("circle", 9.5, 7.0, 2.2, 0.15), ("circle", 9.5, 7.0, 1.0, 0.15)]},
        {"obj": "Encaja la cerradura con mayor precision.",
         "target": {"x": -0.40, "y": 0.60, "iter": 80},
         "series": "Serie de pasos: 1, 2, 4, 8, 16",
         "pieces": [("circle", 9.5, 7.0, 2.2, 0.15), ("circle", 9.5, 7.0, 1.0, 0.15)]},
        {"obj": "Esquiva los bloques laterales con los nuevos valores.",
         "target": {"x": 0.28, "y": 0.01, "iter": 100},
         "series": "Serie de pasos: 1, 2, 4, 8, 16, 32",
         "pieces": [("circle", 9.5, 7.0, 1.6, 0.12), ("rect", 4.0, 11.0, 1.2, 4.0),
                    ("rect", 13.8, 11.0, 1.2, 4.0)]},
    ]},
    3: {"name": "Sierpinski", "levels": [
        {"obj": "Ajusta la profundidad para cubrir las 3 marcas.",
         "target": {"depth": 3},
         "series": "Triangulos: 1, 3, 9, 27",
         "pieces": [("poly", TRIANGLE)] + MARKS},
        {"obj": "Ajusta la profundidad para destapar exactamente 9 puntos de luz.",
         "target": {"depth": 4},
         "series": "Triangulos: 1, 3, 9, 27, 81",
         "pieces": [("poly", TRIANGLE)] + MARKS + POINTS9},
        {"obj": "Elegi la profundidad correcta evitando las zonas de peligro.",
         "target": {"depth": 5},
         "series": "Triangulos: 1, 3, 9, 27, 81, 243",
         "pieces": [("poly", TRIANGLE)] + MARKS + POINTS9 +
                   [("cross", 3.0, 11.0, 2.6, 2.2), ("cross", 8.2, 11.0, 2.6, 2.2),
                    ("cross", 13.4, 11.0, 2.6, 2.2)]},
    ]},
    4: {"name": "Koch", "levels": [
        {"obj": "Une los dos acantilados ajustando iteraciones y largo.",
         "target": {"n": 2, "largo": 1.0},
         "series": "Segmentos: 4, 16, 64",
         "pieces": [("poly", [(0, 4), (7, 4), (7, 16), (0, 16)]),
                    ("poly", [(12, 4), (19, 4), (19, 16), (12, 16)]),
                    ("circle", 9.5, 9.0, 1.5, 0.15)]},
        {"obj": "Esquivá la roca con los nuevos valores.",
         "target": {"n": 3, "largo": 1.3},
         "series": "Segmentos: 4, 16, 64, 256",
         "pieces": [("poly", [(0, 4), (6, 4), (6, 16), (0, 16)]),
                    ("poly", [(13, 4), (19, 4), (19, 16), (13, 16)]),
                    ("circle", 9.5, 5.0, 1.2, 0.15)]},
        {"obj": "Ajustá con la mayor precision posible.",
         "target": {"n": 4, "largo": 1.5},
         "series": "Segmentos: 4, 16, 64, 256, 1024",
         "pieces": [("poly", [(0, 4), (8, 4), (8, 16), (0, 16)]),
                    ("poly", [(11, 4), (19, 4), (19, 16), (11, 16)]),
                    ("circle", 9.5, 10.0, 1.2, 0.15)]},
    ]},
    5: {"name": "Pitagoras", "levels": [
        {"obj": "Ajustá profundidad y ángulo para tocar 2 dianas.",
         "target": {"depth": 6, "angulo": 0.78},
         "series": "Serie: 1 + 0.7 + 0.49 + 0.343 + ...",
         "pieces": [("circle", 5.0, 8.0, 1.8, 0.15), ("circle", 14.0, 8.0, 1.8, 0.15),
                    ("rect", 2.0, 13.0, 4.0, 1.0), ("rect", 13.0, 13.0, 4.0, 1.0)]},
        {"obj": "Tocá 3 dianas a distintas alturas.",
         "target": {"depth": 7, "angulo": 0.70},
         "series": "Serie: 1 + 0.6 + 0.36 + 0.216 + ...",
         "pieces": [("circle", 3.0, 6.0, 1.6, 0.15), ("circle", 9.5, 4.0, 1.6, 0.15),
                    ("circle", 16.0, 6.0, 1.6, 0.15), ("rect", 8.0, 11.0, 3.0, 1.0)]},
        {"obj": "Tocá las dianas esquivando los muros.",
         "target": {"depth": 8, "angulo": 0.87},
         "series": "Serie: 1 + 0.75 + 0.5625 + 0.4219 + ...",
         "pieces": [("circle", 5.0, 8.0, 1.5, 0.15), ("circle", 14.0, 8.0, 1.5, 0.15),
                    ("rect", 9.0, 6.0, 0.8, 8.0)]},
    ]},
    6: {"name": "Dragon", "levels": [
        {"obj": "Completá la ruta evitando los obstaculos.",
         "target": {"dobleces": 10},
         "series": "Pasos: 2, 4, 8, 16 (doblado en cada iteracion)",
         "pieces": grid(4, {(1, 1), (2, 2)}, {(3, 0), (0, 3)})},
        {"obj": "Completá la ruta evitando obstaculos y casillas de peligro.",
         "target": {"dobleces": 12},
         "series": "Pasos: 2, 4, 8, 16, 32",
         "pieces": grid(5, {(1, 1), (3, 2), (2, 4)}, {(4, 0), (0, 4)})},
        {"obj": "Completá la ruta larga.",
         "target": {"dobleces": 14},
         "series": "Pasos: 2, 4, 8, 16, 32, 64",
         "pieces": grid(6, {(1, 1), (4, 2), (2, 4), (5, 5)}, {(5, 0), (0, 5), (3, 3)})},
    ]},
    7: {"name": "Lorenz", "levels": [
        {"obj": "Ajustá los parametros del atractor para atravesar el aro.",
         "target": {"sigma": 12.0, "rho": 30.0, "beta": 2.5},
         "series": "Parametros: sigma 10, rho 28, beta 8/3",
         "pieces": [("circle", 9.5, 8.0, 5.0, 0.2)]},
        {"obj": "Atravesá los dos aros.",
         "target": {"sigma": 10.0, "rho": 24.0, "beta": 2.67},
         "series": "Parametros: sigma 10, rho 24, beta 8/3",
         "pieces": [("circle", 5.5, 8.0, 3.5, 0.2), ("circle", 13.5, 8.0, 3.5, 0.2)]},
        {"obj": "Atravesá los dos aros estrechos.",
         "target": {"sigma": 10.0, "rho": 35.0, "beta": 2.0},
         "series": "Parametros: sigma 10, rho 35, beta 2.0",
         "pieces": [("circle", 5.0, 8.0, 3.2, 0.08), ("circle", 14.0, 8.0, 3.2, 0.08)]},
    ]},
}


def draw_piece(d, p):
    kind = p[0]
    if kind == "circle":
        _, x, y, r, w = p
        d.ellipse([P(x - r, y - r), P(x + r, y + r)], outline=BLACK, width=cm(w))
    elif kind == "disk":
        _, x, y, r = p
        d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=BLACK)
    elif kind == "rect":
        _, x, y, w, h = p
        d.rectangle([P(x, y), P(x + w, y + h)], outline=BLACK, width=cm(0.12))
    elif kind == "block":
        _, x, y, w, h = p
        d.rectangle([P(x, y), P(x + w, y + h)], fill=BLACK)
    elif kind == "cross":
        _, x, y, w, h = p
        d.rectangle([P(x, y), P(x + w, y + h)], outline=BLACK, width=cm(0.12))
        d.line([P(x, y), P(x + w, y + h)], fill=BLACK, width=cm(0.08))
        d.line([P(x, y + h), P(x + w, y)], fill=BLACK, width=cm(0.08))
    elif kind == "poly":
        pts = [P(x, y) for x, y in p[1]]
        d.line(pts + [pts[0]], fill=BLACK, width=cm(0.12))
    elif kind == "text":
        _, x, y, s = p
        d.text(P(x, y), s, fill=BLACK, font=F_SMALL)
    elif kind == "code":
        _, x, y, code = p
        for i, digit in enumerate(code.split("-")):
            bx = x + i * 2.6
            d.rectangle([P(bx, y), P(bx + 2.0, y + 2.4)], outline=BLACK, width=cm(0.12))
            d.text(P(bx + 1.0, y + 1.2), digit, fill=BLACK, font=F_DIGIT, anchor="mm")


def make_marker(game_id):
    dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    img = cv2.aruco.generateImageMarker(dictionary, game_id, cm(MARKER_CM))
    return Image.fromarray(img).convert("RGB")


def render(game_id, game, num, level):
    sheet = Image.new("RGB", (cm(PAGE_W_CM), cm(PAGE_H_CM)), WHITE)
    d = ImageDraw.Draw(sheet)

    d.text((cm(1.0), cm(0.8)), f"Juego {game_id}: {game['name']} - Nivel {num}",
           fill=BLACK, font=F_TITLE)
    sheet.paste(make_marker(game_id), (cm(16.5), cm(1.0)))

    d.rectangle([cm(AREA_X), cm(AREA_Y), cm(AREA_X + AREA_W), cm(AREA_Y + AREA_H)],
                outline=GRAY, width=cm(0.03))
    for p in level["pieces"]:
        draw_piece(d, p)

    y = 23.0
    for line in textwrap.wrap("Objetivo: " + level["obj"], 62):
        d.text((cm(1.0), cm(y)), line, fill=BLACK, font=F_TEXT)
        y += 0.75
    y += 0.3
    values = "   ".join(f"{LABELS.get(k, k)} = {v}" for k, v in level["target"].items())
    d.text((cm(1.0), cm(y)), "Valores: " + values, fill=BLACK, font=F_TEXT)
    y += 0.75
    d.text((cm(1.0), cm(y)), level["series"], fill=BLACK, font=F_TEXT)
    y += 0.9
    d.text((cm(1.0), cm(y)),
           f"Marcador ArUco id {game_id}  -  Imprimir al 100 %, sin ajustar a pagina",
           fill=GRAY, font=F_SMALL)
    return sheet


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    export = {}
    for game_id, game in GAMES.items():
        for num, level in enumerate(game["levels"], start=1):
            name = f"juego{game_id}_nivel{num}.png"
            render(game_id, game, num, level).save(os.path.join(OUT_DIR, name), dpi=(DPI, DPI))
            export[f"J{game_id}N{num}"] = level["target"]
            print("OK", name)
    with open(os.path.join(OUT_DIR, "valores.json"), "w", encoding="utf-8") as f:
        json.dump(export, f, ensure_ascii=False, indent=2)
    print(f"\n21 hojas en {OUT_DIR}")


if __name__ == "__main__":
    main()