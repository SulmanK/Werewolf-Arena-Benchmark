"""Deterministic scripted baseline agent (no LM calls)."""

import random
from typing import List, Optional


class ScriptedAgent:
    """Rule-based agent for reproducible baselines."""

    def __init__(self, name: str, role: str, seed: int):
        self.name = name
        self.role = role
        self.alive = True
        self.seed = seed
        self.rng = random.Random(seed + hash(name) % 1000)
        self.known_wolf: Optional[str] = None

    def mark_dead(self):
        self.alive = False

    def speak(
        self,
        debate_history: List[str],
        round_num: int = 0,
        alive_players: Optional[List[str]] = None,
        graveyard: Optional[List[str]] = None,
        wolves: Optional[List[str]] = None,
    ) -> str:
        if not self.alive:
            return ""
        if self.role == "Werewolf":
            # Deflect to someone already mentioned or random
            if debate_history:
                target = self.rng.choice(debate_history).split(":", 1)[0]
            else:
                target = "someone quiet"
            return f"I suspect {target} is acting strange."
        if self.role == "Seer" and self.known_wolf:
            return f"I have reason to believe {self.known_wolf} is not on our side."
        if self.role == "Doctor":
            return "Stay calm; let's avoid rash votes."
        return "I need more evidence before voting decisively."

    def vote(
        self,
        alive_players: List[str],
        round_num: int = 0,
        graveyard: Optional[List[str]] = None,
        wolves: Optional[List[str]] = None,
    ) -> Optional[str]:
        candidates = [p for p in alive_players if p != self.name]
        if not candidates:
            return None
        if self.role == "Werewolf":
            non_wolves = [p for p in candidates if p != self.known_wolf]
            pool = non_wolves or candidates
        else:
            pool = candidates
        return self.rng.choice(pool)

    def night_power(
        self,
        alive_players: List[str],
        wolves: List[str],
        round_num: int = 0,
        graveyard: Optional[List[str]] = None,
    ) -> Optional[str]:
        if not self.alive:
            return None
        if self.role == "Werewolf":
            pool = [p for p in alive_players if p not in wolves]
            return self.rng.choice(pool) if pool else None
        if self.role == "Doctor":
            return self.rng.choice(alive_players) if alive_players else None
        if self.role == "Seer":
            choices = [p for p in alive_players if p != self.name]
            return self.rng.choice(choices) if choices else None
        return None

    def update_seer_inspection(self, target: str, role: str):
        if role == "Werewolf":
            self.known_wolf = target
