"""Initial schema for RosterPilot backend."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20251023_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("yahoo_sub", sa.String(length=128), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "oauth_tokens",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scopes", sa.String(length=256), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "provider", name="pk_oauth_tokens"),
    )

    op.create_table(
        "yahoo_leagues",
        sa.Column("league_key", sa.String(length=64), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("scoring_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE"),
    )

    op.create_table(
        "yahoo_teams",
        sa.Column("team_key", sa.String(length=64), primary_key=True),
        sa.Column("league_key", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("manager", sa.String(length=128), nullable=False),
        sa.ForeignKeyConstraint(["league_key"], ["yahoo_leagues.league_key"], ondelete="CASCADE"),
    )

    op.create_table(
        "yahoo_players",
        sa.Column("yahoo_player_id", sa.String(length=64), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("pos", sa.String(length=16), nullable=False),
        sa.Column("team_abbr", sa.String(length=8), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=True),
        sa.Column("bye_week", sa.Integer(), nullable=True),
    )

    op.create_table(
        "yahoo_rosters",
        sa.Column("team_key", sa.String(length=64), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("slot", sa.String(length=32), nullable=False),
        sa.Column("yahoo_player_id", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["team_key"], ["yahoo_teams.team_key"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["yahoo_player_id"], ["yahoo_players.yahoo_player_id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("team_key", "week", "slot", name="pk_yahoo_rosters"),
    )

    op.create_table(
        "teams",
        sa.Column("espn_team_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("abbr", sa.String(length=8), nullable=False),
        sa.Column("colors_json", sa.JSON(), nullable=False),
        sa.Column("logos_json", sa.JSON(), nullable=False),
    )

    op.create_table(
        "venues",
        sa.Column("venue_id", sa.String(length=32), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("city", sa.String(length=128), nullable=False),
        sa.Column("roof_type", sa.String(length=32), nullable=True),
        sa.Column("surface", sa.String(length=32), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
    )

    op.create_table(
        "events",
        sa.Column("event_id", sa.String(length=32), primary_key=True),
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("start_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("home_id", sa.Integer(), nullable=False),
        sa.Column("away_id", sa.Integer(), nullable=False),
        sa.Column("venue_id", sa.String(length=32), nullable=True),
        sa.ForeignKeyConstraint(["home_id"], ["teams.espn_team_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["away_id"], ["teams.espn_team_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["venue_id"], ["venues.venue_id"], ondelete="SET NULL"),
    )

    op.create_table(
        "drives",
        sa.Column("event_id", sa.String(length=32), nullable=False),
        sa.Column("drive_id", sa.String(length=16), nullable=False),
        sa.Column("start_yardline_100", sa.Integer(), nullable=True),
        sa.Column("end_yardline_100", sa.Integer(), nullable=True),
        sa.Column("result", sa.String(length=64), nullable=True),
        sa.Column("start_clock", sa.String(length=16), nullable=True),
        sa.Column("end_clock", sa.String(length=16), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.event_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("event_id", "drive_id", name="pk_drives"),
    )

    op.create_table(
        "plays",
        sa.Column("event_id", sa.String(length=32), nullable=False),
        sa.Column("play_id", sa.String(length=32), nullable=False),
        sa.Column("drive_id", sa.String(length=16), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("clock", sa.String(length=16), nullable=True),
        sa.Column("quarter", sa.Integer(), nullable=True),
        sa.Column("down", sa.Integer(), nullable=True),
        sa.Column("distance", sa.Integer(), nullable=True),
        sa.Column("yardline_100", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(length=32), nullable=True),
        sa.Column("yards", sa.Integer(), nullable=True),
        sa.Column("raw_json", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["events.event_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("event_id", "play_id", name="pk_plays"),
    )

    op.create_table(
        "id_map",
        sa.Column("canonical_player_id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("yahoo_player_id", sa.String(length=64), nullable=True),
        sa.Column("espn_player_id", sa.String(length=64), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.UniqueConstraint("yahoo_player_id", name="uq_id_map_yahoo"),
    )

    op.create_table(
        "projections_weekly",
        sa.Column("season", sa.Integer(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("canonical_player_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("points", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["canonical_player_id"], ["id_map.canonical_player_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("season", "week", "canonical_player_id", name="pk_projections_weekly"),
    )


def downgrade() -> None:
    op.drop_table("projections_weekly")
    op.drop_table("id_map")
    op.drop_table("plays")
    op.drop_table("drives")
    op.drop_table("events")
    op.drop_table("venues")
    op.drop_table("teams")
    op.drop_table("yahoo_rosters")
    op.drop_table("yahoo_players")
    op.drop_table("yahoo_teams")
    op.drop_table("yahoo_leagues")
    op.drop_table("oauth_tokens")
    op.drop_table("users")
