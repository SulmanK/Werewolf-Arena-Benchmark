from benchmark import game


def test_run_game_smoke():
    res = game.run_game({"seed": 42, "max_debate_turns": 4, "max_rounds": 4})
    assert res["winner"] in ("Villagers", "Werewolves", "Timeout")
    assert "survivors" in res


def test_run_game_a2a_mode():
    # Using no actual server; the engine will still run scripted if no endpoint.
    res = game.run_game({"seed": 99, "max_debate_turns": 2, "max_rounds": 2, "a2a_endpoint": ""})
    assert res["winner"] in ("Villagers", "Werewolves", "Timeout")
