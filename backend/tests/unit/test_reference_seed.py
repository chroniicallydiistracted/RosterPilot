from __future__ import annotations

from cryptography.fernet import Fernet
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Base
from app.models.espn import Team, Venue
from app.models.projection import IdMap
from app.jobs.reference import seed_canonical_players, seed_reference_data
from app.security.crypto import TokenCipher
from app.services.yahoo.fixtures import load_test_user_bundle
from app.services.yahoo.ingest import YahooIngestionService


def test_reference_seed_populates_teams_and_venues() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        result = seed_reference_data(session)
        session.commit()

        assert result["teams"] >= 32
        # Two franchises share MetLife Stadium, resulting in fewer unique venues.
        assert result["venues"] >= 30

        teams = session.execute(select(Team)).scalars().all()
        venues = session.execute(select(Venue)).scalars().all()

        assert len(teams) >= 32
        assert len(venues) >= 30
        assert any(team.abbr == "ATL" for team in teams)
        assert any(venue.city == "Atlanta" for venue in venues)


def test_canonical_seed_creates_manual_mappings() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed_reference_data(session)
        created = seed_canonical_players(session)
        session.commit()

        assert created > 0

        mapping = session.execute(
            select(IdMap).where(IdMap.yahoo_player_id == "257654")
        ).scalar_one()

        assert mapping.espn_player_id == "3915516"
        assert mapping.full_name == "Jalen Hurts"
        assert mapping.is_manual is True
        assert mapping.confidence >= 1.0


def test_yahoo_ingest_preserves_manual_mapping() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        seed_reference_data(session)
        seed_canonical_players(session)

        cipher = TokenCipher(fernet=Fernet(Fernet.generate_key()))
        service = YahooIngestionService(session=session, cipher=cipher)
        service.ingest_bundle(load_test_user_bundle())
        session.commit()

        mapping = session.execute(
            select(IdMap).where(IdMap.yahoo_player_id == "257654")
        ).scalar_one()

        assert mapping.espn_player_id == "3915516"
        assert mapping.is_manual is True
        assert mapping.confidence >= 1.0
