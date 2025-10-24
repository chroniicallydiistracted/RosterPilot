from __future__ import annotations

import time
from datetime import datetime

from fastapi.testclient import TestClient

from app.core.config import get_settings


def test_runtime_config_endpoint_exposes_flags(client: TestClient) -> None:
    response = client.get("/api/meta/config")
    assert response.status_code == 200
    payload = response.json()

    settings = get_settings()
    assert payload["environment"] == settings.environment
    assert payload["api_prefix"] == settings.api_prefix
    assert payload["heartbeat_sec"] == settings.ws_heartbeat_sec
    assert payload["feature_flags"] == {
        "replay": settings.feature_replay,
        "weather": settings.feature_weather,
    }
    assert payload["websocket_paths"]["game_updates"] == "/ws/games/{event_id}"
    # Ensure generated_at is ISO formatted
    datetime.fromisoformat(payload["generated_at"].replace("Z", "+00:00"))


def test_websocket_live_streams_delta_and_heartbeat(client: TestClient) -> None:
    provider = client.app.state.fake_redis_provider
    with client.websocket_connect("/ws/games/401437933?mode=live") as websocket:
        handshake = websocket.receive_json()
        assert handshake["type"] == "handshake"
        assert handshake["feature_flags"]["replay"] is True

        fake_redis = provider.instances[-1]
        fake_redis.pubsub_instance.push_json(
            {
                "event_id": "401437933",
                "sequence": 101,
                "clock": "12:34",
                "quarter": 2,
                "down": 1,
                "distance": 10,
                "yardline_100": 75,
                "type": "PASS",
                "yards": 15,
                "flags": ["COMPLETE"],
                "description": "Sample completion",
            }
        )

        delta = websocket.receive_json()
        assert delta["type"] == "delta"
        assert delta["data"]["sequence"] == 101
        assert delta["data"]["replay"] is False

        heartbeat = websocket.receive_json()
        assert heartbeat["type"] == "heartbeat"

        # Close after heartbeat to avoid lingering tasks
        websocket.close()
        time.sleep(0.05)


def test_websocket_replay_stream(client: TestClient) -> None:
    with client.websocket_connect("/ws/games/401437933?mode=replay&speed=0") as websocket:
        handshake = websocket.receive_json()
        assert handshake["type"] == "handshake"
        assert handshake["mode"] == "replay"

        deltas: list[dict[str, object]] = []
        while True:
            message = websocket.receive_json()
            if message["type"] == "delta":
                deltas.append(message)
            if message["type"] == "replay_complete":
                break

        assert deltas, "expected at least one replay delta"
        assert all(delta["data"]["replay"] is True for delta in deltas)
