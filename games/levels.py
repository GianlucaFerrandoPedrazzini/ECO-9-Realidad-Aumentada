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
        "marker_id": 0,
        "params": {
            "zoom": ("Zoom", 1.0, 40.0, 1.0, 0.1),
            "cx": ("Centro X", -2.0, 1.0, -0.5, 0.01),
            "cy": ("Centro Y", -1.5, 1.5, 0.0, 0.01),
            "iter": ("Iteraciones", 10, 150, 40, 1),
        },
        "levels": [
            _level("Código numérico", "Enfocar el código numérico de 3 dígitos impreso en la hoja."),
            _level("Detalle puntual", "Ajustar zoom y desplazarse hasta el detalle marcado."),
            _level("Contorno sombreado", "Alinear el relieve con el contorno sombreado antes de que se acabe el tiempo.", 120),
        ],
        "series": "Para cada píxel se evalúa si z(n+1) = z(n)^2 + c queda acotada (convergencia, color oscuro) o escapa a infinito (divergencia, color brillante).",
    },
    2: {
        "name": "La Llave Cambiaformas",
        "concept": "Conjunto de Julia",
        "marker_id": 1,
        "params": {
            "x": ("Parámetro X", -1.5, 1.5, -0.7, 0.01),
            "y": ("Parámetro Y", -1.5, 1.5, 0.27, 0.01),
            "iter": ("Iteraciones", 10, 150, 60, 1),
        },
        "levels": [
            _level("Encaje simple", "Deformar la figura hasta encajar en la cerradura impresa."),
            _level("Alta precisión", "Encajar la figura con un margen de error reducido."),
            _level("Bloques de bloqueo", "Moldear la figura esquivando los dos bloques impresos.", 120),
        ],
        "series": "El valor inicial (semilla) altera el resultado de la serie: un cambio pequeño produce una geometría distinta.",
    },
    3: {
        "name": "La Pirámide Encajable",
        "concept": "Triángulo de Sierpinski",
        "marker_id": 2,
        "params": {
            "depth": ("Profundidad", 1, 5, 1, 1),
            "escala": ("Escala", 0.5, 1.0, 0.9, 0.01),
        },
        "levels": [
            _level("Tres marcas", "Ajustar la profundidad para cubrir las 3 marcas impresas."),
            _level("Nueve puntos", "Ajustar la subdivisión para destapar exactamente 9 puntos de luz."),
            _level("Zonas de peligro", "Elegir el nivel correcto evitando las 3 zonas de peligro.", 120),
        ],
        "series": "Multiplicación de piezas 1 → 3 → 9 → 27 mientras el área de cada pieza se reduce a (1/4)^n.",
    },
    4: {
        "name": "El Puente de Papel",
        "concept": "Copo de nieve de Koch",
        "marker_id": 3,
        "params": {
            "n": ("Iteraciones", 0, 4, 1, 1),
            "largo": ("Largo del puente", 0.5, 1.5, 1.0, 0.01),
        },
        "levels": [
            _level("Acantilados rectos", "Unir los dos acantilados ajustando el largo del puente."),
            _level("Acantilados desalineados", "Aumentar los picos para esquivar la roca impresa."),
            _level("Máxima precisión", "Ajustar el largo con la tolerancia más estrecha.", 120),
        ],
        "series": "El perímetro P(n) = 3·(4/3)^n diverge a infinito, mientras el área queda acotada.",
    },
    5: {
        "name": "El Árbol de la Tarjeta",
        "concept": "Árbol de Pitágoras",
        "marker_id": 4,
        "params": {
            "depth": ("Niveles de ramas", 1, 8, 3, 1),
            "angulo": ("Ángulo de ramas", 0.1, 1.2, 0.6, 0.01),
        },
        "levels": [
            _level("Dos dianas", "Ajustar el ángulo de las ramas para tocar 2 dianas."),
            _level("Tres dianas", "Tocar 3 dianas a distintas alturas."),
            _level("Muros de bloqueo", "Tocar las 3 dianas esquivando 2 muros.", 120),
        ],
        "series": "Serie geométrica decreciente 1 + 0.7 + 0.49 + ... que converge a una altura finita.",
    },
    6: {
        "name": "El Cableado en Cuadrícula",
        "concept": "Curva del dragón",
        "marker_id": 5,
        "params": {
            "dobleces": ("Cantidad de dobleces", 1, 16, 4, 1),
        },
        "levels": [
            _level("Ruta corta", "Completar una ruta de 4 dobleces evitando 1 obstáculo."),
            _level("Ruta media", "Completar una ruta de 8 dobleces evitando 3 casillas de peligro."),
            _level("Sector vacío", "Trazar 16 dobleces sin cruzar el cable sobre sí mismo.", 120),
        ],
        "series": "Secuencia de giros L/R que duplica y revierte en cada paso: S(n+1) = S(n) + R + revertir_y_complementar(S(n)).",
    },
    7: {
        "name": "El Atractor del Caos",
        "concept": "Atractor de Lorenz",
        "marker_id": 6,
        "params": {
            "sigma": ("Sigma", 5.0, 20.0, 10.0, 0.1),
            "rho": ("Rho", 20.0, 35.0, 28.0, 0.1),
            "beta": ("Beta", 1.0, 4.0, 2.67, 0.01),
            "velocidad": ("Velocidad", 0.1, 3.0, 1.0, 0.1),
        },
        "levels": [
            _level("Aro grande", "Ajustar velocidad e inclinación para atravesar 1 aro grande."),
            _level("Dos aros", "Enhebrar la trayectoria a través de 2 aros simultáneamente."),
            _level("Aros estrechos", "Enhebrar 2 aros estrechos mientras el flujo acelera.", 120),
        ],
        "series": "Serie temporal caótica: cada punto deriva del anterior, no se repite y permanece acotada (efecto mariposa).",
    },
}
