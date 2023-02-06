import asyncio
import os
from fastapi.testclient import TestClient

import pytest_asyncio
import asyncpg

import settings
from main import app


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
def create_database_and_run_migrations():
    os.system(f'yoyo apply --database {settings.POSTGRES_DATABASE_URL} .\\migrations\\ -b')


@pytest_asyncio.fixture(scope="session")
async def test_db():
    pool = await asyncpg.create_pool(settings.POSTGRES_DATABASE_URL)
    yield pool


@pytest_asyncio.fixture(scope="session")
async def test_client():
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_tables(test_db):
    """Clean data in all tables before running test function"""
    async with test_db.acquire() as connection:
        await connection.execute("""TRUNCATE TABLE km;""")
