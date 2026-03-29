"""
yooti-dashboard — Agent service entry point
Exposes LangGraph agents as a FastAPI endpoint.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

log = structlog.get_logger()

app = FastAPI(
    title="yooti-dashboard Agent Service",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "agents"}


# Register agent routers here as agent stories are completed
# from template_agent.api import router as template_router
# app.include_router(template_router, prefix="/agents/template")
