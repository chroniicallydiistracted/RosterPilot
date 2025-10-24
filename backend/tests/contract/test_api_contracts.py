"""Contract tests asserting the scaffolded API surface."""

from __future__ import annotations

from fastapi.testclient import TestClient

HTTP_OK = 200
TARGET_WEEK = 7


def test_health_endpoints(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == HTTP_OK
    assert response.json() == {"status": "ok"}

    response = client.get("/readyz")
    assert response.status_code == HTTP_OK
    assert response.json() == {"status": "ready"}


def test_user_leagues_contract(client: TestClient) -> None:
    response = client.get("/api/me/leagues")
    assert response.status_code == HTTP_OK
    payload = response.json()

    assert payload["leagues"], "Expected at least one league stub"
    league = payload["leagues"][0]
    assert league["source"] == "yahoo"
    assert "my_team" in league
    assert league["my_team"]["name"] == "Phoenix Firebirds"


def test_league_roster_contract(client: TestClient) -> None:
    response = client.get("/api/leagues/nfl.l.12345/roster", params={"week": TARGET_WEEK})
    assert response.status_code == HTTP_OK
    roster = response.json()

    assert roster["league_key"] == "nfl.l.12345"
    assert roster["week"] == TARGET_WEEK
    assert len(roster["starters"]) > 0
    assert roster["optimizer"]["source"] == "optimizer"
    assert any(slot["slot"] == "QB" for slot in roster["starters"])


def test_games_contract(client: TestClient) -> None:
    response = client.get("/api/games/live")
    assert response.status_code == HTTP_OK
    games = response.json()

    assert games["games"], "Expected live game fixture"
    game_map = {game["event_id"]: game for game in games["games"]}
    assert "401437933" in game_map
    game = game_map["401437933"]
    assert game["source"] == "pyespn"
    assert game["home"]["name"] == "Atlanta Falcons"
    assert game["away"]["abbr"] == "ARI"
    assert game["venue"]["city"] == "Atlanta"
    assert "FOX" in game["broadcast"]["tv"]

    event_id = game["event_id"]
    pbp_response = client.get(f"/api/games/{event_id}/pbp")
    assert pbp_response.status_code == HTTP_OK
    pbp = pbp_response.json()
    assert pbp["event_id"] == event_id
    assert pbp["drives"], "Expected drives in play-by-play"
    assert pbp["source"] == "pyespn"
    first_drive = pbp["drives"][0]
    assert first_drive["plays"], "Drive should include plays"
    assert any("SCORING" in play["flags"] for play in first_drive["plays"])


def test_openapi_includes_contract_routes(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == HTTP_OK

    schema = response.json()
    paths = schema["paths"]
    for path in [
        "/healthz",
        "/readyz",
        "/api/me/leagues",
        "/api/leagues/{league_key}/roster",
        "/api/games/live",
        "/api/games/{event_id}/pbp",
    ]:
        assert path in paths, f"Missing {path} from OpenAPI schema"
