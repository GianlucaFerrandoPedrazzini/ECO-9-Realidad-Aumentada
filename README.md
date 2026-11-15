# El Códice Fractal AR

Juego de realidad aumentada para dos jugadores (Explorador + Operador) con 7 juegos de 3 niveles cada uno.

## Instalación

```bash
pip install -r requirements.txt
```

## Generar las hojas

```bash
python -m tools.generate_sheets
```

Se crean `tools/hojas/hoja_1.png` a `hoja_7.png`, listas para imprimir en A4 (300 dpi). El marcador mide 6 cm.

## Ejecutar

1. En la PC del Explorador (con cámara):
   ```bash
   python -m explorer.explorer_app
   ```
2. En la PC del Operador (IP de la PC del Explorador; si es la misma, usar 127.0.0.1):
   ```bash
   python -m control.operator_app 192.168.0.10
   ```

El Explorador ve las hojas con la cámara y proyecta el fractal sobre el marcador del juego activo. Presioná `q` en la ventana del Explorador para salir.

## Pruebas

```bash
python -m pytest tests/
```
