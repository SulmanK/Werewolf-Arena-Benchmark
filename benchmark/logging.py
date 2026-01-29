"""Logging helpers."""

import json
from typing import List, Dict, Any


def write_jsonl(path: str, records: List[Dict[str, Any]]) -> None:
    """Write a list of dict records to JSONL."""
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def game_log_to_records(
    game_log: Dict[str, Any],
    meta: Dict[str, Any] | None = None,
    metrics: Dict[str, Any] | None = None,
) -> List[Dict[str, Any]]:
    """Flatten a game log into per-round records for JSONL."""
    records: List[Dict[str, Any]] = []
    meta = meta or {}
    for r in game_log.get("rounds", []):
        round_id = r.get("round")
        records.append({"type": "night", "round": round_id, **meta, **(r.get("night") or {})})
        for speaker, utterance in r.get("debate", []):
            records.append(
                {
                    "type": "debate",
                    "round": round_id,
                    **meta,
                    "speaker": speaker,
                    "utterance": utterance,
                }
            )
        records.append({"type": "votes", "round": round_id, **meta, "votes": r.get("votes", {})})
    records.append(
        {
            "type": "summary",
            **meta,
            "winner": game_log.get("winner"),
            "seed": game_log.get("seed"),
            "roles": game_log.get("roles", {}),
            "metrics": metrics or {},
        }
    )
    return records
