"""Aplicación del Operador: panel con sliders (con valor actual visible y marcas
de mínimo / paso / máximo), selección de juego y nivel, cronómetro y avance
automático al nivel siguiente cuando el Explorador informa la victoria.
No ve la cámara ni las hojas; sólo comunica por voz con el Explorador."""
import queue
import socket
import sys
import threading
import time

import customtkinter as ctk

from config import NETWORK_PORT
from games.levels import GAMES
from shared import protocol


def fmt_value(value, res):
    """Formatea un valor con tantos decimales como indique la resolución."""
    if res >= 1:
        return str(int(round(value)))
    s = f"{res:.10f}".rstrip("0")
    decimals = len(s.split(".")[1]) if "." in s else 0
    return f"{value:.{decimals}f}"


class OperatorApp(ctk.CTk):
    def __init__(self, host):
        super().__init__()
        self.title('Operador - El Códice Fractal AR')
        self.geometry('560x820')
        self.sock = socket.create_connection((host, NETWORK_PORT), timeout=3)
        self.sock.settimeout(None)
        self.inbox = queue.Queue()
        self.game_id = 1
        self.level_idx = 0
        self.deadline = None
        self.finished = False
        self.sliders = {}
        self.value_labels = {}
        self._build()
        threading.Thread(target=self._reader, daemon=True).start()
        self._select_game(1)
        self._tick()

    def _send(self, msg):
        self.sock.sendall(protocol.encode(msg))

    def _reader(self):
        """Hilo que recibe mensajes del Explorador (por ejemplo, 'won')."""
        buf = b''
        while True:
            try:
                data = self.sock.recv(4096)
            except OSError:
                break
            if not data:
                break
            buf += data
            while b'\n' in buf:
                line, buf = buf.split(b'\n', 1)
                msg = protocol.decode(line)
                if msg:
                    self.inbox.put(msg)

    def _build(self):
        top = ctk.CTkFrame(self)
        top.pack(fill='x', padx=12, pady=8)
        names = ['%d. %s' % (k, v['name']) for k, v in GAMES.items()]
        self.game_menu = ctk.CTkOptionMenu(top, values=names, command=self._on_game)
        self.game_menu.pack(fill='x', padx=8, pady=8)
        self.level_seg = ctk.CTkSegmentedButton(
            top, values=['Nivel 1', 'Nivel 2', 'Nivel 3'], command=self._on_level)
        self.level_seg.pack(fill='x', padx=8, pady=(0, 8))
        self.info = ctk.CTkLabel(self, text='', wraplength=520, justify='left')
        self.info.pack(fill='x', padx=12, pady=4)
        self.params_frame = ctk.CTkFrame(self)
        self.params_frame.pack(fill='both', expand=True, padx=12, pady=8)
        self.status = ctk.CTkLabel(self, text='', font=('Arial', 16, 'bold'), wraplength=520)
        self.status.pack(pady=4)
        self.timer_label = ctk.CTkLabel(self, text='', font=('Arial', 22, 'bold'))
        self.timer_label.pack(pady=8)
        self.series = ctk.CTkLabel(self, text='', wraplength=520, justify='left')
        self.series.pack(fill='x', padx=12, pady=(4, 12))

    def _on_game(self, choice):
        self._select_game(int(choice.split('.')[0]))

    def _select_game(self, gid):
        self.game_id = gid
        for w in self.params_frame.winfo_children():
            w.destroy()
        self.sliders = {}
        self.value_labels = {}

        for key, (label, lo, hi, init, res) in GAMES[gid]['params'].items():
            # Encabezado: nombre del parámetro + valor actual (azul, se actualiza en vivo)
            header = ctk.CTkFrame(self.params_frame, fg_color='transparent')
            header.pack(fill='x', padx=8, pady=(6, 0))
            ctk.CTkLabel(header, text=label, anchor='w',
                         font=('Arial', 13, 'bold')).pack(side='left')
            vlabel = ctk.CTkLabel(header, text=fmt_value(init, res), anchor='e',
                                  font=('Arial', 13, 'bold'), text_color='#4FC3F7', width=80)
            vlabel.pack(side='right')
            self.value_labels[key] = (vlabel, res)

            # Slider con número fijo de posiciones discretas
            steps = max(1, round((hi - lo) / res))
            slider = ctk.CTkSlider(self.params_frame, from_=lo, to=hi,
                                   number_of_steps=steps,
                                   command=lambda v, k=key: self._on_param(k, v))
            slider.set(init)
            slider.pack(fill='x', padx=8, pady=(2, 0))
            self.sliders[key] = slider

            # Línea de marcas: mínimo | paso | máximo
            marks = ctk.CTkFrame(self.params_frame, fg_color='transparent')
            marks.pack(fill='x', padx=8, pady=(0, 8))
            ctk.CTkLabel(marks, text=fmt_value(lo, res), font=('Arial', 9),
                         text_color='gray').pack(side='left')
            ctk.CTkLabel(marks, text=fmt_value(hi, res), font=('Arial', 9),
                         text_color='gray').pack(side='right')
            ctk.CTkLabel(marks, text='paso ' + fmt_value(res, res),
                         font=('Arial', 9), text_color='gray').pack(
                side='left', expand=True, fill='x')

        self.game_menu.set('%d. %s' % (gid, GAMES[gid]['name']))
        self.series.configure(text='Serie: ' + GAMES[gid]['series'])
        self._send({'type': 'select', 'game': gid, 'level': 0})
        self._show_level(0)

    def _on_level(self, choice):
        self._show_level(int(choice[-1]) - 1)

    def _show_level(self, idx):
        self.level_idx = idx
        self.finished = False
        level = GAMES[self.game_id]['levels'][idx]
        self.level_seg.set('Nivel %d' % (idx + 1))
        self.info.configure(text='%s: %s' % (level['title'], level['goal']))
        self.status.configure(text='Buscando la posición de la hoja...')
        self.deadline = time.time() + level['time'] if level['time'] else None
        self._send({'type': 'level', 'level': idx})

    def _on_param(self, key, value):
        if key in self.value_labels:
            vlabel, res = self.value_labels[key]
            vlabel.configure(text=fmt_value(value, res))
        self._send({'type': 'param', 'key': key, 'value': float(value)})

    def _on_win(self):
        self.deadline = None
        self.finished = True
        if self.level_idx < 2:
            self.status.configure(text='Nivel %d completado. Pasando al siguiente...' % (self.level_idx + 1))
            gid, idx = self.game_id, self.level_idx
            self.after(3000, lambda: self._advance(gid, idx))
        else:
            self.status.configure(text='¡Juego completado! Elegí otro juego.')

    def _advance(self, gid, idx):
        if self.game_id == gid and self.level_idx == idx:
            self._show_level(idx + 1)

    def _tick(self):
        while not self.inbox.empty():
            msg = self.inbox.get()
            if (msg.get('type') == 'won' and not self.finished
                    and msg.get('game') == self.game_id and msg.get('level') == self.level_idx):
                self._on_win()
        if self.deadline:
            left = max(0, int(self.deadline - time.time()))
            self.timer_label.configure(text='Tiempo: %02d:%02d' % (left // 60, left % 60))
            if left == 0:
                self.timer_label.configure(text='¡Tiempo agotado!')
                self.deadline = None
        else:
            self.timer_label.configure(text='')
        self.after(250, self._tick)


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    OperatorApp(host).mainloop()