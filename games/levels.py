"""Definición de los 7 juegos y sus 3 niveles.

Cada parámetro del panel del Operador tiene la forma:
    clave: (etiqueta, mínimo, máximo, valor_inicial, resolución_del_slider)
"""

def _level(title, goal, time=None):
    return {"title": title, "goal": goal, "time": time}

GAMES = {
    1: {
        "name": "La Cifradora de Papel",
        "concept": "Conjunto de Mandelbrot",
        "marker_id": 1,
        "params": {
            "zoom": ("Zoom", 1.0, 40.0, 1.0, 0.1),
            "cx": ("Centro X", -2.0, 1.0, -0.5, 0.01),
            "cy": ("Centro Y", -1.5, 1.5, 0.0, 0.01),
            "iter": ("Iteraciones", 10, 150, 40, 1),
        },
        "levels": [
            _level("Ajuste básico", "Ajusta zoom, centro X e iteraciones a los valores de la hoja."),
            _level("Detalle puntual", "Ajusta zoom, centro X y centro Y al detalle marcado."),
            _level("Contorno sombreado", "Los mismos valores del nivel 2 con más zoom, antes de que se acabe el tiempo.", 120),
        ],
        "series": "Para cada píxel se evalúa si z(n+1) = z(n)^2 + c queda acotada (convergencia, color oscuro) o escapa a infinito (divergencia, color brillante).",
    },
    2: {
        "name": "La Llave Cambiaformas",
        "concept": "Conjunto de Julia",
        "marker_id": 2,
        "params": {
            "x": ("Parámetro X", -1.5, 1.5, -0.7, 0.01),
            "y": ("Parámetro Y", -1.5, 1.5, 0.27, 0.01),
            "iter": ("Iteraciones", 10, 150, 60, 1),
        },
        "levels": [
            _level("Encaje simple", "Ajusta los parámetros X e Y para encajar la cerradura."),
            _level("Alta precisión", "Encaja la cerradura con mayor precisión."),
            _level("Bloques de bloqueo", "Esquiva los bloques laterales con los nuevos valores, antes de que se acabe el tiempo.", 120),
        ],
        "series": "El valor inicial (semilla) altera el resultado de la serie: un cambio pequeño produce una geometría distinta.",
    },
    3: {
        "name": "La Pirámide Encajable",
        "concept": "Triángulo de Sierpinski",
        "marker_id": 3,
        "params": {
            "depth": ("Profundidad", 1, 5, 1, 1),
            "escala": ("Escala", 0.5, 1.0, 0.9, 0.01),
        },
        "levels": [
            _level("Tres marcas", "Ajusta la profundidad para cubrir las 3 marcas."),
            _level("Nueve puntos", "Ajusta la profundidad para destapar exactamente 9 puntos de luz."),
            _level("Zonas de peligro", "Elegí la profundidad correcta evitando las zonas de peligro, antes de que se acabe el tiempo.", 120),
        ],
        "series": "Multiplicación de piezas 1 → 3 → 9 → 27 mientras el área de cada pieza se reduce a (1/4)^n.",
    },
    4: {
        "name": "El Puente de Papel",
        "concept": "Copo de nieve de Koch",
        "marker_id": 4,
        "params": {
            "n": ("Iteraciones", 0, 4, 1, 1),
            "largo": ("Largo del puente", 0.5, 1.5, 1.0, 0.01),
        },
        "levels": [
            _level("Acantilados rectos", "Une los dos acantilados ajustando iteraciones y largo."),
            _level("Acantilados desalineados", "Esquivá la roca con los nuevos valores."),
            _level("Máxima precisión", "Ajustá con la mayor precisión posible, antes de que se acabe el tiempo.", 120),
        ],
        "series": "El perímetro P(n) = 3·(4/3)^n diverge a infinito, mientras el área queda acotada.",
    },
    5: {
        "name": "El Árbol de la Tarjeta",
        "concept": "Árbol de Pitágoras",
        "marker_id": 5,
        "params": {
            "depth": ("Niveles de ramas", 1, 8, 3, 1),
            "angulo": ("Ángulo de ramas", 0.1, 1.2, 0.6, 0.01),
        },
        "levels": [
            _level("Dos dianas", "Ajustá profundidad y ángulo para tocar 2 dianas."),
            _level("Tres dianas", "Tocá 3 dianas a distintas alturas."),
            _level("Muros de bloqueo", "Tocá las dianas esquivando los muros, antes de que se acabe el tiempo.", 120),
        ],
        "series": "Serie geométrica decreciente 1 + 0.7 + 0.49 + ... que converge a una altura finita.",
    },
    6: {
        "name": "El Cableado en Cuadrícula",
        "concept": "Curva del dragón",
        "marker_id": 6,
        "params": {
            "dobleces": ("Cantidad de dobleces", 1, 16, 4, 1),
        },
        "levels": [
            _level("Ruta corta", "Completá la ruta evitando los obstáculos."),
            _level("Ruta media", "Completá la ruta evitando los obstáculos y casillas de peligro."),
            _level("Sector vacío", "Completá la ruta larga, antes de que se acabe el tiempo.", 120),
        ],
        "series": "Secuencia de giros L/R que duplica y revierte en cada paso: S(n+1) = S(n) + R + revertir_y_complementar(S(n)).",
    },
    7: {
        "name": "El Atractor del Caos",
        "concept": "Atractor de Lorenz",
        "marker_id": 7,
        "params": {
            "sigma": ("Sigma", 5.0, 20.0, 10.0, 0.1),
            "rho": ("Rho", 20.0, 35.0, 28.0, 0.1),
            "beta": ("Beta", 1.0, 4.0, 2.67, 0.01),
            "velocidad": ("Velocidad", 0.1, 3.0, 1.0, 0.1),
        },
        "levels": [
            _level("Aro grande", "Ajustá los parámetros del atractor para atravesar el aro."),
            _level("Dos aros", "Atravesá los dos aros."),
            _level("Aros estrechos", "Atravesá los dos aros estrechos, antes de que se acabe el tiempo.", 120),
        ],
        "series": "Serie temporal caótica: cada punto deriva del anterior, no se repite y permanece acotada (efecto mariposa).",
    },
}