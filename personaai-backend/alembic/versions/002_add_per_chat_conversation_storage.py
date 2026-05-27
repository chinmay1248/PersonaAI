"""Add per-chat conversation storage and tone profiles.

Revision ID: 002
Revises: 001
Create Date: 2025-05-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create chat_message_logs table
    op.create_table(
        'chat_message_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('chat_config_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('message_role', sa.String(20), nullable=False),
        sa.Column('message_text', sa.Text(), nullable=False),
        sa.Column('detected_mood', sa.String(50), nullable=True),
        sa.Column('language_detected', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['chat_config_id'], ['chat_configs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_message_logs_chat_config_id'), 'chat_message_logs', ['chat_config_id'], unique=False)
    op.create_index(op.f('ix_chat_message_logs_user_id'), 'chat_message_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_chat_message_logs_created_at'), 'chat_message_logs', ['created_at'], unique=False)
    op.create_index('idx_chat_config_created', 'chat_message_logs', ['chat_config_id', 'created_at'], unique=False)
    op.create_index('idx_user_created', 'chat_message_logs', ['user_id', 'created_at'], unique=False)

    # Create chat_tone_profiles table
    op.create_table(
        'chat_tone_profiles',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('chat_config_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('avg_message_length', sa.Float(), nullable=True),
        sa.Column('emoji_frequency', sa.Float(), nullable=True),
        sa.Column('common_emojis', sa.JSON(), nullable=False),
        sa.Column('slang_patterns', sa.JSON(), nullable=False),
        sa.Column('punctuation_style', sa.String(50), nullable=True),
        sa.Column('formality_score', sa.Float(), nullable=True),
        sa.Column('caps_usage', sa.String(50), nullable=True),
        sa.Column('language_mix', sa.JSON(), nullable=False),
        sa.Column('tone_shifts', sa.JSON(), nullable=False),
        sa.Column('message_openers', sa.JSON(), nullable=False),
        sa.Column('message_closers', sa.JSON(), nullable=False),
        sa.Column('response_timing', sa.JSON(), nullable=False),
        sa.Column('last_trained_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['chat_config_id'], ['chat_configs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_tone_profiles_chat_config_id'), 'chat_tone_profiles', ['chat_config_id'], unique=False)
    op.create_index(op.f('ix_chat_tone_profiles_user_id'), 'chat_tone_profiles', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_chat_tone_profiles_user_id'), table_name='chat_tone_profiles')
    op.drop_index(op.f('ix_chat_tone_profiles_chat_config_id'), table_name='chat_tone_profiles')
    op.drop_table('chat_tone_profiles')
    op.drop_index('idx_user_created', table_name='chat_message_logs')
    op.drop_index('idx_chat_config_created', table_name='chat_message_logs')
    op.drop_index(op.f('ix_chat_message_logs_created_at'), table_name='chat_message_logs')
    op.drop_index(op.f('ix_chat_message_logs_user_id'), table_name='chat_message_logs')
    op.drop_index(op.f('ix_chat_message_logs_chat_config_id'), table_name='chat_message_logs')
    op.drop_table('chat_message_logs')
