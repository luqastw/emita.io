from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.users.router import router as users_router

app = FastAPI(title="InvoiceKit", version="0.1.0")

app.include_router(auth_router)
app.include_router(users_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
