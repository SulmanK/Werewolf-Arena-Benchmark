"""A2A proxy to Gemini (gemini-2.5-flash-lite by default).

Usage:
  GEMINI_API_KEY=... python scripts/a2a_gemini_proxy.py --host 0.0.0.0 --port 8080 \
      --model gemini-2.5-flash-lite --temperature 0.2 --max-output-tokens 256

Notes:
- Expects A2A-style observations and returns action JSON: speak/vote/night_power.
- Default model: gemini-2.5-flash-lite; override via --model or env MODEL_ID.
- Not used in CI; offline scripted remains default in runner.
"""

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict

import google.generativeai as genai

DEFAULT_MODEL = os.environ.get("MODEL_ID", "gemini-2.5-flash-lite")
DEFAULT_TEMPERATURE = float(os.environ.get("MODEL_TEMPERATURE", "0.2"))
DEFAULT_MAX_OUTPUT_TOKENS = int(os.environ.get("MODEL_MAX_TOKENS", "256"))


def format_prompt(obs: Dict) -> str:
    role = obs.get("role")
    phase = obs.get("phase")
    public = obs.get("public_debate", [])
    remaining = obs.get("remaining_players", [])
    graveyard = obs.get("graveyard", [])
    private = obs.get("private", {})

    if phase == "day":
        if public:
            action_hint = (
                'Valid action: {"type": "speak", "content": "<one line naming a suspect from remaining_players and why (cite a specific speaker/line)>"} '
                "(no generic intros; do NOT repeat the same line; avoid generic 'quiet' accusations unless you mention who was quiet and why it matters)."
            )
        else:
            action_hint = (
                'Valid action: {"type": "speak", "content": "<one line asking for info/observing; no accusations yet>"} '
                "(no generic intros; do not accuse before anyone speaks)."
            )
    elif phase == "day_vote":
        action_hint = (
            f'Valid action: {{"type": "vote", "target": "<one of: {remaining}>"}}. '
            "Pick the player you most suspect; optional short reason in content. Do NOT return speak."
        )
    else:
        action_hint = (
            f'Valid action: {{"type": "night_power", "target": "<one of: {remaining}>"}}. '
            "Do NOT return speak."
        )

    # Role-specific nudge: wolves avoid voting/attacking wolves
    role_hint = ""
    if role == "Werewolf" and phase in ("day", "day_vote", "night"):
        role_hint = "As a Werewolf, avoid targeting or accusing other Werewolves; prefer non-wolf targets."

    lines = [
        f"You are {obs.get('name')} playing role {role}.",
        f"Round: {obs.get('round')} Phase: {phase}.",
        f"Remaining players: {remaining}",
        f"Graveyard: {graveyard}",
        f"Debate so far: {public}",
        f"Private info: {private}",
        action_hint,
        role_hint,
        "Return ONLY JSON, no text before/after. Schema: {\"type\": \"speak|vote|night_power\", \"content\": str?, \"target\": str?}.",
    ]
    return "\n".join(lines)


def call_model(model: str, temperature: float, max_tokens: int, obs: Dict) -> Dict:
    prompt = format_prompt(obs)
    response = genai.GenerativeModel(model).generate_content(
        prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        },
    )
    # Parse JSON action from text
    text = response.text or "{}"
    try:
        action = json.loads(text)
    except json.JSONDecodeError:
        # fallback: try to extract JSON object
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            action = json.loads(text[start : end + 1])
        else:
            action = {"type": "speak", "content": text.strip()[:200]}
    return action


def validate_action(obs: Dict, action: Dict) -> str:
    """Return empty string if valid, else error message."""
    phase = obs.get("phase")
    remaining = obs.get("remaining_players", [])
    t = action.get("type")
    if t not in ("speak", "vote", "night_power"):
        return "invalid type"
    if phase == "day":
        if t != "speak" or not action.get("content"):
            return "day requires speak with content"
    elif phase == "day_vote":
        if t != "vote" or not action.get("target") or action.get("target") not in remaining:
            return "day_vote requires vote with target in remaining_players"
    else:
        if t != "night_power" or not action.get("target") or action.get("target") not in remaining:
            return "night requires night_power with target in remaining_players"
    return ""


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            obs = json.loads(raw)
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"invalid json")
            return
        try:
            print(f"[REQ] round={obs.get('round')} phase={obs.get('phase')} role={obs.get('role')} name={obs.get('name')}")
            action = call_model(self.server.model, self.server.temperature, self.server.max_tokens, obs)
            print(f"[RES] action={action}")
            err = validate_action(obs, action)
            if err:
                raise ValueError(err)
        except Exception as e:
            print(f"[ERR] {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode("utf-8"))
            return
        body = json.dumps(action).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def main():
    parser = argparse.ArgumentParser(description="A2A proxy to Gemini")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--max-output-tokens", type=int, default=DEFAULT_MAX_OUTPUT_TOKENS)
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is required")
    genai.configure(api_key=api_key)

    server = HTTPServer((args.host, args.port), Handler)
    server.model = args.model
    server.temperature = args.temperature
    server.max_tokens = args.max_output_tokens
    print(f"Gemini proxy listening on {args.host}:{args.port} model={args.model} temp={args.temperature} key_present={'yes' if api_key else 'no'}")
    server.serve_forever()


if __name__ == "__main__":
    main()
