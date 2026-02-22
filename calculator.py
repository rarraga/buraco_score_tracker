"""
calculator.py - Diálogo calculadora de fichas
"""

import tkinter as tk
from tkinter import ttk
from game import CARD_VALUES, calculate_cards


class CardCalculatorDialog(tk.Toplevel):
    """Ventana emergente para calcular el valor de un conjunto de fichas."""

    def __init__(self, parent, title="Calculadora de Fichas"):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = 0
        self.grab_set()  # Modal

        self.entries: dict = {}
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _build_ui(self):
        CARD_LABELS = {
            1: "As  (1) → 15 pts",
            2: "2   → 20 pts",
            3: "3   → 5 pts",
            4: "4   → 5 pts",
            5: "5   → 5 pts",
            6: "6   → 5 pts",
            7: "7   → 5 pts",
            8: "8   → 10 pts",
            9: "9   → 10 pts",
            10: "10  → 10 pts",
            11: "J   → 10 pts",
            12: "Q   → 10 pts",
            13: "K   → 10 pts",
            "comodin": "Comodín → 50 pts",
        }

        frame = ttk.Frame(self, padding=16)
        frame.grid(sticky="nsew")

        ttk.Label(frame, text="Ingresá la cantidad de cada ficha:",
                  font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(0, 10), sticky="w")

        # Encabezados
        ttk.Label(frame, text="Ficha", width=22).grid(row=1, column=0, sticky="w")
        ttk.Label(frame, text="Cant.", width=6).grid(row=1, column=1)
        ttk.Label(frame, text="Subtotal", width=8).grid(row=1, column=2)

        ttk.Separator(frame, orient="horizontal").grid(
            row=2, column=0, columnspan=3, sticky="ew", pady=4)

        self._subtotal_vars = {}
        for i, (card, label) in enumerate(CARD_LABELS.items(), start=3):
            ttk.Label(frame, text=label, anchor="w").grid(
                row=i, column=0, sticky="w", pady=1)
            var = tk.StringVar(value="0")
            sub_var = tk.StringVar(value="0")
            self._subtotal_vars[card] = sub_var

            entry = ttk.Entry(frame, textvariable=var, width=6, justify="center")
            entry.grid(row=i, column=1, padx=4)
            ttk.Label(frame, textvariable=sub_var, width=8, anchor="e").grid(
                row=i, column=2)

            var.trace_add("write", lambda *_, c=card, v=var, s=sub_var: self._update_sub(c, v, s))
            self.entries[card] = var

        sep_row = 3 + len(CARD_LABELS)
        ttk.Separator(frame, orient="horizontal").grid(
            row=sep_row, column=0, columnspan=3, sticky="ew", pady=8)

        self.total_var = tk.StringVar(value="Total: 0 pts")
        ttk.Label(frame, textvariable=self.total_var,
                  font=("Segoe UI", 12, "bold")).grid(
            row=sep_row + 1, column=0, columnspan=3, pady=4)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=sep_row + 2, column=0, columnspan=3, pady=(8, 0))
        ttk.Button(btn_frame, text="✔ Usar este total",
                   command=self._on_confirm).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="✖ Cancelar",
                   command=self._on_cancel).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="↺ Limpiar",
                   command=self._clear).pack(side="left", padx=4)

    def _update_sub(self, card, var, sub_var):
        try:
            qty = max(0, int(var.get()))
        except ValueError:
            qty = 0
        pts = CARD_VALUES.get(card, 0) * qty
        sub_var.set(str(pts))
        self._recalculate()

    def _recalculate(self):
        total = 0
        for card, var in self.entries.items():
            try:
                qty = max(0, int(var.get()))
            except ValueError:
                qty = 0
            total += CARD_VALUES.get(card, 0) * qty
        self.result = total
        self.total_var.set(f"Total: {total} pts")

    def _clear(self):
        for var in self.entries.values():
            var.set("0")

    def _on_confirm(self):
        self._recalculate()
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()