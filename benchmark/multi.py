"""Run multiple seeded games and aggregate scores."""

import argparse
import json
from pathlib import Path
from typing import List

from benchmark import game
from scorer import score


def load_seeds(path: str) -> List[int]:
    seeds = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                seeds.append(int(line))
            except ValueError:
                continue
    return seeds


def main():
    parser = argparse.ArgumentParser(description="Run multiple seeds and aggregate scores.")
    parser.add_argument("--seeds-file", type=str, default="configs/seeds.txt", help="Path to seeds list.")
    parser.add_argument("--max-turns", type=int, default=8, help="Max debate turns per round.")
    parser.add_argument("--max-rounds", type=int, default=10, help="Max rounds before timeout.")
    parser.add_argument("--output", type=str, default="", help="Optional path to write aggregate JSON.")
    parser.add_argument("--a2a-endpoint", type=str, default="", help="Optional A2A endpoint (delegate actions).")
    args = parser.parse_args()

    seeds = load_seeds(args.seeds_file)
    scores = []
    for s in seeds:
        log = game.run_game(
            {
                "seed": s,
                "max_debate_turns": args.max_turns,
                "max_rounds": args.max_rounds,
                "a2a_endpoint": args.a2a_endpoint,
            }
        )
        scores.append(score.score_game(log))
    agg = score.aggregate(scores)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({"aggregate": agg, "scores": scores}, f, indent=2)

    print(json.dumps(agg, indent=2))


if __name__ == "__main__":
    main()
