"""TEMPORARY diagnostics router.

Added to capture the traceback behind a production-only 500 on
/v1/ai/generate-reply that could not be reproduced locally. Remove this
module, and its include_router call in app.main, once the bug is fixed.
"""

import traceback

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.ai import GenerateReplyRequest
from app.services.ai_engine import AIEngineService

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.post("/generate-reply-trace")
def generate_reply_trace(
    payload: GenerateReplyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Run the reply pipeline and return the traceback instead of a bare 500."""
    try:
        AIEngineService.generate_replies(db, current_user.id, payload)
    except Exception as exc:
        db.rollback()
        return {
            "ok": False,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc().splitlines()[-25:],
        }

    return {"ok": True}
