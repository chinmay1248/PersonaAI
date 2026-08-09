"""Add conversation_threads table and thread_id link on chat_message_logs.

The ConversationThread model and the ChatMessageLog.thread_id column were
added to the ORM (Phase 2/3 of per-chat storage) but no migration was ever
written for them, so `alembic upgrade head` left the database without the
`conversation_threads` table and without `chat_message_logs.thread_id`.
That made every `/v1/ai/generate-reply` call fail with
`OperationalError: no such column: chat_message_logs.thread_id`.

Revision ID: 004
Revises: 003
Create Date: 2026-08-09 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversation_threads",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("chat_config_id", sa.String(36), nullable=False),
        sa.Column("topic_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["chat_config_id"], ["chat_configs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_thread_chat_config", "conversation_threads", ["chat_config_id"], unique=False
    )

    with op.batch_alter_table("chat_message_logs") as batch_op:
        batch_op.add_column(sa.Column("thread_id", sa.String(36), nullable=True))
        batch_op.create_foreign_key(
            "fk_chat_message_logs_thread_id",
            "conversation_threads",
            ["thread_id"],
            ["id"],
            ondelete="SET NULL",
        )
    op.create_index(
        op.f("ix_chat_message_logs_thread_id"), "chat_message_logs", ["thread_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_chat_message_logs_thread_id"), table_name="chat_message_logs")
    with op.batch_alter_table("chat_message_logs") as batch_op:
        batch_op.drop_constraint("fk_chat_message_logs_thread_id", type_="foreignkey")
        batch_op.drop_column("thread_id")

    op.drop_index("idx_thread_chat_config", table_name="conversation_threads")
    op.drop_table("conversation_threads")
