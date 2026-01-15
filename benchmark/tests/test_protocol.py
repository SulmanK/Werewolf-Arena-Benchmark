from benchmark import protocol


def test_validate_observation():
    obs = protocol.make_observation(
        round_num=0,
        phase="day",
        role="Villager",
        name="A",
        seed=1,
        remaining_players=["A", "B"],
        graveyard=[],
        public_debate=["A: hi"],
        private_info={},
    )
    assert obs["phase"] == "day"


def test_validate_action():
    act = {"type": "speak", "content": "hello"}
    res = protocol.validate_action(act)
    assert res["type"] == "speak"
