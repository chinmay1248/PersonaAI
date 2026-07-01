from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models import ChatMessageLog, ChatConfig
import json


class ChatHistoryService:
    """Service for managing per-chat conversation history."""

    @staticmethod
    def log_message(
        db: Session,
        chat_config_id: str,
        user_id: str,
        message_role: str,
        message_text: str,
        detected_mood: Optional[str] = None,
        language_detected: Optional[str] = None,
    ) -> ChatMessageLog:
        """Log a message to chat history.

        Args:
            db: Database session
            chat_config_id: ID of the chat configuration
            user_id: ID of the user
            message_role: Role of message sender ('user' or 'contact')
            message_text: The message text content
            detected_mood: Optional mood detection result
            language_detected: Optional detected language

        Returns:
            Created ChatMessageLog record
        """
        from app.models.conversation_thread import ConversationThread

        active_thread = db.query(ConversationThread).filter(
            ConversationThread.chat_config_id == chat_config_id,
            ConversationThread.is_active == True
        ).order_by(ConversationThread.created_at.desc()).first()

        if not active_thread:
            active_thread = ConversationThread(
                chat_config_id=chat_config_id,
                topic_name=None,
            )
            db.add(active_thread)
            db.commit()
            db.refresh(active_thread)
        else:
            last_msg = db.query(ChatMessageLog).filter(
                ChatMessageLog.thread_id == active_thread.id
            ).order_by(ChatMessageLog.created_at.desc()).first()
            
            # Simple heuristic: if more than 4 hours since last message, start a new thread
            if last_msg and last_msg.created_at.tzinfo is None:
                last_msg_time = last_msg.created_at.replace(tzinfo=timezone.utc)
            elif last_msg:
                last_msg_time = last_msg.created_at
            else:
                last_msg_time = datetime.now(timezone.utc)

            if last_msg and (datetime.now(timezone.utc) - last_msg_time) > timedelta(hours=4):
                active_thread.is_active = False
                active_thread = ConversationThread(
                    chat_config_id=chat_config_id,
                    topic_name=None,
                )
                db.add(active_thread)
                db.commit()
                db.refresh(active_thread)

        message_log = ChatMessageLog(
            chat_config_id=chat_config_id,
            user_id=user_id,
            message_role=message_role,
            message_text=message_text,
            detected_mood=detected_mood,
            language_detected=language_detected,
            thread_id=active_thread.id,
        )
        db.add(message_log)
        db.commit()
        db.refresh(message_log)
        return message_log

    @staticmethod
    def get_chat_history(
        db: Session,
        chat_config_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ChatMessageLog]:
        """Retrieve chat history for a specific chat.

        Args:
            db: Database session
            chat_config_id: ID of the chat configuration
            limit: Maximum number of messages to retrieve
            offset: Offset for pagination

        Returns:
            List of ChatMessageLog records, newest first
        """
        return db.query(ChatMessageLog).filter(
            ChatMessageLog.chat_config_id == chat_config_id
        ).order_by(
            ChatMessageLog.created_at.desc()
        ).offset(offset).limit(limit).all()

    @staticmethod
    def get_recent_messages(
        db: Session,
        chat_config_id: str,
        minutes: int = 1440,
    ) -> list[ChatMessageLog]:
        """Get messages from the last N minutes.

        Args:
            db: Database session
            chat_config_id: ID of the chat configuration
            minutes: Number of minutes to look back (default 24 hours)

        Returns:
            List of recent messages
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return db.query(ChatMessageLog).filter(
            ChatMessageLog.chat_config_id == chat_config_id,
            ChatMessageLog.created_at >= cutoff,
        ).order_by(ChatMessageLog.created_at.asc()).all()

    @staticmethod
    def get_user_messages_only(
        db: Session,
        chat_config_id: str,
        limit: int = 50,
    ) -> list[ChatMessageLog]:
        """Get only the user's sent messages from a chat.

        Args:
            db: Database session
            chat_config_id: ID of the chat configuration
            limit: Maximum number of messages

        Returns:
            List of user messages, newest first
        """
        return db.query(ChatMessageLog).filter(
            ChatMessageLog.chat_config_id == chat_config_id,
            ChatMessageLog.message_role == "user",
        ).order_by(ChatMessageLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_contact_messages_only(
        db: Session,
        chat_config_id: str,
        limit: int = 50,
    ) -> list[ChatMessageLog]:
        """Get only incoming messages from a chat.

        Args:
            db: Database session
            chat_config_id: ID of the chat configuration
            limit: Maximum number of messages

        Returns:
            List of contact messages, newest first
        """
        return db.query(ChatMessageLog).filter(
            ChatMessageLog.chat_config_id == chat_config_id,
            ChatMessageLog.message_role == "contact",
        ).order_by(ChatMessageLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def search_messages_by_mood(
        db: Session,
        chat_config_id: str,
        mood: str,
        limit: int = 50,
    ) -> list[ChatMessageLog]:
        """Find messages with a specific detected mood.

        Args:
            db: Database session
            chat_config_id: ID of the chat configuration
            mood: Mood to search for
            limit: Maximum number of messages

        Returns:
            List of messages with specified mood
        """
        return db.query(ChatMessageLog).filter(
            ChatMessageLog.chat_config_id == chat_config_id,
            ChatMessageLog.detected_mood == mood,
        ).order_by(ChatMessageLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_message_count(
        db: Session,
        chat_config_id: str,
    ) -> int:
        """Get total message count for a chat.

        Args:
            db: Database session
            chat_config_id: ID of the chat configuration

        Returns:
            Total number of messages in chat
        """
        return db.query(ChatMessageLog).filter(
            ChatMessageLog.chat_config_id == chat_config_id
        ).count()

    @staticmethod
    def export_chat_history(
        db: Session,
        chat_config_id: str,
        include_encrypted: bool = False,
    ) -> dict:
        """Export full chat history as a dictionary.

        Args:
            db: Database session
            chat_config_id: ID of the chat configuration
            include_encrypted: Whether to include encrypted text (for exports)

        Returns:
            Dictionary with chat metadata and messages
        """
        chat_config = db.query(ChatConfig).filter(
            ChatConfig.id == chat_config_id
        ).first()

        if not chat_config:
            raise ValueError(f"Chat config {chat_config_id} not found")

        messages = ChatHistoryService.get_chat_history(
            db, chat_config_id, limit=10000
        )

        # Sort chronologically for export
        messages = sorted(messages, key=lambda m: m.created_at)

        return {
            "chat_label": chat_config.chat_label,
            "chat_type": chat_config.chat_type,
            "total_messages": len(messages),
            "created_at": chat_config.created_at.isoformat(),
            "messages": [
                {
                    "timestamp": msg.created_at.isoformat(),
                    "role": msg.message_role,
                    "text": msg.message_text if include_encrypted else "[encrypted]",
                    "mood": msg.detected_mood,
                    "language": msg.language_detected,
                }
                for msg in messages
            ]
        }

    @staticmethod
    def format_for_prompt(messages: list[ChatMessageLog]) -> str:
        """Format chat history for inclusion in LLM prompt.

        Args:
            messages: List of ChatMessageLog records

        Returns:
            Formatted string for prompt inclusion
        """
        formatted = []
        for msg in reversed(messages):  # Chronological order
            role_label = "You" if msg.message_role == "user" else "Them"
            formatted.append(f"{role_label}: {msg.message_text}")
        return "\n".join(formatted)

    @staticmethod
    def delete_old_messages(
        db: Session,
        chat_config_id: str,
        days_to_keep: int = 90,
    ) -> int:
        """Delete messages older than specified days (optional archival).

        Args:
            db: Database session
            chat_config_id: ID of the chat configuration
            days_to_keep: Number of days of history to keep

        Returns:
            Number of messages deleted
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_to_keep)
        deleted = db.query(ChatMessageLog).filter(
            ChatMessageLog.chat_config_id == chat_config_id,
            ChatMessageLog.created_at < cutoff,
        ).delete()
        db.commit()
        return deleted
