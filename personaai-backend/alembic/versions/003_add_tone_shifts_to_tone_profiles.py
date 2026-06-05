"""Add tone_shifts to global tone profiles.

Revision ID: 003
Revises: 002
Create Date: 2026-06-04 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tone_profiles",
        sa.Column(
            "tone_shifts",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
    )
    if op.get_bind().dialect.name != "sqlite":
        op.alter_column("tone_profiles", "tone_shifts", server_default=None)


def downgrade() -> None:
    op.drop_column("tone_profiles", "tone_shifts")
