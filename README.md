# AgentBeats Green - Werewolf Benchmark

## Run a single game

```
python -m benchmark.runner --seed 123 --max-turns 4 --max-rounds 4 --output fixtures/golden_score.json --log-jsonl fixtures/sample_log.jsonl
```

## Run multiple seeds and aggregate

```
python -m benchmark.multi --seeds-file configs/seeds.txt --max-turns 4 --max-rounds 4 --output fixtures/aggregate.json
```

## Tests

```
python -m pytest scorer/tests/test_score.py benchmark/tests/test_protocol.py
```

## Structure
- configs/: task/config seeds (placeholders).
- benchmark/: game engine, runner, multi-seed aggregator, protocol, logging, (stub) A2A server.
- agents/: scripted baseline and stubs for A2A/LLM.
- scorer/: metrics and aggregation.
- fixtures/: sample log/score outputs.
- docker/: Dockerfile and entrypoint stub.
- scripts/: CI smoke script.

## Notes
- Current default is offline scripted baseline; A2A server/adapter are stubs (HTTP echo + scripted response).
- Online mode (opt-in): start an A2A endpoint (e.g., `python scripts/a2a_gemini_proxy.py` with `GEMINI_API_KEY`) and run with `--a2a-endpoint http://localhost:8080`. Default proxy model: `gemini-2.5-flash-lite`; override with `--model`.
- Dockerfile installs requirements.txt if present; adjust as we add deps.
- Stub A2A server: `python -m benchmark.a2a_server` (returns scripted actions); HTTP client stub in `agents/a2a_adapter.py`.
- Safety heuristics are simple keyword/regex checks; no external services or classifiers.
- CI smoke: `python scripts/ci_smoke.py` or `make ci`.
- Optional A2A mode: pass `--a2a-endpoint http://host:port` to runner; actions will be fetched from that endpoint per observation (scripted fallback if no endpoint).
- Metrics: vote accuracy/focus, misvotes, flip rates, survival, and soft safety flags as proxies for deception/detection; aligned with paper emphasis (win/loss and voting behavior).

## Demo script outline (for video)
1) Build/run: `python -m benchmark.runner --seed 123 --max-turns 4 --max-rounds 4 --output fixtures/golden_score.json --log-jsonl fixtures/sample_log.jsonl`
2) Show scorecard JSON and tail JSONL log.
3) Optional: `python -m benchmark.a2a_server` (stub) and run with `--a2a-endpoint http://localhost:8080` to illustrate A2A wiring.
4) Multi-seed aggregate: `python -m benchmark.multi --seeds-file configs/seeds.txt --output fixtures/aggregate.json`

## Make targets
```
make run    # run a seeded game and write outputs
make smoke  # run minimal tests
make multi  # run multiple seeds and aggregate
make ci     # run smoke across seeds
```

## Quick setup and demo (offline default, optional API mode)
1) Install deps: `pip install -r requirements.txt`
2) Offline run (default, no keys needed):  
   `python -m benchmark.runner --seed 123 --max-turns 4 --max-rounds 4 --output fixtures/golden_score.json --log-jsonl fixtures/sample_log.jsonl`
3) Multi-seed aggregate:  
   `python -m benchmark.multi --seeds-file configs/seeds.txt --max-turns 4 --max-rounds 4 --output fixtures/aggregate.json`
4) Optional A2A/LLM mode (once you have an A2A endpoint, e.g., Gemini proxy):  
   - Set provider env (e.g., `GEMINI_API_KEY=...`) in your proxy.  
   - Run the proxy: `python scripts/a2a_gemini_proxy.py --model gemini-2.5-flash-lite --host 0.0.0.0 --port 8080`.  
   - Run benchmark with delegation:  
     `python -m benchmark.runner --seed 123 --max-turns 4 --max-rounds 4 --a2a-endpoint http://localhost:8080 --output fixtures/gemini_score.json --log-jsonl fixtures/gemini_log.jsonl`  
   - Note: offline scripted remains the default; API mode is opt-in.
   - To load `.env` automatically: `python -m dotenv run -- python scripts/a2a_gemini_proxy.py --model gemini-2.5-flash-lite --host 0.0.0.0 --port 8080`.
