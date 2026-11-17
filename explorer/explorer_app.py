"""Aplicación del Explorador: cámara, detección ArUco, proyección sobre el marcador,
evaluación de objetivos (victoria) y servidor de sockets que recibe órdenes del Operador."""
import socket
import threading
import time
import unicodedata

import cv2
import numpy as np

from config import ARUCO_DICT_NAME, CAMERA_INDEX, NETWORK_HOST, NETWORK_PORT
from explorer import goals
from explorer.renderers import render
from games.levels import GAMES
from shared import protocol

FONT = cv2.FONT_HERSHEY_SIMPLEX

state = {'game': 1, 'level': 0, 'params': {}, 'won': False, 'hold_start': None, 'conn': None}
lock = threading.Lock()


def _defaults(game_id):
    return {k: v[3] for k, v in GAMES[game_id]['params'].items()}


def _reset_progress():
    state['won'] = False
    state['hold_start'] = None


def apply_message(msg):
    """Actualiza el estado según el mensaje recibido del Operador."""
    kind = msg.get('type')
    with lock:
        if kind == 'select':
            g = int(msg['game'])
            if g in GAMES:
                state['game'] = g
                state['params'] = _defaults(g)
                state['level'] = int(msg.get('level', 0))
                _reset_progress()
        elif kind == 'param':
            if msg['key'] in GAMES[state['game']]['params']:
                state['params'][msg['key']] = float(msg['value'])
        elif kind == 'level':
            state['level'] = int(msg['level'])
            _reset_progress()


def _notify(msg):
    """Envía un mensaje al Operador (debe llamarse SIN el lock tomado)."""
    with lock:
        conn = state['conn']
    if conn is None:
        return
    try:
        conn.sendall(protocol.encode(msg))
    except OSError:
        pass


def handle_client(conn):
    """Lee mensajes JSON terminados en salto de línea."""
    buf = b''
    with lock:
        state['conn'] = conn
    with conn:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            buf += data
            while b'\n' in buf:
                line, buf = buf.split(b'\n', 1)
                msg = protocol.decode(line)
                if msg:
                    apply_message(msg)
    with lock:
        state['conn'] = None


def serve():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((NETWORK_HOST, NETWORK_PORT))
    srv.listen(1)
    while True:
        conn, _ = srv.accept()
        threading.Thread(target=handle_client, args=(conn,), daemon=True).start()


def update_progress(game, level, params):
    """Evalúa el objetivo. Devuelve (estado, avance): 'playing', 'holding' o 'won'."""
    now = time.time()
    notify_msg = None
    with lock:
        if state['won']:
            return 'won', 1.0
        if not goals.check(game, level, params):
            state['hold_start'] = None
            return 'playing', 0.0
        if state['hold_start'] is None:
            state['hold_start'] = now
        held = now - state['hold_start']
        if held < goals.HOLD_SECONDS:
            return 'holding', held / goals.HOLD_SECONDS
        state['won'] = True
        notify_msg = {'type': 'won', 'game': game, 'level': level}
    if notify_msg:
        _notify(notify_msg)
    return 'won', 1.0


def _ascii(text):
    """Quita acentos: las fuentes Hershey de OpenCV no muestran tildes."""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()


def _hud(frame, status, progress, game, level):
    if status == 'won':
        cv2.putText(frame, 'Nivel completado!', (20, 40), FONT, 1.0, (0, 255, 0), 2)
        cv2.putText(frame, _ascii(goals.reveal_text(game, level)), (20, 75), FONT, 0.7, (255, 255, 255), 2)
    elif status == 'holding':
        cv2.putText(frame, 'Manten la posicion... %d%%' % int(progress * 100), (20, 40),
                    FONT, 0.7, (0, 255, 255), 2)


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
        state['params'] = _defaults(state['game'])
    threading.Thread(target=serve, daemon=True).start()
    cap = cv2.VideoCapture(CAMERA_INDEX)
    detector = make_detector()
    frame_idx = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        with lock:
            game, level, params = state['game'], state['level'], dict(state['params'])
        status, progress = update_progress(game, level, params)
        corners, ids, _ = detector.detectMarkers(frame)
        if ids is not None:
            for quad, mid in zip(corners, ids.flatten()):
                if mid == GAMES[game]['marker_id']:
                    img = render(game, params, frame_idx)
                    img = goals.draw_targets(img, game, level)
                    frame = project(frame, img, quad.reshape(4, 2))
        _hud(frame, status, progress, game, level)
        frame_idx += 1
        cv2.imshow('Explorador', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()