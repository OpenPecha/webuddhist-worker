import logging
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from ..config import get

mongodb_client = None
mongodb = None


@asynccontextmanager
async def lifespan(api: FastAPI):
    global mongodb_client, mongodb
    # Initialize the MongoDB client and database
    mongodb_client = AsyncIOMotorClient(get("MONGO_CONNECTION_STRING"))
    mongodb = mongodb_client[get("MONGO_DATABASE_NAME")]
    api.mongodb = mongodb  # Attach the database instance to the FastAPI app

    # Initialize collections and indexes if necessary
    try:
        # Note: Add document models here as needed when transferring endpoints
        await init_beanie(database=mongodb, document_models=[])
        logging.info("Beanie initialized for worker API.")
        
    except Exception as e:
        logging.error(f"Error during collection initialization: {e}")
        raise

    yield

    if mongodb_client:
        mongodb_client.close()
