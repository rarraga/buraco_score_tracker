"""
game.py - Lógica del juego Buraco
"""

from dataclasses import dataclass, field
from typing import List, Optional
import json
import os

# ── Valores de las fichas ──────────────────────────────────────────────────────
CARD_VALUES = {
    1: 15,
    2: 20,
    **{n: 5 for n in range(3, 8)},   # 3 al 7
    **{n: 10 for n in range(8, 14)}, # 8 al 13
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
    """Puntuación de una mano para un equipo."""
    team_name: str
    cards_down: int = 0          # Puntos por fichas bajadas
    cards_remaining: int = 0     # Puntos por fichas NO bajadas (se restan)
    cierre: bool = False
    canastas_puras: int = 0
    canastas_impuras: int = 0
    muerto_bought: bool = False
    muerto_available: bool = True  # Si el muerto fue ofrecido en esta mano

    @property
    def total(self) -> int:
        pts = self.cards_down
        pts -= self.cards_remaining
        if self.cierre:
            pts += BONUS["cierre"]
        pts += self.canastas_puras * BONUS["canasta_pura"]
        pts += self.canastas_impuras * BONUS["canasta_impura"]
        if self.muerto_available:
            if self.muerto_bought:
                pts += BONUS["muerto"]
            else:
                pts -= BONUS["muerto"]  # Penalización por no comprar
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
    def __init__(self, team1_name: str = "Equipo 1", team2_name: str = "Equipo 2"):
        self.teams = [Team(team1_name), Team(team2_name)]
        self.rounds: List[Round] = []
        self.current_round = 1
        self.winner: Optional[Team] = None

    @property
    def is_over(self) -> bool:
        return self.winner is not None

    def add_round(self, score1: RoundScore, score2: RoundScore):
        """Registra los puntajes de una mano."""
        r = Round(self.current_round, [score1, score2])
        self.rounds.append(r)
        self.teams[0].scores.append(score1.total)
        self.teams[1].scores.append(score2.total)
        self.current_round += 1
        self._check_winner()

    def _check_winner(self):
        winners = [t for t in self.teams if t.has_won]
        if winners:
            # Si ambos superan 3000, gana el de mayor puntaje
            self.winner = max(winners, key=lambda t: t.total)

    def undo_last_round(self):
        """Deshace la última mano registrada."""
        if not self.rounds:
            return
        self.rounds.pop()
        for team in self.teams:
            if team.scores:
                team.scores.pop()
        self.current_round -= 1
        self.winner = None
        # Re-check winner after undo
        self._check_winner()

    def score_summary(self) -> str:
        lines = [f"{'─'*40}"]
        lines.append(f"{'PARTIDA BURACO':^40}")
        lines.append(f"{'─'*40}")
        for t in self.teams:
            lines.append(f"  {t.name:<20} {t.total:>6} pts")
        lines.append(f"{'─'*40}")
        lines.append(f"  Objetivo: {TARGET_SCORE} puntos")
        if self.winner:
            lines.append(f"\n🏆 ¡GANADOR: {self.winner.name}!")
        return "\n".join(lines)

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
        g = cls(teams[0]["name"], teams[1]["name"])
        g.teams[0].scores = teams[0]["scores"]
        g.teams[1].scores = teams[1]["scores"]
        g.current_round = data["current_round"]
        g._check_winner()
        return g


# ── Calculadora de fichas ──────────────────────────────────────────────────────
def calculate_cards(cards: dict) -> int:
    """
    cards: {numero_o_'comodin': cantidad}
    Ej: {1: 2, 7: 3, 'comodin': 1}
    """
    total = 0
    for card, qty in cards.items():
        if card in CARD_VALUES:
            total += CARD_VALUES[card] * qty
    return total