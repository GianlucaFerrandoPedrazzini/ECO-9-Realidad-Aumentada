"""Genera las 7 hojas imprimibles (A4 a 300 dpi) con su marcador ArUco y las instrucciones.
Ejecutar: python -m tools.generate_sheets"""
import os

import cv2
import numpy as np

from config import ARUCO_DICT_NAME
from games.levels import GAMES

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hojas")
PAGE_W, PAGE_H = 2480, 3508   # A4 a 300 dpi
MARKER_PX = 709               # 6 cm a 300 dpi
FONT = cv2.FONT_HERSHEY_SIMPLEX

def main():
    os.makedirs(OUT, exist_ok=True)
    dic = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, ARUCO_DICT_NAME))
    for gid, g in GAMES.items():
        page = np.full((PAGE_H, PAGE_W), 255, np.uint8)
        cv2.putText(page, f"Hoja {gid}: {g['concept']}", (150, 200), FONT, 1.8, 0, 4, cv2.LINE_AA)
        cv2.putText(page, g["name"], (150, 290), FONT, 1.2, 0, 2, cv2.LINE_AA)
        marker = cv2.aruco.generateImageMarker(dic, g["marker_id"], MARKER_PX)
        x = (PAGE_W - MARKER_PX) // 2
        page[400:400 + MARKER_PX, x:x + MARKER_PX] = marker
        y = 1300
        for i, lv in enumerate(g["levels"], 1):
            cv2.putText(page, f"Nivel {i} - {lv['title']}", (150, y), FONT, 1.1, 0, 2, cv2.LINE_AA)
            cv2.putText(page, lv["goal"][:80], (150, y + 70), FONT, 0.8, 0, 2, cv2.LINE_AA)
            y += 260
        cv2.imwrite(os.path.join(OUT, f"hoja_{gid}.png"), page)
        print(f"Creada hoja_{gid}.png (marcador id {g['marker_id']})")

if __name__ == "__main__":
    main()
