"""Adapter for communicating with external A2A agents (HTTP JSON)."""

import os
import requests
from typing import Dict, Any


class A2AClient:
    def __init__(self, url: str):
        self.url = url.rstrip("/")

    def send_action(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Send observation to external agent and return parsed action."""
        timeout = float(os.environ.get("A2A_TIMEOUT", "30"))
        resp = requests.post(self.url, json=observation, timeout=timeout)
        resp.raise_for_status()
        return resp.json()


class A2AAgent:
    """Wraps A2AClient into agent-like interface."""

    def __init__(self, name: str, role: str, seed: int, client: A2AClient):
        self.name = name
        self.role = role
        self.seed = seed
        self.client = client
        self.alive = True
        self.seer_checks = []

    def _private_obs(self, wolves):
        if self.role == "Werewolf":
            return {"wolves": wolves or []}
        if self.role == "Seer":
            return {"seer_checks": list(self.seer_checks)}
        return {}

    def speak(self, debate_history, round_num=0, alive_players=None, graveyard=None, wolves=None):
        obs = {
            "round": round_num,
            "phase": "day",
            "role": self.role,
            "name": self.name,
            "seed": self.seed,
            "remaining_players": alive_players or [],
            "graveyard": graveyard or [],
            "public_debate": debate_history,
            "private": self._private_obs(wolves),
        }
        action = self.client.send_action(obs)
        return action.get("content", "")

    def vote(self, players, debate_history=None, round_num=0, graveyard=None, wolves=None):
        obs = {
            "round": round_num,
            "phase": "day_vote",
            "role": self.role,
            "name": self.name,
            "seed": self.seed,
            "remaining_players": players or [],
            "graveyard": graveyard or [],
            "public_debate": debate_history or [],
            "private": self._private_obs(wolves),
        }
        action = self.client.send_action(obs)
        return action.get("target")

    def night_power(self, players, wolves, round_num=0, graveyard=None):
        obs = {
            "round": round_num,
            "phase": "night",
            "role": self.role,
            "name": self.name,
            "seed": self.seed,
            "remaining_players": players or [],
            "graveyard": graveyard or [],
            "public_debate": [],
            "private": self._private_obs(wolves),
        }
        action = self.client.send_action(obs)
        return action.get("target")

    def mark_dead(self):
        self.alive = False

    def update_seer_inspection(self, target: str, role: str):
        self.seer_checks.append({"target": target, "role": role})
