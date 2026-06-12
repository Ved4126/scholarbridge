from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.profile_router import router as profile_router
from backend.app.api.scorer_router import router as scorer_router

app = FastAPI(title="ScholarBridge", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profile_router)
app.include_router(scorer_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "version": "0.1.0"
    }
