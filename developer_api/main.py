import asyncio
from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool
from fastapi.middleware.cors import CORSMiddleware

from db import get_async_pool
from routers import v2_api

pool: AsyncConnectionPool[Any] | None = None  # Will be initialized during lifespan

async def check_connections() -> None:
    while True:
        await asyncio.sleep(600)  # wait 10 minutes
        print("Checking Connections")
        if pool:
            await pool.check()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = get_async_pool()
    await pool.open()
    task = asyncio.create_task(check_connections())
    yield None
    task.cancel()
    await pool.check()


app = FastAPI(lifespan=lifespan)
app.include_router(v2_api.router, prefix="/api")  # include the methods declared in our api

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Allow the API to be used by the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # You can also use ["*"] to allow all, not recommended for prod
    allow_credentials=True,
    allow_methods=["*"],  # Or ["GET", "POST", ...]
    allow_headers=["*"],  # Or restrict to specific headers
)

for route in app.routes:
    print(f"Path: {route.path} Methods: {route.methods}")


@app.get("/")
async def root():
    return {"message": "Hello World"}
