"""Series numéricas y fractales. Matemática pura, sin dependencias gráficas."""


def geometric_partial_sums(first, ratio, terms):
    """Sumas parciales de una serie geométrica: primer término, razón y cantidad de términos."""
    sums, total, term = [], 0.0, first
    for _ in range(terms):
        total += term
        sums.append(total)
        term *= ratio
    return sums


def sierpinski_stats(depth):
    """Cantidad de piezas (3^n) y área de cada pieza ((1/4)^n) por nivel."""
    return [{"nivel": n, "piezas": 3 ** n, "area_pieza": 0.25 ** n} for n in range(depth + 1)]


def koch_stats(n, side=1.0):
    """Número de lados, longitud de cada lado y perímetro del copo de Koch en el nivel n."""
    return {
        "nivel": n,
        "lados": 3 * 4 ** n,
        "longitud_lado": side / 3 ** n,
        "perimetro": 3 * side * (4 / 3) ** n,
    }


def mandelbrot_escape(c, max_iter):
    """Iteraciones hasta que z = z^2 + c escapa de radio 2. Devuelve max_iter si queda acotada."""
    z = 0j
    for n in range(max_iter):
        z = z * z + c
        if abs(z) > 2:
            return n
    return max_iter


def julia_escape(z, c, max_iter):
    """Igual que mandelbrot_escape, pero con z inicial (semilla) y c constante."""
    for n in range(max_iter):
        z = z * z + c
        if abs(z) > 2:
            return n
    return max_iter


def dragon_turns(n):
    """Secuencia de giros de la curva del dragón tras n pasos (longitud 2^n - 1)."""
    s = ""
    for _ in range(n):
        s = s + "R" + "".join("L" if ch == "R" else "R" for ch in reversed(s))
    return s


def lorenz_step(x, y, z, sigma, rho, beta, dt):
    """Un paso de integración de Euler del sistema de Lorenz."""
    dx = sigma * (y - x)
    dy = x * (rho - z) - y
    dz = x * y - beta * z
    return x + dx * dt, y + dy * dt, z + dz * dt
