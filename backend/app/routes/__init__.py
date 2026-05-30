from .health import router as health_router
from .auth import router as auth_router
from .generate import router as generate_router
from .meetings import router as meetings_router
from .action_items import router as action_items_router
from .ai import router as ai_router
from .trial import router as trial_router

__all__ = [
    "health_router",
    "auth_router",
    "generate_router",
    "meetings_router",
    "action_items_router",
    "ai_router",
    "trial_router",
]