"""
ui.py - Interfaz principal de la aplicación Buraco
"""

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

        self.after(0, self._set_fullscreen)

    def _set_fullscreen(self):
        try:
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
        style.configure("Score.TLabel",  font=("Segoe UI", 36, "bold"))
        style.configure("Sub.TLabel",    font=("Segoe UI", 10))
        style.configure("Win.TLabel",    font=("Segoe UI", 14, "bold"), foreground="#2e7d32")
        style.configure("Round.Treeview", font=("Segoe UI", 10), rowheight=24)
        style.configure("Round.Treeview.Heading", font=("Segoe UI", 10, "bold"))
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
        game_menu.add_command(label="Nueva partida",    command=self._new_game,  accelerator="Ctrl+N")
        game_menu.add_command(label="Abrir partida...", command=self._load_game, accelerator="Ctrl+O")
        game_menu.add_command(label="Guardar partida...", command=self._save_game, accelerator="Ctrl+S")
        game_menu.add_separator()
        game_menu.add_command(label="Salir", command=self.quit)
        menubar.add_cascade(label="Partida", menu=game_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Valores de fichas", command=self._show_card_values)
        help_menu.add_command(label="Reglas de puntaje",  command=self._show_rules)
        menubar.add_cascade(label="Ayuda", menu=help_menu)

        self.config(menu=menubar)
        self.bind("<Control-n>", lambda _: self._new_game())
        self.bind("<Control-o>", lambda _: self._load_game())
        self.bind("<Control-s>", lambda _: self._save_game())

    # ── Layout principal ──────────────────────────────────────────────────────

    def _build_scrollable_main(self):
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._canvas = tk.Canvas(self, highlightthickness=0)
        self._vscroll = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._vscroll.set)

        self._canvas.grid(row=0, column=0, sticky="nsew")
        self._vscroll.grid(row=0, column=1, sticky="ns")

        self.main_frame = ttk.Frame(self._canvas, padding=12)
        self._canvas_window = self._canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=0)
        self.main_frame.rowconfigure(3, weight=0)

        self._canvas.bind("<Configure>",       self._on_canvas_resize)
        self.main_frame.bind("<Configure>",    self._on_frame_resize)
        self._canvas.bind_all("<MouseWheel>",  self._on_mousewheel)
        self._canvas.bind_all("<Button-4>",    self._on_mousewheel)
        self._canvas.bind_all("<Button-5>",    self._on_mousewheel)

        self._build_main_content()

    def _on_canvas_resize(self, event):
        canvas_w, canvas_h = event.width, event.height
        self._canvas.itemconfig(self._canvas_window, width=canvas_w)
        frame_h = self.main_frame.winfo_reqheight()
        self._canvas.itemconfig(self._canvas_window, height=max(frame_h, canvas_h))
        self._canvas.configure(scrollregion=(0, 0, canvas_w, max(frame_h, canvas_h)))

    def _on_frame_resize(self, _event=None):
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

        # ── Fila 0: Marcador (se reconstruye al iniciar partida) ──────────────
        self.score_frame = ttk.Frame(self.main_frame)
        self.score_frame.grid(row=0, column=0, sticky="ew", pady=(0, PAD))
        self.team_panels: list[dict] = []

        # ── Fila 1: Historial ─────────────────────────────────────────────────
        self.hist_frame = ttk.LabelFrame(self.main_frame,
                                         text="  Historial de Manos  ", padding=8)
        self.hist_frame.grid(row=1, column=0, sticky="nsew", pady=(0, PAD))
        self.hist_frame.rowconfigure(0, weight=1)
        self.hist_frame.columnconfigure(0, weight=1)

        self._build_history_table(["Equipo 1", "Equipo 2"])  # placeholder hasta iniciar partida

        # ── Fila 2: Botones ───────────────────────────────────────────────────
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.grid(row=2, column=0, sticky="ew", pady=(0, 4))
        btn_frame.columnconfigure(1, weight=1)

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

    def _build_score_panels(self, team_names: list[str]):
        """Construye los paneles de puntaje dinámicamente según la cantidad de equipos."""
        for widget in self.score_frame.winfo_children():
            widget.destroy()
        self.team_panels = []

        n = len(team_names)
        for i in range(n):
            self.score_frame.columnconfigure(i, weight=1)

        for i, name in enumerate(team_names):
            col = ttk.Frame(self.score_frame, relief="groove", padding=14)
            padx = (0, 4) if i < n - 1 else (4, 0)
            if n == 1:
                padx = (0, 0)
            elif i == 0:
                padx = (0, 4)
            elif i == n - 1:
                padx = (4, 0)
            else:
                padx = (4, 4)  # panel del medio en 3 jugadores
            col.grid(row=0, column=i, sticky="ew", padx=padx)
            col.columnconfigure(0, weight=1)

            name_var  = tk.StringVar(value=name)
            score_var = tk.StringVar(value="0")
            diff_var  = tk.StringVar(value=f"Faltan {TARGET_SCORE} pts")

            ttk.Label(col, textvariable=name_var,
                      style="Header.TLabel", anchor="center").grid(row=0, column=0, sticky="ew")
            ttk.Label(col, textvariable=score_var,
                      style="Score.TLabel",  anchor="center").grid(row=1, column=0, sticky="ew")
            ttk.Label(col, textvariable=diff_var,
                      style="Sub.TLabel",    anchor="center").grid(row=2, column=0, sticky="ew")
            prog = ttk.Progressbar(col, maximum=TARGET_SCORE, mode="determinate",
                                   style="Green.Horizontal.TProgressbar")
            prog.grid(row=3, column=0, sticky="ew", pady=(6, 2))

            self.team_panels.append({
                "frame": col, "name": name_var,
                "score": score_var, "diff": diff_var, "prog": prog,
            })

    def _build_history_table(self, team_names: list[str]):
        """Reconstruye la tabla del historial con columnas dinámicas."""
        for widget in self.hist_frame.winfo_children():
            widget.destroy()

        short = [n[:12] for n in team_names]
        cols = ["#"] + short + [f"Acum. {n[:8]}" for n in short]

        self.tree = ttk.Treeview(self.hist_frame, columns=cols,
                                  show="headings", style="Round.Treeview")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center", stretch=True,
                             width=50 if c == "#" else 110)
        self.tree.column("#", width=50, stretch=False)
        self.tree.grid(row=0, column=0, sticky="nsew")

        tree_scroll = ttk.Scrollbar(self.hist_frame, orient="vertical",
                                    command=self.tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=tree_scroll.set)

    def _show_welcome(self):
        self._build_score_panels(["—", "—"])
        for p in self.team_panels:
            p["score"].set("—")
            p["diff"].set("")
            p["prog"]["value"] = 0

    # ── Acciones ──────────────────────────────────────────────────────────────

    def _new_game(self):
        # ── Aviso si hay una partida en curso ─────────────────────────────────
        if self.game and not self.game.is_over and self.game.rounds:
            response = _GameInProgressDialog(self).response
            if response == "cancel":
                return
            if response == "save":
                self._save_game()

        dlg = NewGameDialog(self)
        self.wait_window(dlg)
        if not dlg.result:
            return

        names = dlg.result
        self.game = Game(names)
        self._build_score_panels(names)
        self._build_history_table(names)
        self._refresh_ui()
        self.btn_new_round.config(state="normal")
        self.btn_undo.config(state="disabled")
        self.status_var.set(f"¡Partida iniciada! Objetivo: {TARGET_SCORE} puntos.")

    def _add_round(self):
        if not self.game or self.game.is_over:
            return
        names = [t.name for t in self.game.teams]
        dlg = RoundDialog(self, self.game.current_round, names)
        self.wait_window(dlg)

        scores = list(dlg.result)
        if any(not isinstance(s, RoundScore) for s in scores):
            return

        self.game.add_round(scores)
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
            names = [t.name for t in self.game.teams]
            self._build_score_panels(names)
            self._build_history_table(names)
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

        for i, team in enumerate(self.game.teams):
            if i >= len(self.team_panels):
                break
            p = self.team_panels[i]
            p["name"].set(team.name)
            p["score"].set(str(team.total))
            if team.has_won:
                p["diff"].set("¡GANADOR! 🏆")
            else:
                p["diff"].set(f"Faltan {TARGET_SCORE - team.total} pts")
            p["prog"]["value"] = min(team.total, TARGET_SCORE)

        # Historial
        self.tree.delete(*self.tree.get_children())
        n = self.game.num_teams
        acc = [0] * n
        for rnd in self.game.rounds:
            round_scores = [rnd.scores[i].total for i in range(n)]
            for i in range(n):
                acc[i] += round_scores[i]
            self.tree.insert("", "end", values=(
                rnd.number,
                *[f"{s:+}" for s in round_scores],
                *[str(a) for a in acc],
            ))

        children = self.tree.get_children()
        if children:
            self.tree.see(children[-1])

        rounds_count = len(self.game.rounds)
        self.status_var.set(
            f"Mano {rounds_count} completada."
            if rounds_count else "Partida lista. Ingresá la primera mano."
        )

    def _show_winner(self):
        if not self.game or self.game.winner is None:
            return
        w = self.game.winner
        self.btn_new_round.config(state="disabled")

        # Mensaje diferenciado según si hubo empate en 3000+
        if self.game.was_tied_win:
            others = [t for t in self.game.teams if t is not w]
            others_str = " y ".join(f"{t.name} ({t.total} pts)" for t in others)
            msg = (
                f"Varios equipos superaron {TARGET_SCORE} puntos en la misma mano.\n\n"
                f"  {others_str}\n"
                f"  {w.name}: {w.total} pts  ← Mayor puntaje\n\n"
                f"🏆 ¡Gana {w.name}!"
            )
        else:
            msg = f"¡{w.name} llegó a {w.total} puntos!\n\n🏆 ¡{w.name} gana la partida!"

        messagebox.showinfo("🏆 ¡Fin de la partida!", msg)

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
        ttk.Label(dlg, text=text, font=("Courier", 11), padding=16, justify="left").pack()
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
        ttk.Label(dlg, text=text, font=("Courier", 11), padding=16, justify="left").pack()
        ttk.Button(dlg, text="Cerrar", command=dlg.destroy).pack(pady=8)


