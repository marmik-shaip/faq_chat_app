from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from middlewares.auth import AuthMiddleware
from routes import (
    document_qa, auth
)


def create_app():
    app = FastAPI(debug=True)

    app.include_router(document_qa.router, prefix="/ml/api/prompting")
    app.include_router(auth.router, prefix="")

    @app.get("/health")
    def health():
        return JSONResponse({"message": "Health is OK"})

    @app.get("/ml/api/prompting/health")
    def prompt_health():
        return JSONResponse({"message": "Health is OK"})

    app.add_middleware(AuthMiddleware)

    app.add_middleware(
        SessionMiddleware,
        session_cookie="INSIGHT_SESSION",
        secret_key="Secret",
        https_only=True,
        same_site="none",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:8501",
            "http://localhost:8000",
            "https://copilot.insightsaio.com",
            "https://intcopilot.insightsaio.com",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


fastapi_app = create_app()
