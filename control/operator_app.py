"""Aplicación del Operador: panel con sliders, selección de juego y nivel, y cronómetro.
No ve la cámara ni las hojas; sólo comunica por voz con el Explorador."""
import socket
import sys
import time

import customtkinter as ctk

from config import NETWORK_PORT
from games.levels import GAMES
from shared import protocol

class OperatorApp(ctk.CTk):
    def __init__(self, host):
        super().__init__()
        self.title("Operador - El Códice Fractal AR")
        self.geometry("540x680")
        self.sock = socket.create_connection((host, NETWORK_PORT), timeout=3)
        self.game_id = 1
        self.deadline = None
        self.sliders = {}
        self._build()
        self._select_game(1)
        self._tick()

    def _send(self, msg):
        self.sock.sendall(protocol.encode(msg))

    def _build(self):
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=12, pady=8)
        names = [f"{k}. {v['name']}" for k, v in GAMES.items()]
        self.game_menu = ctk.CTkOptionMenu(top, values=names, command=self._on_game)
        self.game_menu.pack(fill="x", padx=8, pady=8)
        self.level_seg = ctk.CTkSegmentedButton(top, values=["Nivel 1", "Nivel 2", "Nivel 3"],
                                                command=self._on_level)
        self.level_seg.pack(fill="x", padx=8, pady=(0, 8))
        self.info = ctk.CTkLabel(self, text="", wraplength=500, justify="left")
        self.info.pack(fill="x", padx=12, pady=4)
        self.params_frame = ctk.CTkFrame(self)
        self.params_frame.pack(fill="both", expand=True, padx=12, pady=8)
        self.timer_label = ctk.CTkLabel(self, text="", font=("Arial", 22, "bold"))
        self.timer_label.pack(pady=8)
        self.series = ctk.CTkLabel(self, text="", wraplength=500, justify="left")
        self.series.pack(fill="x", padx=12, pady=(4, 12))

    def _on_game(self, choice):
        self._select_game(int(choice.split(".")[0]))

    def _select_game(self, gid):
        self.game_id = gid
        for w in self.params_frame.winfo_children():
            w.destroy()
        self.sliders = {}
        for key, (label, lo, hi, init, res) in GAMES[gid]["params"].items():
            ctk.CTkLabel(self.params_frame, text=label).pack(anchor="w", padx=8)
            steps = max(1, round((hi - lo) / res))
            s = ctk.CTkSlider(self.params_frame, from_=lo, to=hi, number_of_steps=steps,
                              command=lambda v, k=key: self._on_param(k, v))
            s.set(init)
            s.pack(fill="x", padx=8, pady=(0, 6))
            self.sliders[key] = s
        self.game_menu.set(f"{gid}. {GAMES[gid]['name']}")
        self.series.configure(text="Serie: " + GAMES[gid]["series"])
        self._send({"type": "select", "game": gid, "level": 0})
        self._show_level(0)

    def _on_level(self, choice):
        self._show_level(int(choice[-1]) - 1)

    def _show_level(self, idx):
        level = GAMES[self.game_id]["levels"][idx]
        self.level_seg.set(f"Nivel {idx + 1}")
        self.info.configure(text=f"{level['title']}: {level['goal']}")
        self.deadline = time.time() + level["time"] if level["time"] else None
        self._send({"type": "level", "level": idx})

    def _on_param(self, key, value):
        self._send({"type": "param", "key": key, "value": float(value)})

    def _tick(self):
        if self.deadline:
            left = max(0, int(self.deadline - time.time()))
            self.timer_label.configure(text=f"Tiempo: {left // 60:02d}:{left % 60:02d}")
            if left == 0:
                self.timer_label.configure(text="¡Tiempo agotado!")
                self.deadline = None
        else:
            self.timer_label.configure(text="")
        self.after(250, self._tick)

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    OperatorApp(host).mainloop()
