from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_NAME, APP_VERSION, CORS_ORIGINS, DEBUG
from app.database import engine, Base
from app.routes import (
    health_router,
    generate_router,
    meetings_router,
    action_items_router,
    ai_router,
)

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered Meeting Minutes & Action Item Extractor"
)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(health_router)
app.include_router(generate_router)
app.include_router(meetings_router)
app.include_router(action_items_router)
app.include_router(ai_router)


@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG
    )
