"""
round_dialog.py - Diálogo para ingresar los puntajes de una mano
"""

import tkinter as tk
from tkinter import ttk, messagebox
from game import RoundScore, BONUS
from calculator import CardCalculatorDialog


class RoundDialog(tk.Toplevel):
    def __init__(self, parent, round_num: int, team_names: list[str]):
        super().__init__(parent)
        self.title(f"Mano #{round_num}")
        self.resizable(False, False)
        self.grab_set()
        self.result: tuple = tuple([None] * len(team_names))
        self.team_names = team_names
        self.round_num = round_num

        self._fields: list[dict] = [{} for _ in team_names]
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=8)

        for i, name in enumerate(self.team_names):
            tab = ttk.Frame(notebook, padding=12)
            notebook.add(tab, text=f"  {name}  ")
            self._build_team_tab(tab, i)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=12, pady=8)
        ttk.Button(btn_frame, text="✔ Confirmar mano",
                   command=self._on_confirm).pack(side="right", padx=4)
        ttk.Button(btn_frame, text="✖ Cancelar",
                   command=self._on_cancel).pack(side="right", padx=4)

    def _build_team_tab(self, parent, idx: int):
        f = self._fields[idx]
        row = 0

        # ── Fichas bajadas ────────────────────────────────────────────────────
        ttk.Label(parent, text="Fichas BAJADAS (puntos a favor):").grid(
            row=row, column=0, sticky="w", pady=(0, 2))
        row += 1

        cards_frame = ttk.Frame(parent)
        cards_frame.grid(row=row, column=0, sticky="ew")
        f["cards_down"] = tk.StringVar(value="0")
        ttk.Entry(cards_frame, textvariable=f["cards_down"],
                  width=10, justify="center").pack(side="left")
        ttk.Button(cards_frame, text="🧮 Calcular",
                   command=lambda: self._open_calc(f["cards_down"])
                   ).pack(side="left", padx=6)
        row += 1

        ttk.Separator(parent, orient="horizontal").grid(
            row=row, column=0, sticky="ew", pady=8)
        row += 1

        # ── Fichas en mano ────────────────────────────────────────────────────
        ttk.Label(parent, text="Fichas EN MANO del compañero (puntos a restar):").grid(
            row=row, column=0, sticky="w", pady=(0, 2))
        row += 1

        rem_frame = ttk.Frame(parent)
        rem_frame.grid(row=row, column=0, sticky="ew")
        f["cards_remaining"] = tk.StringVar(value="0")
        ttk.Entry(rem_frame, textvariable=f["cards_remaining"],
                  width=10, justify="center").pack(side="left")
        ttk.Button(rem_frame, text="🧮 Calcular",
                   command=lambda: self._open_calc(f["cards_remaining"])
                   ).pack(side="left", padx=6)
        row += 1

        ttk.Separator(parent, orient="horizontal").grid(
            row=row, column=0, sticky="ew", pady=8)
        row += 1

        # ── Jugadas especiales ────────────────────────────────────────────────
        ttk.Label(parent, text="Jugadas especiales:",
                  font=("Segoe UI", 9, "bold")).grid(row=row, column=0, sticky="w")
        row += 1

        f["cierre"] = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent, text=f"Cierre  (+{BONUS['cierre']} pts)",
                        variable=f["cierre"]
                        ).grid(row=row, column=0, sticky="w", padx=8)
        row += 1

        f["muerto_bought"] = tk.BooleanVar(value=False)
        ttk.Checkbutton(parent,
                        text=f"Compró el Muerto  (+{BONUS['muerto']} pts / −{BONUS['muerto']} si no)",
                        variable=f["muerto_bought"]
                        ).grid(row=row, column=0, sticky="w", padx=8)
        row += 1

        cp_frame = ttk.Frame(parent)
        cp_frame.grid(row=row, column=0, sticky="w", padx=8, pady=2)
        ttk.Label(cp_frame, text=f"Canastas Puras  (+{BONUS['canasta_pura']} c/u):").pack(side="left")
        f["canastas_puras"] = tk.StringVar(value="0")
        ttk.Spinbox(cp_frame, from_=0, to=20, width=4,
                    textvariable=f["canastas_puras"]).pack(side="left", padx=6)
        row += 1

        ci_frame = ttk.Frame(parent)
        ci_frame.grid(row=row, column=0, sticky="w", padx=8, pady=2)
        ttk.Label(ci_frame, text=f"Canastas Impuras  (+{BONUS['canasta_impura']} c/u):").pack(side="left")
        f["canastas_impuras"] = tk.StringVar(value="0")
        ttk.Spinbox(ci_frame, from_=0, to=20, width=4,
                    textvariable=f["canastas_impuras"]).pack(side="left", padx=6)
        row += 1

        ttk.Separator(parent, orient="horizontal").grid(
            row=row, column=0, sticky="ew", pady=8)
        row += 1

        f["preview_var"] = tk.StringVar(value="Subtotal estimado: —")
        ttk.Label(parent, textvariable=f["preview_var"],
                  font=("Segoe UI", 10, "bold")).grid(row=row, column=0, sticky="w")

        for key in ("cards_down", "cards_remaining", "canastas_puras", "canastas_impuras"):
            f[key].trace_add("write", lambda *_, i=idx: self._update_preview(i))
        f["cierre"].trace_add("write",        lambda *_, i=idx: self._update_preview(i))
        f["muerto_bought"].trace_add("write", lambda *_, i=idx: self._update_preview(i))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _open_calc(self, target_var: tk.StringVar):
        dlg = CardCalculatorDialog(self)
        self.wait_window(dlg)
        if dlg.result is not None:
            target_var.set(str(dlg.result))

    def _has_data(self, idx: int) -> bool:
        f = self._fields[idx]
        try:
            return any([
                int(f["cards_down"].get()       or 0) > 0,
                int(f["cards_remaining"].get()  or 0) > 0,
                int(f["canastas_puras"].get()   or 0) > 0,
                int(f["canastas_impuras"].get() or 0) > 0,
                f["cierre"].get(),
                f["muerto_bought"].get(),
            ])
        except ValueError:
            return False

    def _update_preview(self, idx: int):
        if not self._has_data(idx):
            self._fields[idx]["preview_var"].set("Subtotal estimado: —")
            return
        try:
            rs = self._build_round_score(idx)
            self._fields[idx]["preview_var"].set(f"Subtotal estimado: {rs.total:+} pts")
        except Exception:
            self._fields[idx]["preview_var"].set("Subtotal estimado: —")

    def _build_round_score(self, idx: int) -> RoundScore:
        f = self._fields[idx]
        return RoundScore(
            team_name=self.team_names[idx],
            cards_down=max(0, int(f["cards_down"].get()       or 0)),
            cards_remaining=max(0, int(f["cards_remaining"].get()  or 0)),
            cierre=f["cierre"].get(),
            canastas_puras=max(0, int(f["canastas_puras"].get()   or 0)),
            canastas_impuras=max(0, int(f["canastas_impuras"].get() or 0)),
            muerto_bought=f["muerto_bought"].get(),
            muerto_available=True,
        )

    def _on_confirm(self):
        try:
            scores = [self._build_round_score(i) for i in range(len(self.team_names))]
        except ValueError as e:
            messagebox.showerror("Error", f"Valor inválido: {e}", parent=self)
            return
        self.result = tuple(scores)
        self.destroy()

    def _on_cancel(self):
        self.result = tuple([None] * len(self.team_names))
        self.destroy()