from fastapi import FastAPI
from app.api.inbound import router as inbound_router
from app.api.rules import router as rules_router
from app.api.dashboard import router as dashboard_router
from app.api.auth import router as auth_router
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="AI-powered email classification and routing engine",
    version="1.0.0",
)

app.include_router(inbound_router)
app.include_router(rules_router)
app.include_router(dashboard_router)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
