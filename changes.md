# Change Log

## 2025-12-03
- Context (API run before change, seed 123):
```
$ python -m benchmark.runner --seed 123 --max-turns 4 --max-rounds 4 --a2a-endpoint http://localhost:8080 --output fixtures/gemini_score.json --log-jsonl fixtures/gemini_log.jsonl
{
  "winner": "Villagers",
  "metrics": {
    "rounds_played": 2,
    "debate_turns": 8,
    "total_votes": 12,
    "villager_vote_accuracy": 1.0,
    "villager_misvote_rate": 0.0,
    "wolf_vote_focus": 0.3333333333333333,
    "wolf_on_wolf_rate": 0.6666666666666666,
    "villager_flip_rate_toward_wolves": 1.0,
    "wolf_flip_rate_toward_villagers": 1.0,
    "wolf_survival_rate": 0.0,
    "villager_survival_rate": 0.6666666666666666,
    "safety_flags": {
      "invalid_action": false,
      "toxic": false,
      "off_policy": false,
      "pii": false
    }
  },
  "seed": 123
}
```
- Change: tightened Gemini proxy prompts for Werewolves to explicitly avoid targeting other wolves during day_vote and night phases. Added role-specific hint in `scripts/a2a_gemini_proxy.py` to reduce wolf-on-wolf votes/attacks.
- Rationale: Prior runs showed high wolf_on_wolf_rate and low wolf_vote_focus, causing self-sabotage. The hint nudges wolves toward non-wolf targets to make online runs more realistic.

## 2025-12-03 (later)
- Change: reduce repetitive day chatter by nudging speak actions to be brief, single-line, and avoid repeated introductions.
- Rationale: Logs showed multiple “Derek” day messages repeating intros; added guidance in proxy prompt to keep speak concise/one-liner and reduce repetition.

## 2025-12-04
- Change: tightened Gemini proxy prompts to encourage useful suspicion/reasons instead of generic intros; day speak now asks to name a suspect and why; day_vote asks to pick a suspect (optional reason) and wolves are reminded to avoid targeting other wolves across day/day_vote/night.
- Rationale: Prior API runs showed shallow behavior (introductions then voting without reasoning, occasional wolf self-targeting). Prompt tweaks aim for paper-aligned social reasoning and reduce wolf self-sabotage.

## 2025-12-04 (later)
- Change: day prompt now branches—if no debate yet, ask for info/observations with no accusations; once debate exists, require citing a suspect from remaining_players with a reason tied to debate. Keeps early turns from random accusations.
- Rationale: Early accusations against “quiet” players before anyone speaks were unrealistic; this reduces blind accusations and encourages referencing actual debate content.

## 2025-12-04 (latest)
- Change: further refined day speak prompt to discourage repeated lines and generic "quiet" accusations; requires citing a specific speaker/line and avoiding repetition.
- Rationale: Logs still showed duplicate responses and shallow "quiet" accusations; this nudges more grounded, non-repetitive suspicion.
