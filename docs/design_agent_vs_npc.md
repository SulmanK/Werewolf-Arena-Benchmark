# Agent vs NPC Baseline Design (Werewolf Roles Only)

## 1) Goal
Define a reproducible **Agent vs NPC baseline** mode where a single evaluated agent plays a seat (or role group) against scripted NPC baselines. This enables stable, comparable metrics across agents and seeds.

## 2) Paper Alignment (high-level)
- **Werewolf Arena (2407.13943)** frames evaluation as a multi-agent arena with bidding-based turn taking to probe strategic communication. We keep the core social-deduction loop but simplify turn-taking for determinism in this baseline mode.
- **WereWolf-Plus (2506.12841)** emphasizes multi-model, multi-dimensional evaluation and supports role extensibility (Seer/Witch/Hunter/Guard/Sheriff) plus richer metrics. We adopt the spirit of richer metrics but limit roles to Werewolf/Seer/Doctor/Villager for v1.

Sources:
- https://arxiv.org/abs/2407.13943
- https://arxiv.org/abs/2506.12841

## 3) Game Mode: Agent vs NPC Baseline
**Purpose:** Compare one evaluated agent against stable scripted NPC baselines.

**Green vs Purple (AgentBeats terms):**
- **Green agent** = this repo's evaluator (game engine + runner + scorer).
- **Purple agent** = the agent under test (A2A endpoint you plug in).
- **Agent vs NPC mode** = one purple seat + 7 scripted NPC seats.

**Setup:**
- 8 players total.
- Roles: 2 Werewolves, 1 Seer, 1 Doctor, 4 Villagers.
- Night/Day cycle, debate -> vote -> night actions.
- Deterministic seeds, fixed player ordering.

**Agent placement:**
- The evaluated agent controls **one seat** per game.
- NPCs control all remaining seats (scripted baseline).

**Run plan:**
- **30 total games per agent**.
- **Role-balanced**: distribute the evaluated agent across roles (e.g., 6 games per role).
- Fixed seed list (published).

## 4) Metrics

### 4.1 Base Metrics (player-oriented)
- **Win rate** (overall and by role). [paper]
- **Games played**. [extension]
- **Survival rate** (overall and by role). [paper]

### 4.2 Role-Specific Metrics (v1 roles only)
- **Seer - Wolf discovery rate** [paper]
  # investigated wolves / # total wolves in game.
- **Doctor - Protection success rate** [paper]
  # protected victim survived / # protection attempts.
- **Werewolf - Survival score** [paper]
  alpha * (survival rounds / total rounds) + (1 - alpha) * I(survived to end).

### 4.3 Additional Player-Oriented Metrics (lightweight)
- **Vote accuracy**: % of votes targeting wolves. [paper]
- **Misvote rate**: % of votes targeting villagers. [paper]
- **Flip rates**: vote changes toward wolves vs. toward villagers. [paper]
- **Bandwagon rate**: % of votes that follow the current majority without new evidence. [extension]
- **Reason grounding**: % of votes/suspicions that cite a specific prior statement. [extension]
- **Rationale diversity**: penalty for repeated low-signal rationales (e.g., overuse of "quiet"). [extension]
- **Debate efficiency**: unique informational statements per turn. [extension]
- **Late-game clutch**: win rate when wolves reach parity-1 (hard scenarios). [extension]
- **Vote influence**: delta in votes toward a target after the player speaks. [extension]
- **Followership**: % of players who align with this player's vote in critical votes. [extension]

### 4.4 Paper-Inspired Team Metrics (planned)
- **IRP (Identification Precision)** = # correct identifications / # total identification attempts. [paper]
- **KRE (Key Role Skill Effectiveness)** = alpha * (# key role survived / # total key role games) + (1 - alpha) * (# key role score / # total key role scores). [paper]
- **VSS (Voting Success Score)** = # successful votes / # total critical votes. [paper]

**Operational definitions (Agent vs NPC mode):**
- **Identification attempt**: any explicit claim in speak/vote content that labels a player as wolf/good (e.g., "X is a wolf", "Y is villager"). Each claim counts once per turn.
- **Correct identification**: the claimed camp matches the true role at game end.
- **Key roles (v1)**: Seer and Doctor.
- **Key role survived**: Seer/Doctor alive at game end.
- **Key role score**: role-specific success score per game:
  - Seer: wolf discovery rate (investigated wolves / total wolves in game).
  - Doctor: protection success rate (protected victim survived / protection attempts).
- **Critical vote**: a day vote where the top two candidates include at least one werewolf (pivotal for camp outcome).
- **Successful vote**:
  - Villager camp: votes that target a werewolf in a critical vote.
  - Werewolf camp: votes that target a villager in a critical vote.

## 5) Reporting
- Per-game JSON scorecard + JSONL logs.
- Aggregate over 30 games, with **role-wise breakdowns** and **overall metrics**.

## 6) Future Extensions (post-v1)
- Add WereWolf-Plus roles (Witch/Hunter/Guard/Sheriff).
- Multi-agent arena mode (multiple evaluated agents per game).
- Bidding-based speaker selection (paper-aligned).
