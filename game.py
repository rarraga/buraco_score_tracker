"""
game.py - Lógica del juego Buraco
"""

from dataclasses import dataclass, field
from typing import List, Optional
import json

# ── Valores de las fichas ──────────────────────────────────────────────────────
CARD_VALUES = {
    1: 15,
    2: 20,
    **{n: 5 for n in range(3, 8)},   # 3 al 7
    **{n: 10 for n in range(8, 14)}, # 8 al 13 (J=11, Q=12, K=13)
    "comodin": 50,
}

# ── Bonus por tipo de jugada ───────────────────────────────────────────────────
BONUS = {
    "cierre": 100,
    "canasta_pura": 200,
    "canasta_impura": 100,
    "muerto": 100,
}

TARGET_SCORE = 3000


@dataclass
class RoundScore:
    """Puntuación de una mano para un equipo/jugador."""
    team_name: str
    cards_down: int = 0
    cards_remaining: int = 0
    cierre: bool = False
    canastas_puras: int = 0
    canastas_impuras: int = 0
    muerto_bought: bool = False
    muerto_available: bool = True

    @property
    def total(self) -> int:
        pts = self.cards_down - self.cards_remaining
        if self.cierre:
            pts += BONUS["cierre"]
        pts += self.canastas_puras   * BONUS["canasta_pura"]
        pts += self.canastas_impuras * BONUS["canasta_impura"]
        if self.muerto_available:
            pts += BONUS["muerto"] if self.muerto_bought else -BONUS["muerto"]
        return pts

    def breakdown(self) -> str:
        lines = [
            f"  Fichas bajadas:     +{self.cards_down}",
            f"  Fichas en mano:     -{self.cards_remaining}",
        ]
        if self.cierre:
            lines.append(f"  Cierre:             +{BONUS['cierre']}")
        if self.canastas_puras:
            lines.append(f"  Canastas puras x{self.canastas_puras}: +{self.canastas_puras * BONUS['canasta_pura']}")
        if self.canastas_impuras:
            lines.append(f"  Canastas impuras x{self.canastas_impuras}: +{self.canastas_impuras * BONUS['canasta_impura']}")
        if self.muerto_available:
            if self.muerto_bought:
                lines.append(f"  Muerto comprado:    +{BONUS['muerto']}")
            else:
                lines.append(f"  Muerto NO comprado: -{BONUS['muerto']}")
        lines.append(f"  ─────────────────────────")
        lines.append(f"  SUBTOTAL:           {self.total:+}")
        return "\n".join(lines)


@dataclass
class Team:
    name: str
    scores: List[int] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(self.scores)

    @property
    def has_won(self) -> bool:
        return self.total >= TARGET_SCORE


@dataclass
class Round:
    number: int
    scores: List[RoundScore] = field(default_factory=list)


class Game:
    def __init__(self, team_names: list[str]):
        """
        team_names: lista de 2 o 3 nombres (equipos o jugadores individuales).
        - 2 nombres → partida de 2 equipos/jugadores
        - 3 nombres → partida de 3 jugadores individuales
        Para 4 jugadores se usan 2 nombres de equipo (equipos de 2).
        """
        if len(team_names) < 2 or len(team_names) > 3:
            raise ValueError("Se requieren 2 o 3 participantes.")
        self.teams: List[Team] = [Team(n) for n in team_names]
        self.rounds: List[Round] = []
        self.current_round = 1
        self.winner: Optional[Team] = None
        # Indica si la victoria fue por empate en 3000+ (para el mensaje de UI)
        self.was_tied_win: bool = False

    @property
    def num_teams(self) -> int:
        return len(self.teams)

    @property
    def is_over(self) -> bool:
        return self.winner is not None

    def add_round(self, scores: list[RoundScore]):
        """Registra los puntajes de una mano. scores debe tener un elemento por equipo."""
        if len(scores) != self.num_teams:
            raise ValueError(f"Se esperaban {self.num_teams} puntajes, se recibieron {len(scores)}.")
        r = Round(self.current_round, list(scores))
        self.rounds.append(r)
        for team, score in zip(self.teams, scores):
            team.scores.append(score.total)
        self.current_round += 1
        self._check_winner()

    def _check_winner(self):
        winners = [t for t in self.teams if t.has_won]
        if not winners:
            return
        # Si solo uno superó 3000, ese gana directamente
        if len(winners) == 1:
            self.winner = winners[0]
            self.was_tied_win = False
        else:
            # Varios superaron 3000 en la misma mano → gana el de mayor puntaje
            self.winner = max(winners, key=lambda t: t.total)
            self.was_tied_win = True

    def undo_last_round(self):
        if not self.rounds:
            return
        self.rounds.pop()
        for team in self.teams:
            if team.scores:
                team.scores.pop()
        self.current_round -= 1
        self.winner = None
        self.was_tied_win = False
        self._check_winner()

    def to_dict(self) -> dict:
        return {
            "teams": [{"name": t.name, "scores": t.scores} for t in self.teams],
            "current_round": self.current_round,
            "winner": self.winner.name if self.winner else None,
        }

    def save(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "Game":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        teams = data["teams"]
        g = cls([t["name"] for t in teams])
        for team_obj, team_data in zip(g.teams, teams):
            team_obj.scores = team_data["scores"]
        g.current_round = data["current_round"]
        g._check_winner()
        return g


# ── Calculadora de fichas ──────────────────────────────────────────────────────
def calculate_cards(cards: dict) -> int:
    total = 0
    for card, qty in cards.items():
        if card in CARD_VALUES:
            total += CARD_VALUES[card] * qty
    return total