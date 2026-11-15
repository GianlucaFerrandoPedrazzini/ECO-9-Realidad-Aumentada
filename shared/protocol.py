"""Formato de mensajes por socket: JSON terminado en salto de línea."""
import json


def encode(msg):
    """Convierte un diccionario en bytes listos para enviar."""
    return (json.dumps(msg) + "\n").encode("utf-8")


def decode(line):
    """Convierte una línea de bytes en diccionario. Devuelve None si no es válida."""
    try:
        return json.loads(line.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
