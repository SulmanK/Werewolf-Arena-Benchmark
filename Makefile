.PHONY: run smoke test multi ci

run:
	python -m benchmark.runner --seed 123 --max-turns 4 --max-rounds 4 --output fixtures/golden_score.json --log-jsonl fixtures/sample_log.jsonl

smoke:
	python -m pytest scorer/tests/test_score.py benchmark/tests/test_protocol.py

test: smoke

multi:
	python -m benchmark.multi --seeds-file configs/seeds.txt --output fixtures/aggregate.json

ci:
	python scripts/ci_smoke.py
