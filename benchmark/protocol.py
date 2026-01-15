"""Schemas and validation for observations/actions."""

from typing import Dict, Any, List

OBS_SCHEMA = {
    "required": ["round", "phase", "role", "name", "seed", "remaining_players", "graveyard", "public_debate"],
}

ACT_SCHEMA = {
    "required": ["type"],
    "enum": ["speak", "vote", "night_power", "noop"],
}


def make_observation(
    round_num: int,
    phase: str,
    role: str,
    name: str,
    seed: int,
    remaining_players: List[str],
    graveyard: List[str],
    public_debate: List[str],
    private_info: Dict[str, Any],
) -> Dict[str, Any]:
    """Construct an observation payload for A2A agents."""
    obs = {
        "round": round_num,
        "phase": phase,
        "role": role,
        "name": name,
        "seed": seed,
        "remaining_players": remaining_players,
        "graveyard": graveyard,
        "public_debate": public_debate,
        "private": private_info,
    }
    return validate_observation(obs)


def validate_observation(obs: Dict[str, Any]) -> Dict[str, Any]:
    for key in OBS_SCHEMA["required"]:
        if key not in obs:
            raise ValueError(f"Observation missing field: {key}")
    return obs


def validate_action(action: Dict[str, Any]) -> Dict[str, Any]:
    if "type" not in action:
        raise ValueError("Action missing type")
    if action["type"] not in ACT_SCHEMA["enum"]:
        raise ValueError(f"Unsupported action type: {action['type']}")
    return action
