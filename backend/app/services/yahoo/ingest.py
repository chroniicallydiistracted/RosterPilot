"""Persist Yahoo Fantasy data into the application database."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.projection import IdMap, WeeklyProjection
from app.models.user import OAuthToken, User
from app.models.yahoo import YahooLeague, YahooPlayer, YahooRoster, YahooTeam
from app.security.crypto import TokenCipher
from app.services.yahoo.models import YahooLeagueData, YahooRosterEntry, YahooUserBundle


@dataclass(slots=True)
class TokenPayload:
    """Container for OAuth tokens returned from Yahoo exchanges."""

    provider: str
    access_token: str
    refresh_token: str
    expires_at: datetime
    scopes: str | None = None


class YahooIngestionService:
    """Synchronize Yahoo domain objects from API payloads."""

    def __init__(self, session: Session, cipher: TokenCipher) -> None:
        self.session = session
        self.cipher = cipher

    def ingest_bundle(self, bundle: YahooUserBundle) -> User:
        """Upsert user, leagues, teams, and rosters derived from Yahoo."""

        user = self._upsert_user(bundle)
        self._upsert_leagues(user.user_id, bundle)
        return user

    def store_tokens(self, user: User, payload: TokenPayload) -> OAuthToken:
        """Persist encrypted OAuth tokens for the user."""

        encrypted_access = self.cipher.encrypt(payload.access_token)
        encrypted_refresh = self.cipher.encrypt(payload.refresh_token)
        provider = payload.provider
        scopes = payload.scopes or ""

        existing = self.session.get(OAuthToken, (user.user_id, provider))
        if existing:
            existing.access_token = encrypted_access
            existing.refresh_token = encrypted_refresh
            existing.expires_at = payload.expires_at
            existing.scopes = scopes
            token = existing
        else:
            token = OAuthToken(
                user_id=user.user_id,
                provider=provider,
                access_token=encrypted_access,
                refresh_token=encrypted_refresh,
                expires_at=payload.expires_at,
                scopes=scopes,
            )
            self.session.add(token)
        return token

    # --- Internal helpers -------------------------------------------------

    def _upsert_user(self, bundle: YahooUserBundle) -> User:
        user = self.session.execute(
            select(User).where(User.yahoo_sub == bundle.yahoo_sub)
        ).scalar_one_or_none()
        if user is None:
            user = User(yahoo_sub=bundle.yahoo_sub)
            self.session.add(user)
            self.session.flush()
        return user

    def _upsert_leagues(self, user_id: uuid.UUID, bundle: YahooUserBundle) -> None:
        for league_data in bundle.leagues:
            league = self.session.get(YahooLeague, league_data.league_key)
            if league is None:
                league = YahooLeague(
                    league_key=league_data.league_key,
                    user_id=user_id,
                    season=league_data.season,
                    name=league_data.name,
                    scoring_json=league_data.scoring_json,
                    status=league_data.status,
                    last_synced=league_data.last_synced,
                )
                self.session.add(league)
            else:
                league.season = league_data.season
                league.name = league_data.name
                league.scoring_json = league_data.scoring_json
                league.status = league_data.status
                league.last_synced = league_data.last_synced

            self._upsert_teams(league.league_key, league_data)

    def _upsert_teams(self, league_key: str, league_data: YahooLeagueData) -> None:
        for team_data in league_data.teams:
            team = self.session.get(YahooTeam, team_data.team_key)
            if team is None:
                team = YahooTeam(
                    team_key=team_data.team_key,
                    league_key=league_key,
                    name=team_data.name,
                    manager=team_data.manager,
                    is_user_team=team_data.is_user_team,
                )
                self.session.add(team)
            else:
                team.name = team_data.name
                team.manager = team_data.manager
                team.is_user_team = team_data.is_user_team

            self._upsert_roster(team, team_data.roster)

    def _upsert_roster(self, team: YahooTeam, roster_entries: list[YahooRosterEntry]) -> None:
        weeks = {entry.week for entry in roster_entries}
        for week in weeks:
            self.session.execute(
                delete(YahooRoster).where(YahooRoster.team_key == team.team_key, YahooRoster.week == week)
            )

        for entry in roster_entries:
            player = self._upsert_player(entry)
            yahoo_player_id = player.yahoo_player_id if player else None
            roster = YahooRoster(
                team_key=team.team_key,
                week=entry.week,
                slot=entry.slot,
                yahoo_player_id=yahoo_player_id,
                is_starter=entry.is_starter,
                projected_points=entry.player.projected_points or 0.0,
                actual_points=entry.player.actual_points,
            )
            self.session.add(roster)

    def _upsert_player(self, entry: YahooRosterEntry) -> YahooPlayer:
        player_data = entry.player
        player = self.session.get(YahooPlayer, player_data.yahoo_player_id)
        if player is None:
            player = YahooPlayer(
                yahoo_player_id=player_data.yahoo_player_id,
                name=player_data.full_name,
                pos=player_data.position,
                team_abbr=player_data.team_abbr,
                status=player_data.status,
                bye_week=player_data.bye_week,
            )
            self.session.add(player)
        else:
            player.name = player_data.full_name
            player.pos = player_data.position
            player.team_abbr = player_data.team_abbr
            player.status = player_data.status
            player.bye_week = player_data.bye_week

        self._upsert_projection(entry)
        return player

    def _upsert_projection(self, entry: YahooRosterEntry) -> None:
        player_data = entry.player
        id_map = self.session.execute(
            select(IdMap).where(IdMap.yahoo_player_id == player_data.yahoo_player_id)
        ).scalar_one_or_none()
        if id_map is None:
            id_map = IdMap(
                yahoo_player_id=player_data.yahoo_player_id,
                full_name=player_data.full_name,
                position=player_data.position,
                team_abbr=player_data.team_abbr,
                confidence=0.5 if player_data.projected_points is not None else 0.0,
            )
            self.session.add(id_map)
            self.session.flush()
        else:
            if not id_map.is_manual:
                id_map.full_name = player_data.full_name
                id_map.position = player_data.position
                if player_data.team_abbr:
                    id_map.team_abbr = player_data.team_abbr
            if player_data.projected_points is not None:
                id_map.confidence = max(id_map.confidence, 0.5)

        if player_data.projected_points is None:
            return

        projection = self.session.execute(
            select(WeeklyProjection).where(
                WeeklyProjection.season == self._season_for_week(entry.week),
                WeeklyProjection.week == entry.week,
                WeeklyProjection.canonical_player_id == id_map.canonical_player_id,
            )
        ).scalar_one_or_none()

        if projection is None:
            projection = WeeklyProjection(
                season=self._season_for_week(entry.week),
                week=entry.week,
                canonical_player_id=id_map.canonical_player_id,
                points=player_data.projected_points,
            )
            self.session.add(projection)
        else:
            projection.points = player_data.projected_points

    @staticmethod
    def _season_for_week(week: int) -> int:
        """Derive the current NFL season based on ISO calendar."""

        now = datetime.now(tz=UTC)
        return now.year if now.month >= 6 else now.year - 1
