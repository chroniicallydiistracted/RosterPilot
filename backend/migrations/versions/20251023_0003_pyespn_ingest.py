"""PyESPN ingestion schema additions."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251023_0003"
down_revision = "20251023_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "venues",
        sa.Column("state", sa.String(length=64), nullable=False, server_default=""),
    )

    op.add_column("drives", sa.Column("team_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_drives_team_id",
        "drives",
        "teams",
        ["team_id"],
        ["espn_team_id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "event_states",
        sa.Column("event_id", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("status_detail", sa.String(length=128), nullable=True),
        sa.Column("quarter", sa.Integer(), nullable=True),
        sa.Column("clock", sa.String(length=16), nullable=True),
        sa.Column("possession", sa.String(length=8), nullable=True),
        sa.Column("home_score", sa.Integer(), nullable=False),
        sa.Column("away_score", sa.Integer(), nullable=False),
        sa.Column("home_timeouts", sa.Integer(), nullable=True),
        sa.Column("away_timeouts", sa.Integer(), nullable=True),
        sa.Column("broadcast_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("last_update", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["event_id"], ["events.event_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("event_id", name="pk_event_states"),
    )

    op.alter_column("venues", "state", server_default=None)
    op.alter_column("event_states", "broadcast_json", server_default=None)
    op.alter_column("event_states", "last_update", server_default=None)


def downgrade() -> None:
    op.drop_table("event_states")
    op.drop_constraint("fk_drives_team_id", "drives", type_="foreignkey")
    op.drop_column("drives", "team_id")
    op.drop_column("venues", "state")
