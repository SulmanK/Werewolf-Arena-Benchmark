"""A2A bridge/server (minimal functional HTTP JSON)."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from benchmark import protocol
from agents.scripted import ScriptedAgent
import random


class A2AHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            obs = json.loads(raw)
            protocol.validate_observation(obs)
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(str(e).encode("utf-8"))
            return

        # Generate a deterministic scripted response as a fallback baseline
        role = obs.get("role", "Villager")
        name = obs.get("name", "Agent")
        seed = obs.get("seed", 0)
        agent = ScriptedAgent(name=name, role=role, seed=seed)
        if obs.get("phase") == "day":
            content = agent.speak(obs.get("public_debate", []))
            action = {"type": "speak", "content": content}
        elif obs.get("phase") == "day_vote":
            players = obs.get("remaining_players", [])
            target = agent.vote(players)
            action = {"type": "vote", "target": target}
        else:
            players = obs.get("remaining_players", [])
            wolves = obs.get("wolves", [])
            target = agent.night_power(players, wolves)
            action = {"type": "night_power", "target": target}

        body = json.dumps(action).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return  # silence default logging


def start_server(host: str = "0.0.0.0", port: int = 8080):
    server = HTTPServer((host, port), A2AHandler)
    print(f"Starting A2A server on {host}:{port}")
    server.serve_forever()
