from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.utils.jwt_handler import create_access_token, create_refresh_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


class AuthService:
    @staticmethod
    def register_user(db: Session, payload: RegisterRequest) -> AuthResponse:
        existing_user = db.query(User).filter(User.email == payload.email).one_or_none()
        if existing_user:
            raise ValueError("A user with this email already exists")

        user = User(
            email=payload.email,
            password_hash=pwd_context.hash(payload.password),
            display_name=payload.display_name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return AuthResponse(
            user_id=user.id,
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
            expires_in=settings.access_token_expire_minutes * 60,
        )

    @staticmethod
    def login_user(db: Session, payload: LoginRequest) -> AuthResponse:
        user = db.query(User).filter(User.email == payload.email).one_or_none()
        if not user or not pwd_context.verify(payload.password, user.password_hash):
            raise ValueError("Invalid credentials")

        return AuthResponse(
            user_id=user.id,
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
            expires_in=settings.access_token_expire_minutes * 60,
        )
