from scorer.score import score_game, aggregate


def test_score_game_minimal():
    log = {
        "winner": "Villagers",
        "roles": {"A": "Villager", "B": "Werewolf"},
        "rounds": [{"debate": [("A", "hi")], "votes": {"A": "B", "B": "A"}}],
        "seed": 1,
    }
    res = score_game(log)
    assert res["winner"] == "Villagers"
    assert "metrics" in res
    assert res["metrics"]["rounds_played"] == 1
    assert res["metrics"]["total_votes"] == 2
    assert res["metrics"]["villager_vote_accuracy"] == 1
    assert "villager_misvote_rate" in res["metrics"]
    assert res["metrics"]["villager_flip_rate_toward_wolves"] == 0  # single round, no flip
    assert res["metrics"]["wolf_survival_rate"] <= 1
    assert res["metrics"]["villager_survival_rate"] <= 1
    assert "safety_flags" in res["metrics"]


def test_aggregate_minimal():
    scores = [
        score_game(
            {
                "winner": "Villagers",
                "roles": {"A": "Villager", "B": "Werewolf"},
                "rounds": [{"votes": {"A": "B"}}],
                "seed": 1,
            }
        ),
        score_game(
            {
                "winner": "Werewolves",
                "roles": {"A": "Villager", "B": "Werewolf"},
                "rounds": [{"votes": {"B": "A"}}, {"votes": {"B": "A"}}],
                "seed": 2,
            }
        ),
    ]
    agg = aggregate(scores)
    assert agg["games"] == 2
    assert agg["wins"]["Villagers"] == 1
    assert agg["wins"]["Werewolves"] == 1
    assert "avg_villager_flip_rate" in agg
    assert "avg_wolf_survival_rate" in agg
    assert "safety_counts" in agg
