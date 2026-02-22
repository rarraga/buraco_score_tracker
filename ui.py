"""
ui.py - Interfaz principal de la aplicación Buraco
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from game import Game, RoundScore, TARGET_SCORE
from round_dialog import RoundDialog


class BuracoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🃏 Buraco - Contador de Puntajes")
        self.minsize(680, 520)
        self.game: Game | None = None

        self._apply_style()
        self._build_menu()
        self._build_scrollable_main()
        self._show_welcome()

        # ── Pantalla completa al iniciar (cross-platform) ──────────────────
        self.after(0, self._set_fullscreen)

    def _set_fullscreen(self):
        try:
            # Windows y algunos Linux con TkAgg
            self.state("zoomed")
        except Exception:
            try:
                self.attributes("-zoomed", True)
            except Exception:
                self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

    # ── Estilo ────────────────────────────────────────────────────────────────

    def _apply_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", padding=6)
        style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("Score.TLabel", font=("Segoe UI", 36, "bold"))
        style.configure("Sub.TLabel", font=("Segoe UI", 10))
        style.configure("Win.TLabel", font=("Segoe UI", 14, "bold"), foreground="#2e7d32")
        style.configure("Round.Treeview", font=("Segoe UI", 10), rowheight=24)
        style.configure("Round.Treeview.Heading", font=("Segoe UI", 10, "bold"))
        # Barra de progreso verde
        style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor="#e0e0e0",
            background="#43a047",
            thickness=18,
        )

    # ── Menú ──────────────────────────────────────────────────────────────────

    def _build_menu(self):
        menubar = tk.Menu(self)
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="Nueva partida", command=self._new_game, accelerator="Ctrl+N")
        game_menu.add_command(label="Abrir partida...", command=self._load_game, accelerator="Ctrl+O")
        game_menu.add_command(label="Guardar partida...", command=self._save_game, accelerator="Ctrl+S")
        game_menu.add_separator()
        game_menu.add_command(label="Salir", command=self.quit)
        menubar.add_cascade(label="Partida", menu=game_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Valores de fichas", command=self._show_card_values)
        help_menu.add_command(label="Reglas de puntaje", command=self._show_rules)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

        self.config(menu=menubar)
        self.bind("<Control-n>", lambda _: self._new_game())
        self.bind("<Control-o>", lambda _: self._load_game())
        self.bind("<Control-s>", lambda _: self._save_game())

    # ── Layout principal con grid dinámico ───────────────────────────────────

    def _build_scrollable_main(self):
        """
        Layout con grid + pesos para que todo se ajuste dinámicamente.
        El historial ocupa todo el espacio restante en cualquier resolución.
        Un canvas envuelve el contenido para permitir scroll si la ventana
        se reduce por debajo del tamaño mínimo.
        """
        # La ventana raíz tiene una sola celda que ocupa todo
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Canvas + scrollbar — ocupa toda la ventana
        self._canvas = tk.Canvas(self, highlightthickness=0)
        self._vscroll = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vscroll.set)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._vscroll.grid(row=0, column=1, sticky="ns")

        # Frame interno con grid (no pack, para control total de expansión)
        self.main_frame = ttk.Frame(self._canvas, padding=12)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self.main_frame, anchor="nw"
        )

        # El frame interno tiene 4 filas:
        #   0 → marcador        (fijo)
        #   1 → historial       (expande con weight=1)
        #   2 → botones         (fijo)
        #   3 → status          (fijo)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)
        self.main_frame.rowconfigure(1, weight=1)   # ← historial se expande aquí
        self.main_frame.rowconfigure(2, weight=0)
        self.main_frame.rowconfigure(3, weight=0)

        # Cuando el canvas cambia de tamaño, ajustamos el inner frame
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self.main_frame.bind("<Configure>", self._on_frame_resize)

        # Scroll con rueda del mouse
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_all("<Button-4>",   self._on_mousewheel)
        self._canvas.bind_all("<Button-5>",   self._on_mousewheel)

        self._build_main_content()

    def _on_canvas_resize(self, event):
        """Cuando el canvas crece/achica: ajusta ancho y altura del inner frame."""
        canvas_w = event.width
        canvas_h = event.height

        # El inner frame ocupa al menos todo el ancho del canvas
        self._canvas.itemconfig(self._canvas_window, width=canvas_w)

        # Si el contenido es menor que la altura del canvas, estiramos el frame
        frame_h = self.main_frame.winfo_reqheight()
        new_h = max(frame_h, canvas_h)
        self._canvas.itemconfig(self._canvas_window, height=new_h)

        # Actualiza scrollregion (permite scroll si el contenido es mayor)
        self._canvas.configure(scrollregion=(0, 0, canvas_w, max(frame_h, canvas_h)))

    def _on_frame_resize(self, _event=None):
        """Cuando el contenido cambia de tamaño, recalcula scrollregion."""
        canvas_h = self._canvas.winfo_height()
        frame_h  = self.main_frame.winfo_reqheight()
        canvas_w = self._canvas.winfo_width()
        self._canvas.itemconfig(self._canvas_window, height=max(frame_h, canvas_h))
        self._canvas.configure(scrollregion=(0, 0, canvas_w, max(frame_h, canvas_h)))

    def _on_mousewheel(self, event):
        if event.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(1, "units")
        else:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_main_content(self):
        PAD = 8

        # ── Fila 0: Marcador de equipos ───────────────────────────────────────
        score_frame = ttk.Frame(self.main_frame)
        score_frame.grid(row=0, column=0, sticky="ew", pady=(0, PAD))
        score_frame.columnconfigure(0, weight=1)
        score_frame.columnconfigure(1, weight=1)

        self.team_panels: list[dict] = [{}, {}]
        for i in range(2):
            col = ttk.Frame(score_frame, relief="groove", padding=14)
            col.grid(row=0, column=i, sticky="ew",
                     padx=(0, PAD // 2) if i == 0 else (PAD // 2, 0))
            col.columnconfigure(0, weight=1)

            name_var  = tk.StringVar(value=f"Equipo {i+1}")
            score_var = tk.StringVar(value="0")
            diff_var  = tk.StringVar(value=f"Faltan {TARGET_SCORE} pts")

            ttk.Label(col, textvariable=name_var,
                      style="Header.TLabel", anchor="center").grid(
                row=0, column=0, sticky="ew")
            ttk.Label(col, textvariable=score_var,
                      style="Score.TLabel", anchor="center").grid(
                row=1, column=0, sticky="ew")
            ttk.Label(col, textvariable=diff_var,
                      style="Sub.TLabel", anchor="center").grid(
                row=2, column=0, sticky="ew")

            prog = ttk.Progressbar(
                col, maximum=TARGET_SCORE, mode="determinate",
                style="Green.Horizontal.TProgressbar"
            )
            prog.grid(row=3, column=0, sticky="ew", pady=(6, 2))

            self.team_panels[i] = {
                "frame": col, "name": name_var,
                "score": score_var, "diff": diff_var, "prog": prog,
            }

        # ── Fila 1: Historial (se expande) ────────────────────────────────────
        hist_frame = ttk.LabelFrame(self.main_frame,
                                    text="  Historial de Manos  ", padding=8)
        hist_frame.grid(row=1, column=0, sticky="nsew", pady=(0, PAD))
        hist_frame.rowconfigure(0, weight=1)
        hist_frame.columnconfigure(0, weight=1)

        cols = ("#", "Equipo 1", "Equipo 2", "Acum. E1", "Acum. E2")
        self.tree = ttk.Treeview(hist_frame, columns=cols,
                                  show="headings", style="Round.Treeview")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="center", stretch=True)
        self.tree.column("#", width=50, stretch=False)
        self.tree.grid(row=0, column=0, sticky="nsew")

        tree_scroll = ttk.Scrollbar(hist_frame, orient="vertical",
                                    command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=tree_scroll.set)

        # ── Fila 2: Botones ───────────────────────────────────────────────────
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(0, 4))
        btn_frame.columnconfigure(1, weight=1)   # espacio entre izq y der

        self.btn_new_round = ttk.Button(btn_frame, text="➕ Nueva Mano",
                                         command=self._add_round, state="disabled")
        self.btn_new_round.grid(row=0, column=0, padx=(0, 4))

        self.btn_undo = ttk.Button(btn_frame, text="↩ Deshacer última mano",
                                    command=self._undo_round, state="disabled")
        self.btn_undo.grid(row=0, column=1, padx=4, sticky="w")

        self.btn_new_game = ttk.Button(btn_frame, text="🆕 Nueva Partida",
                                        command=self._new_game)
        self.btn_new_game.grid(row=0, column=2, padx=(4, 0))

        # ── Fila 3: Status ────────────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Iniciá una nueva partida para comenzar.")
        ttk.Label(self.main_frame, textvariable=self.status_var,
                  style="Sub.TLabel", anchor="center").grid(
            row=3, column=0, sticky="ew", pady=(0, 4))

    def _show_welcome(self):
        for p in self.team_panels:
            p["name"].set("—")
            p["score"].set("—")
            p["diff"].set("")
            p["prog"]["value"] = 0

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _new_game(self):
        dlg = NewGameDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            self.game = Game(*dlg.result)
            self._refresh_ui()
            self.btn_new_round.config(state="normal")
            self.btn_undo.config(state="disabled")
            self.status_var.set(f"¡Partida iniciada! Objetivo: {TARGET_SCORE} puntos.")

    def _add_round(self):
        if not self.game or self.game.is_over:
            return
        dlg = RoundDialog(self, self.game.current_round,
                          [t.name for t in self.game.teams])
        self.wait_window(dlg)
        s1, s2 = dlg.result

        # Cancelado o datos inválidos
        if not isinstance(s1, RoundScore) or not isinstance(s2, RoundScore):
            return

        self.game.add_round(s1, s2)
        self._refresh_ui()
        self.btn_undo.config(state="normal")

        if self.game.is_over:
            self._show_winner()

    def _undo_round(self):
        if not self.game or not self.game.rounds:
            return
        if messagebox.askyesno("Deshacer", "¿Deshacer la última mano?", parent=self):
            self.game.undo_last_round()
            self._refresh_ui()

            self.btn_new_round.config(
                state="disabled" if self.game.is_over else "normal"
            )

            if not self.game.rounds:
                self.btn_undo.config(state="disabled")

    def _save_game(self):
        if not self.game:
            messagebox.showinfo("Sin partida", "No hay ninguna partida activa.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Partida Buraco", "*.json"), ("Todos", "*.*")],
            title="Guardar partida"
        )
        if path:
            self.game.save(path)
            self.status_var.set(f"Partida guardada en {path}")

    def _load_game(self):
        path = filedialog.askopenfilename(
            filetypes=[("Partida Buraco", "*.json"), ("Todos", "*.*")],
            title="Abrir partida"
        )
        if not path:
            return
        try:
            self.game = Game.load(path)
            self._refresh_ui()
            self.btn_new_round.config(state="normal" if not self.game.is_over else "disabled")
            self.btn_undo.config(state="normal" if self.game.rounds else "disabled")
            self.status_var.set(f"Partida cargada desde {path}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la partida:\n{e}")

    # ── Actualización de UI ───────────────────────────────────────────────────

    def _refresh_ui(self):
        if not self.game:
            return

        # Scoreboard
        for i, team in enumerate(self.game.teams):
            p = self.team_panels[i]
            p["name"].set(team.name)
            p["score"].set(str(team.total))
            remaining = TARGET_SCORE - team.total
            if team.has_won:
                p["diff"].set("¡GANADOR! 🏆")
            else:
                p["diff"].set(f"Faltan {remaining} pts")
            p["prog"]["value"] = min(team.total, TARGET_SCORE)

        # Historial
        self.tree.delete(*self.tree.get_children())
        acc = [0, 0]
        for rnd in self.game.rounds:
            s0 = rnd.scores[0].total
            s1 = rnd.scores[1].total
            acc[0] += s0
            acc[1] += s1
            self.tree.insert("", "end", values=(
                rnd.number,
                f"{s0:+}",
                f"{s1:+}",
                acc[0],
                acc[1],
            ))

        # Scroll al final
        children = self.tree.get_children()
        if children:
            self.tree.see(children[-1])

        n = len(self.game.rounds)
        self.status_var.set(f"Mano {n} completada." if n else "Partida lista. Ingresá la primera mano.")

    def _show_winner(self):
        if not self.game or self.game.winner is None:
            return
        w = self.game.winner          # ahora el type checker sabe que no es None
        self.btn_new_round.config(state="disabled")
        messagebox.showinfo(
            "🏆 ¡Fin de la partida!",
            f"¡{w.name} ganó la partida con {w.total} puntos!\n\n"
            f"Iniciá una nueva partida desde el menú."
        )

    # ── Diálogos de ayuda ─────────────────────────────────────────────────────

    def _show_card_values(self):
        dlg = tk.Toplevel(self)
        dlg.title("Valores de Fichas")
        dlg.resizable(False, False)
        text = (
            "Ficha        Puntos\n"
            "──────────────────\n"
            "As (1)       15 pts\n"
            "2            20 pts\n"
            "3 al 7        5 pts\n"
            "8 al 13      10 pts\n"
            "Comodín      50 pts\n"
        )
        ttk.Label(dlg, text=text, font=("Courier", 11), padding=16,
                  justify="left").pack()
        ttk.Button(dlg, text="Cerrar", command=dlg.destroy).pack(pady=8)

    def _show_rules(self):
        dlg = tk.Toplevel(self)
        dlg.title("Reglas de Puntaje")
        dlg.resizable(False, False)
        text = (
            "Jugada              Puntos\n"
            "───────────────────────────\n"
            "Cierre              +100 pts\n"
            "Canasta Impura      +100 pts\n"
            "Canasta Pura        +200 pts\n"
            "Muerto comprado     +100 pts\n"
            "Muerto NO comprado  -100 pts\n"
            "\n"
            "Objetivo: llegar a 3000 puntos.\n"
            "\n"
            "Para cerrar, el equipo debe tener\n"
            "al menos una canasta (pura o impura)\n"
            "y haber comprado el muerto."
        )
        ttk.Label(dlg, text=text, font=("Courier", 11), padding=16,
                  justify="left").pack()
        ttk.Button(dlg, text="Cerrar", command=dlg.destroy).pack(pady=8)


# ── Diálogo nueva partida ──────────────────────────────────────────────────────

class NewGameDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Nueva Partida")
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        frame = ttk.Frame(self, padding=20)
        frame.pack()

        ttk.Label(frame, text="Nombre del Equipo 1:").grid(row=0, column=0, sticky="w", pady=4)
        self.t1 = ttk.Entry(frame, width=24)
        self.t1.insert(0, "Equipo 1")
        self.t1.grid(row=0, column=1, padx=8)

        ttk.Label(frame, text="Nombre del Equipo 2:").grid(row=1, column=0, sticky="w", pady=4)
        self.t2 = ttk.Entry(frame, width=24)
        self.t2.insert(0, "Equipo 2")
        self.t2.grid(row=1, column=1, padx=8)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(12, 0))
        ttk.Button(btn_frame, text="✔ Comenzar",
                   command=self._confirm).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="✖ Cancelar",
                   command=self.destroy).pack(side="left", padx=4)

        self.t1.focus()
        self.t1.select_range(0, "end")

    def _confirm(self):
        n1 = self.t1.get().strip() or "Equipo 1"
        n2 = self.t2.get().strip() or "Equipo 2"
        self.result = (n1, n2)
        self.destroy()