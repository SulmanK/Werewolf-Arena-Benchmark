# Werewolf Arena Paper Summary and Agentic Port Analysis

## Paper Overview (Werewolf Arena: Social Deduction for LLMs)
- **Goal:** Evaluate LLMs on social reasoning/deception via the game Werewolf (Mafia). Measure ability to persuade, detect deception, and coordinate under hidden roles.
- **Setup:** 8-player games with 2 Werewolves, 1 Seer, 1 Doctor, rest Villagers. Night phase (eliminate/protect/unmask), day debate and vote, repeated until wolves dead or reach parity.
- **Agents:** LLM-driven roles using structured prompts (bidding, debate, vote, night actions). Uses OpenAI/Gemini models in the reference code.
- **Metrics:** Win rates by role, vote accuracy, elimination outcomes, and qualitative analysis of debates. Emphasis on social reasoning (persuasion, bluffing, detection).
- **Findings (high level):** LLMs can coordinate and bluff but are brittle; vote accuracy and deception success vary by model; social deduction highlights weaknesses in consistency and detection of hidden adversaries.

## What We Are Building
- **Green benchmark:** A reproducible Werewolf evaluation harness for AgentBeats (Green phase), aligned with the paper's protocol but packaged as a deterministic, headless benchmark with scripted baselines and A2A compatibility.
- **Online-major use case:** Primary target is to plug in external LLM calls (e.g., Gemini) via A2A; offline scripted path remains for reproducibility and CI.
- **Offline baseline:** Deterministic scripted agents (no API keys/network) for reproducibility, Docker/CI, and quick runs.
- **Online A2A:** A2A delegation hook so a white agent (LLM-backed, e.g., Gemini) can play roles via an HTTP endpoint. Mirrors the tau-bench agentify pattern.
- **Scoring:** Structured scorecards with vote accuracy/focus, misvotes, flip rates, survival rates, soft safety flags; win/loss remains the core outcome.
- **Logging:** JSON scorecards + JSONL step logs for reproducibility and debugging.

## Why Agentic Port Matters
- **Reproducibility:** The paper?s setup depends on remote LLM calls; we need a deterministic, offline baseline and pinned configs to make results rerunnable by any A2A-compatible agent.
- **Interop (A2A):** By defining observations/actions and exposing an A2A endpoint, any agent can be plugged in (scripted, local model, or remote LLM) without code changes to the harness.
- **Benchmarking social reasoning:** Social deduction stresses persuasion, deception detection, and coordination?capabilities not captured by simple QA or coding benchmarks. Agentic packaging lets teams systematically test and compare agents under these pressures.
- **Deployment readiness:** Docker/CI and deterministic fixtures reduce friction for competitors and reviewers, addressing the pain points of setup, logging, metrics, and data management.

## Design Choices vs. Paper
- **Protocol fidelity:** Keep roles, phases, and win conditions from the paper (8 players, 2 wolves, seer, doctor; night/day, vote/exile).
- **Determinism:** Seed role assignment, speaker selection, and actions for scripted baselines; provide seed lists and fixtures.
- **Metrics:** Extend beyond win rate to vote accuracy/focus, flips, survival, and soft safety; no heavy classifiers by default (paper-aligned emphasis on voting outcomes/deception).
- **Modes:** Offline scripted default; A2A/LLM mode opt-in for parity with the paper?s LLM runs.

## Next Steps (for the agentic port)
- Finalize A2A proxy for Gemini (obs ? prompt ? action) and endpoint mapping so specific roles delegate to the external agent.
- Keep CI/offline runs as default; document API-mode setup (keys, model, costs) as optional.
- Add golden fixtures/checksums and polish README/demo to show both offline and online runs.
