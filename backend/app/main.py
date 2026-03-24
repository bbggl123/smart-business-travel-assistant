from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import chat, transport, hotel, dining, approval, invoice, voice, booking, reimbursement
from app.storage.redis_client import get_redis, close_redis
from app.storage.message_queue import get_message_queue, close_message_queue
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    try:
        await get_redis()
        logger.info("Redis connected")
    except Exception as e:
        logger.warning(f"Redis connection failed (non-blocking): {e}")

    try:
        await get_message_queue()
        logger.info("Message queue connected")
    except Exception as e:
        logger.warning(f"Message queue init failed (non-blocking): {e}")

    yield
    logger.info("Application shutting down...")
    await close_redis()
    await close_message_queue()
    logger.info("Resources closed")


app = FastAPI(
    title="智能商旅助手 API",
    description="多Agent协作的智能商旅服务系统后端API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(transport.router)
app.include_router(hotel.router)
app.include_router(dining.router)
app.include_router(approval.router)
app.include_router(invoice.router)
app.include_router(voice.router)
app.include_router(booking.router)
app.include_router(reimbursement.router)


@app.get("/")
async def root():
    return {"message": "智能商旅助手 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
