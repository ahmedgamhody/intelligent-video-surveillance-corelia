from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import uvicorn

from config import app_settings
from routes import predictor
from database import db_controller, kafka_consumer, kafka_producer

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_controller.connect()
    await kafka_producer.start()
    await kafka_consumer.start()
    print("✅ App initialized.")
    yield
    await kafka_consumer.stop()
    await kafka_producer.stop()
    await db_controller.disconnect()
    print("🛑 App shutdown clean.")


app = FastAPI(
    title=app_settings.APP_NAME,
    description=app_settings.APP_DESCRIPTION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root():
    return """
    <h2 style="text-align:center">
        Click
        <a href="/docs">API DOCs</a>
        to see the API docs
    </h2>
    """

app.include_router(predictor, prefix=app_settings.ROOT)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=app_settings.DOMAIN,
        port=app_settings.PORT,
        reload=app_settings.DEBUG_MODE,
    )
