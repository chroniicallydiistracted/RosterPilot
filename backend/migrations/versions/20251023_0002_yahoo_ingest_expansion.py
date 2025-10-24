"""Expand Yahoo schema for ingestion."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251023_0002"
down_revision = "20251023_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("yahoo_leagues", sa.Column("status", sa.String(length=32), nullable=False, server_default="in_season"))
    op.add_column(
        "yahoo_leagues",
        sa.Column("last_synced", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.add_column(
        "yahoo_teams",
        sa.Column("is_user_team", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "yahoo_rosters",
        sa.Column("is_starter", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "yahoo_rosters",
        sa.Column("projected_points", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "yahoo_rosters", sa.Column("actual_points", sa.Float(), nullable=True)
    )

    # Clear server defaults to avoid unintended future inserts.
    op.alter_column("yahoo_leagues", "status", server_default=None)
    op.alter_column("yahoo_leagues", "last_synced", server_default=None)
    op.alter_column("yahoo_teams", "is_user_team", server_default=None)
    op.alter_column("yahoo_rosters", "is_starter", server_default=None)
    op.alter_column("yahoo_rosters", "projected_points", server_default=None)


def downgrade() -> None:
    op.drop_column("yahoo_rosters", "actual_points")
    op.drop_column("yahoo_rosters", "projected_points")
    op.drop_column("yahoo_rosters", "is_starter")
    op.drop_column("yahoo_teams", "is_user_team")
    op.drop_column("yahoo_leagues", "last_synced")
    op.drop_column("yahoo_leagues", "status")
