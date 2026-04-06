"""Initial schema migration.

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('privacy_mode', sa.Boolean(), nullable=False),
        sa.Column('auto_training_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create tone_profiles table
    op.create_table(
        'tone_profiles',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('formality_score', sa.Float(), nullable=True),
        sa.Column('avg_message_length', sa.Float(), nullable=True),
        sa.Column('emoji_frequency', sa.Float(), nullable=True),
        sa.Column('common_emojis', sa.JSON(), nullable=False),
        sa.Column('slang_patterns', sa.JSON(), nullable=False),
        sa.Column('punctuation_style', sa.String(50), nullable=True),
        sa.Column('caps_usage', sa.String(50), nullable=True),
        sa.Column('language_mix', sa.JSON(), nullable=False),
        sa.Column('vector_id', sa.String(255), nullable=True),
        sa.Column('accuracy_score', sa.Float(), nullable=False),
        sa.Column('last_trained_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tone_profiles_user_id'), 'tone_profiles', ['user_id'], unique=False)

    # Create chat_configs table
    op.create_table(
        'chat_configs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('chat_label', sa.String(100), nullable=False),
        sa.Column('chat_type', sa.String(50), nullable=True),
        sa.Column('personality_mode', sa.String(50), nullable=True),
        sa.Column('auto_reply_mode', sa.String(20), nullable=False),
        sa.Column('ai_enabled', sa.Boolean(), nullable=False),
        sa.Column('is_private', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chat_configs_user_id'), 'chat_configs', ['user_id'], unique=False)

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('chat_config_id', sa.String(36), nullable=False),
        sa.Column('incoming_msg', sa.Text(), nullable=False),
        sa.Column('detected_mood', sa.String(50), nullable=True),
        sa.Column('context_window', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['chat_config_id'], ['chat_configs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_chat_config_id'), 'conversations', ['chat_config_id'], unique=False)
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)

    # Create training_samples table
    op.create_table(
        'training_samples',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('sample_text', sa.Text(), nullable=False),
        sa.Column('source', sa.String(50), nullable=True),
        sa.Column('used_in_training', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_training_samples_user_id'), 'training_samples', ['user_id'], unique=False)

    # Create reply_suggestions table
    op.create_table(
        'reply_suggestions',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('conversation_id', sa.String(36), nullable=False),
        sa.Column('reply_text', sa.Text(), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('was_used', sa.Boolean(), nullable=False),
        sa.Column('feedback', sa.String(10), nullable=True),
        sa.Column('feedback_reason', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reply_suggestions_conversation_id'), 'reply_suggestions', ['conversation_id'], unique=False)

    # Create feedback_logs table
    op.create_table(
        'feedback_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('reply_suggestion_id', sa.String(36), nullable=False),
        sa.Column('rating', sa.String(10), nullable=False),
        sa.Column('reason', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['reply_suggestion_id'], ['reply_suggestions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feedback_logs_user_id'), 'feedback_logs', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_feedback_logs_user_id'), table_name='feedback_logs')
    op.drop_table('feedback_logs')
    op.drop_index(op.f('ix_reply_suggestions_conversation_id'), table_name='reply_suggestions')
    op.drop_table('reply_suggestions')
    op.drop_index(op.f('ix_training_samples_user_id'), table_name='training_samples')
    op.drop_table('training_samples')
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_chat_config_id'), table_name='conversations')
    op.drop_table('conversations')
    op.drop_index(op.f('ix_chat_configs_user_id'), table_name='chat_configs')
    op.drop_table('chat_configs')
    op.drop_index(op.f('ix_tone_profiles_user_id'), table_name='tone_profiles')
    op.drop_table('tone_profiles')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
