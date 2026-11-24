from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import scans, agent, github, intelligence


app = FastAPI(
    title="CODE SENTINEL AI: Autonomous AI Software Quality Engineer",
    description="Multi-agent orchestration, repository intelligence, isolated microVM sandboxing, and self-healing review platform.",
    version="2.0.0",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(scans.router)
app.include_router(agent.router)
app.include_router(github.router)
app.include_router(intelligence.router)


@app.get("/health", tags=["Health"])
def health_check():
    """Lightweight health check for service monitors and Render wake-up."""
    from app.services.llm_provider import llm_factory
    active_provider = llm_factory.get_provider().__class__.__name__

    return {
        "status": "ok",
        "system": "CODE SENTINEL AI",
        "environment": settings.ENVIRONMENT,
        "active_llm_provider": active_provider,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "e2b_configured": bool(settings.E2B_API_KEY),
        "version": "2.0.0",
    }