# ── Diálogo: partida en curso ──────────────────────────────────────────────────

class _GameInProgressDialog(tk.Toplevel):
    """
    Aparece cuando el usuario intenta iniciar una nueva partida
    con una partida activa en curso.
    response: "save" | "discard" | "cancel"
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Partida en curso")
        self.resizable(False, False)
        self.grab_set()
        self.response = "cancel"

        frame = ttk.Frame(self, padding=20)
        frame.pack()

        ttk.Label(frame,
                  text="⚠️  Estás en una partida en curso.",
                  font=("Segoe UI", 11, "bold")).pack(pady=(0, 6))
        ttk.Button(frame, text="💾  Guardar la partida actual",
                   width=40, command=self._save).pack(pady=3)
        ttk.Button(frame, text="🗑️  Descartar la partida actual",
                   width=40, command=self._discard).pack(pady=3)
        ttk.Button(frame, text="✖  Cancelar (volver a la partida actual)",
                   width=40, command=self._cancel).pack(pady=(12, 0))

        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.wait_window()

    def _save(self):
        self.response = "save"
        self.destroy()

    def _discard(self):
        self.response = "discard"
        self.destroy()

    def _cancel(self):
        self.response = "cancel"
        self.destroy()


# ── Diálogo: nueva partida ─────────────────────────────────────────────────────

class NewGameDialog(tk.Toplevel):
    """
    Selección de cantidad de jugadores y nombres.
    - 2 jugadores → 2 nombres individuales
    - 3 jugadores → 3 nombres individuales
    - 4 jugadores → 2 nombres de equipo (equipos de 2)
    result: list[str] con los nombres, o None si se canceló
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Nueva Partida")
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        self._num_players = tk.IntVar(value=4)
        self._entries: list[ttk.Entry] = []

        self._build_ui()

    def _build_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack()

        # ── Selector de jugadores ─────────────────────────────────────────────
        ttk.Label(frame, text="Cantidad de jugadores:",
                  font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        btn_row = ttk.Frame(frame)
        btn_row.grid(row=1, column=0, columnspan=2, pady=(0, 12))
        for n, label in [(2, "2 jugadores"), (3, "3 jugadores"), (4, "4 jugadores (2 equipos)")]:
            ttk.Radiobutton(btn_row, text=label, variable=self._num_players,
                            value=n, command=self._refresh_names).pack(side="left", padx=8)

        ttk.Separator(frame, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        # ── Contenedor de nombres (se regenera al cambiar cantidad) ───────────
        self._names_frame = ttk.Frame(frame)
        self._names_frame.grid(row=3, column=0, columnspan=2)
        self._refresh_names()

        # ── Botones ───────────────────────────────────────────────────────────
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(16, 0))
        ttk.Button(btn_frame, text="✔ Comenzar",
                   command=self._confirm).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="✖ Cancelar",
                   command=self.destroy).pack(side="left", padx=4)

    def _refresh_names(self):
        for w in self._names_frame.winfo_children():
            w.destroy()
        self._entries = []

        n = self._num_players.get()

        if n == 4:
            labels   = ["Nombre del Equipo 1:", "Nombre del Equipo 2:"]
            defaults = ["Equipo 1", "Equipo 2"]
            ttk.Label(self._names_frame,
                      text="(4 jugadores: 2 equipos de 2 personas)",
                      foreground="gray").grid(row=0, column=0, columnspan=2,
                                              sticky="w", pady=(0, 8))
            offset = 1
        elif n == 3:
            labels   = ["Nombre del Jugador 1:", "Nombre del Jugador 2:", "Nombre del Jugador 3:"]
            defaults = ["Jugador 1", "Jugador 2", "Jugador 3"]
            ttk.Label(self._names_frame,
                      text="(3 jugadores individuales)",
                      foreground="gray").grid(row=0, column=0, columnspan=2,
                                              sticky="w", pady=(0, 8))
            offset = 1
        else:
            labels   = ["Nombre del Jugador 1:", "Nombre del Jugador 2:"]
            defaults = ["Jugador 1", "Jugador 2"]
            ttk.Label(self._names_frame,
                      text="(2 jugadores individuales)",
                      foreground="gray").grid(row=0, column=0, columnspan=2,
                                              sticky="w", pady=(0, 8))
            offset = 1

        for i, (label, default) in enumerate(zip(labels, defaults)):
            ttk.Label(self._names_frame, text=label).grid(
                row=i + offset, column=0, sticky="w", pady=4, padx=(0, 8))
            entry = ttk.Entry(self._names_frame, width=24)
            entry.insert(0, default)
            entry.grid(row=i + offset, column=1, pady=4)
            self._entries.append(entry)

        if self._entries:
            self._entries[0].focus()
            self._entries[0].select_range(0, "end")

    def _confirm(self):
        names = [e.get().strip() or f"Jugador {i+1}" for i, e in enumerate(self._entries)]
        # Para 4 jugadores se usan los 2 nombres de equipo
        self.result = names
        self.destroy()