"""Canonical player mapping metadata and reference seeds."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251023_0004"
down_revision = "20251023_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "espn_players",
        sa.Column("espn_player_id", sa.String(length=16), nullable=False),
        sa.Column("full_name", sa.String(length=128), nullable=False),
        sa.Column("position", sa.String(length=16), nullable=True),
        sa.Column("team_abbr", sa.String(length=8), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("espn_player_id", name="pk_espn_players"),
    )

    op.add_column("id_map", sa.Column("full_name", sa.String(length=128), nullable=True))
    op.add_column("id_map", sa.Column("position", sa.String(length=16), nullable=True))
    op.add_column("id_map", sa.Column("team_abbr", sa.String(length=8), nullable=True))
    op.add_column(
        "id_map",
        sa.Column("is_manual", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column(
        "id_map",
        "confidence",
        existing_type=sa.Float(),
        nullable=False,
        server_default="0",
    )
    op.create_unique_constraint("uq_id_map_espn", "id_map", ["espn_player_id"])
    op.create_index("ix_id_map_team_pos", "id_map", ["team_abbr", "position"])

    op.alter_column("id_map", "is_manual", server_default=None)
    op.alter_column("id_map", "confidence", server_default=None)


def downgrade() -> None:
    op.alter_column(
        "id_map",
        "confidence",
        existing_type=sa.Float(),
        nullable=True,
        server_default=None,
    )
    op.drop_index("ix_id_map_team_pos", table_name="id_map")
    op.drop_constraint("uq_id_map_espn", "id_map", type_="unique")
    op.drop_column("id_map", "is_manual")
    op.drop_column("id_map", "team_abbr")
    op.drop_column("id_map", "position")
    op.drop_column("id_map", "full_name")
    op.drop_table("espn_players")
