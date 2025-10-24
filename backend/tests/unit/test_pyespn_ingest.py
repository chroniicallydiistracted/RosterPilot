"""Unit coverage for the PyESPN ingestion service."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Base
from app.models.espn import Drive, Event, EventState, Play, Team, Venue
from app.services.pyespn.ingest import PyESPNIngestionService
from ..fixtures.pyespn import load_play_by_play_fixture, load_scoreboard_fixture


def test_ingests_scoreboard_and_play_by_play(tmp_path: Path) -> None:
    database_path = tmp_path / "pyespn.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        service = PyESPNIngestionService(session)
        scoreboard = load_scoreboard_fixture()
        service.ingest_scoreboard(scoreboard)
        service.ingest_play_by_play("401437933", load_play_by_play_fixture("401437933"))
        session.commit()

        event = session.execute(
            select(Event).where(Event.event_id == "401437933")
        ).scalar_one()
        state = session.execute(
            select(EventState).where(EventState.event_id == "401437933")
        ).scalar_one()

        assert event.home_id in {team.espn_team_id for team in session.execute(select(Team)).scalars()}
        assert state.home_score == 20
        assert state.away_score == 19

        venue = session.get(Venue, event.venue_id)
        assert venue is not None
        assert venue.city == "Atlanta"
        assert venue.state == "GA"

        drives = session.execute(select(Drive).where(Drive.event_id == event.event_id)).scalars().all()
        plays = session.execute(select(Play).where(Play.event_id == event.event_id)).scalars().all()

        assert len(drives) > 0
        assert len(plays) > 0
        assert any(play.raw_json.get("scoringPlay") for play in plays)
