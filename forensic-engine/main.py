import os
import sys
from pathlib import Path

# Ensure root of forensic engine is in sys.path
ENGINE_DIR = Path(__file__).resolve().parent
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

# Create FastAPI application instance
app = FastAPI(
    title="ForenXAI Forensic Analysis Engine",
    description=(
        "Deterministic image forensic feature extraction, spatial statistics, "
        "SRM noise residuals, wavelet subband decomposition, JPEG compression analysis, "
        "and error level analysis (ELA)."
    ),
    version="2.1.0",
)

# Enable CORS for frontend and Node.js backend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
