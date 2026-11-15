"""Aplicación del Explorador: cámara, detección ArUco, proyección sobre el marcador
y servidor de sockets que recibe órdenes del Operador."""
import socket
import threading

import cv2
import numpy as np

from config import ARUCO_DICT_NAME, CAMERA_INDEX, NETWORK_HOST, NETWORK_PORT
from explorer.renderers import render
from games.levels import GAMES
from shared import protocol

# Estado compartido entre el hilo de red y el hilo de video
state = {"game": 1, "params": {}, "level": 0}
lock = threading.Lock()

def _defaults(game_id):
    return {k: v[3] for k, v in GAMES[game_id]["params"].items()}

def apply_message(msg):
    """Actualiza el estado según el mensaje recibido del Operador."""
    kind = msg.get("type")
    with lock:
        if kind == "select":
            g = int(msg["game"])
            if g in GAMES:
                state["game"] = g
                state["params"] = _defaults(g)
                state["level"] = int(msg.get("level", 0))
        elif kind == "param":
            if msg["key"] in GAMES[state["game"]]["params"]:
                state["params"][msg["key"]] = float(msg["value"])
        elif kind == "level":
            state["level"] = int(msg["level"])

def handle_client(conn):
    """Lee mensajes JSON terminados en salto de línea."""
    buf = b""
    with conn:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buf += data
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                msg = protocol.decode(line)
                if msg:
                    apply_message(msg)

def serve():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((NETWORK_HOST, NETWORK_PORT))
    srv.listen(1)
    while True:
        conn, _ = srv.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

def make_detector():
    dic = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, ARUCO_DICT_NAME))
    return cv2.aruco.ArucoDetector(dic, cv2.aruco.DetectorParameters())

def project(frame, img, quad):
    """Deforma la imagen del fractal sobre las 4 esquinas del marcador detectado."""
    h, w = img.shape[:2]
    fh, fw = frame.shape[:2]
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    H, _ = cv2.findHomography(src, quad.astype(np.float32))
    if H is None:
        return frame
    warped = cv2.warpPerspective(img, H, (fw, fh))
    mask = cv2.warpPerspective(np.full((h, w), 255, np.uint8), H, (fw, fh)) > 0
    blended = cv2.addWeighted(frame, 0.35, warped, 0.9, 0)
    return np.where(mask[..., None], blended, frame)

def main():
    with lock:
        state["params"] = _defaults(state["game"])
    threading.Thread(target=serve, daemon=True).start()
    cap = cv2.VideoCapture(CAMERA_INDEX)
    detector = make_detector()
    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        with lock:
            game, params = state["game"], dict(state["params"])
        corners, ids, _ = detector.detectMarkers(frame)
        if ids is not None:
            for quad, mid in zip(corners, ids.flatten()):
                if mid == GAMES[game]["marker_id"]:
                    img = render(game, params, frame_idx)
                    frame = project(frame, img, quad.reshape(4, 2))
        frame_idx += 1
        cv2.imshow("Explorador", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
