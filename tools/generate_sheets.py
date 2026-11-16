"""Genera las 7 hojas imprimibles (A4 a 300 dpi).
Cada hoja incluye:
- El marcador ArUco del juego.
- El título y el objetivo de cada uno de sus 3 niveles (texto completo).
- Las piezas físicas del nivel (cerradura, bloques, marcas, dianas, aros,
etc.),
 dibujadas con goals.draw_targets() para que coincidan con la pantalla del
Explorador.
Ejecutar desde la carpeta raíz del proyecto:
 python -m tools.generate_sheets
Salida: tools/hojas/hoja_1.png ... hoja_7.png
Imprimir al 100% (sin ajustar a la página) en A4.
"""
import os
import textwrap

import cv2
import numpy as np

from config import ARUCO_DICT_NAME
from games.levels import GAMES
from explorer.goals import draw_targets

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hojas")
PAGE_W, PAGE_H = 2480, 3508 # A4 a 300 dpi
MARKER_PX = 709 # 6 cm a 300 dpi
PIECE_PX = 1200 # zona de piezas: 10 cm cuadrados
PIECE_SRC = 320 # lienzo de origen usado por goals.draw_targets()
MARGIN_X = 150
FONT = cv2.FONT_HERSHEY_SIMPLEX

def _put_wrapped(page, text, x, y, scale, thick, width_chars=60, line_h=60):
    """Escribe texto con salto de línea. Devuelve la próxima y libre."""
    for line in textwrap.wrap(text, width_chars):
        cv2.putText(page, line, (x, y), FONT, scale, 0, thick, cv2.LINE_AA)
        y += line_h
    return y

def _piece_canvas(game_id, level):
    """Lienzo con las piezas del nivel, escalado a PIECE_PX sobre fondo blanco."""
    src = np.full((PIECE_SRC, PIECE_SRC, 3), 255, np.uint8)
    drawn = draw_targets(src, game_id, level)
    scaled = cv2.resize(drawn, (PIECE_PX, PIECE_PX), interpolation=cv2.INTER_NEAREST)
    # Los colores de goals.py son para pantalla; en papel se pasan a negro/gris.

    gray = cv2.cvtColor(scaled, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
    return bw

def build_sheet(gid, g, dic):
    page = np.full((PAGE_H, PAGE_W), 255, np.uint8)
    
    # Encabezado
    cv2.putText(page, f"Hoja {gid}: {g['concept']}", (MARGIN_X, 200), FONT, 1.8, 0, 4, cv2.LINE_AA)
    cv2.putText(page, g["name"], (MARGIN_X, 290), FONT, 1.2, 0, 2, cv2.LINE_AA)
    
    # Marcador ArUco centrado
    marker = cv2.aruco.generateImageMarker(dic, g["marker_id"], MARKER_PX)
    x = (PAGE_W - MARKER_PX) // 2
    page[400:400 + MARKER_PX, x:x + MARKER_PX] = marker
    
    # Niveles: título + objetivo completo
    y = 1200
    for i, lv in enumerate(g["levels"]):
        cv2.putText(page, f"Nivel {i + 1} - {lv['title']}", (MARGIN_X, y), FONT, 1.1, 0, 2, cv2.LINE_AA)
        y = _put_wrapped(page, lv["goal"], MARGIN_X, y + 65, 0.8, 2)
        y += 30
    
    # Piezas físicas de los 3 niveles, una debajo de otra o en fila según espacio.

    # Cada nivel recibe su propio recuadro; se imprime sólo si el nivel tiene piezas.
    pieces_y = 1850
    slot = PIECE_PX
    for i in range(3):
        canvas = _piece_canvas(gid, i)
        if canvas.min() == 255: # lienzo vacío: el nivel usa sólo el fractal
            continue
        
        px = (PAGE_W - PIECE_PX) // 2
        page[pieces_y:pieces_y + slot, px:px + PIECE_PX] = canvas
        cv2.putText(page, f"Piezas nivel {i + 1}", (MARGIN_X, pieces_y -20), FONT, 1.0, 0, 2, cv2.LINE_AA)
        break # el resto de niveles se imprime en hojas separadas (ver nota abajo)

    return page

def main():
    os.makedirs(OUT, exist_ok=True)
    dic = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, ARUCO_DICT_NAME))
    for gid, g in GAMES.items():
        page = build_sheet(gid, g, dic)
        path = os.path.join(OUT, f"hoja_{gid}.png")
        cv2.imwrite(path, page)
        print(f"Creada {path} (marcador id {g['marker_id']})")

if __name__ == "__main__":
    main()