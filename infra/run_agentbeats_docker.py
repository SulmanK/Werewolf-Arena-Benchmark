"""
One-shot runner to trigger the green agent via A2A and capture results.
"""

import asyncio
import json
import os
from typing import Any, Dict

import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart, DataPart


async def _wait_for_agent(url: str, httpx_client: httpx.AsyncClient) -> None:
    # Wait for agent card to become reachable (container DNS + server startup).
    for attempt in range(20):
        try:
            resp = await httpx_client.get(f"{url}/.well-known/agent-card.json")
            if resp.status_code == 200:
                return
        except Exception:
            await asyncio.sleep(1 + attempt * 0.2)
    raise RuntimeError(f"Agent card not reachable at {url}")


def _extract_data_from_parts(parts: Any) -> Any:
    if not parts:
        return None
    for part in parts:
        root = getattr(part, "root", None)
        if isinstance(root, DataPart):
            return root.data
    return None


def _extract_data_from_event(event: Any) -> Any:
    if isinstance(event, Message):
        return _extract_data_from_parts(getattr(event, "parts", None))
    if isinstance(event, tuple):
        task, update = event
        data = _extract_data_from_parts(getattr(task, "artifacts", None))
        if data is not None:
            return data
        update_artifact = getattr(update, "artifact", None) if update else None
        return _extract_data_from_parts(getattr(update_artifact, "parts", None))
    return None


async def send_message(payload: Dict[str, Any], url: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=300) as httpx_client:
        print(f"[runner] GREEN_AGENT_URL={url}")
        await _wait_for_agent(url, httpx_client)
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=url)
        agent_card = await resolver.get_agent_card()
        print(f"[runner] agent_card.url={agent_card.url}")
        config = ClientConfig(httpx_client=httpx_client, streaming=False)
        factory = ClientFactory(config)
        client = factory.create(agent_card)

        msg = Message(
            kind="message",
            role=Role.user,
            parts=[Part(TextPart(kind="text", text=json.dumps(payload)))],
            messageId="agentbeats-docker-001",
        )

        last_event = None
        latest_data = None
        async for event in client.send_message(msg):
            last_event = event
            data = _extract_data_from_event(event)
            if data is not None:
                latest_data = data

        results = {"status": "unknown", "data": latest_data}
        if isinstance(last_event, Message):
            # plain message response
            results["status"] = "message"
            results["data"] = "".join(
                p.root.text for p in last_event.parts if isinstance(p.root, TextPart)
            )
            return results

        if isinstance(last_event, tuple):
            task, update = last_event
            results["status"] = getattr(task.status.state, "value", "unknown")
            return results

        return results


async def main() -> None:
    green_url = os.getenv("GREEN_AGENT_URL", "http://green_agent:9009")
    purple_url = os.getenv("PURPLE_AGENT_URL", "http://purple_agent:8100")
    num_tasks = int(os.getenv("NUM_TASKS", "5"))
    shuffle_seed = int(os.getenv("SHUFFLE_SEED", "20206"))

    payload = {
        "participant": purple_url,
        "config": {
            "num_games": num_tasks,
            "shuffle_seed": shuffle_seed,
            "max_rounds": int(os.getenv("MAX_ROUNDS", "10")),
            "max_turns": int(os.getenv("MAX_TURNS", "8")),
        },
    }

    result = await send_message(payload, green_url)

    if result.get("data") is None:
        fallback_path = "/app/results/agentbeats_results.json"
        if os.path.exists(fallback_path):
            with open(fallback_path, "r", encoding="utf-8") as f:
                result["data"] = json.load(f)

    output_path = "/app/results/agentbeats_docker_results.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result.get("data", {}), f, indent=2)

    print(json.dumps(result.get("data", {}), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
