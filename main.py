from fastapi import FastAPI, Request
import asyncpg
import uvicorn
from fastapi.routing import APIRoute, APIRouter
from handlers import ping, insert_kits, delete_kits, count_articles, \
    check_kit_integrity, get_article_by_kit
import settings


class Database:
    def __init__(self):
        self.pool = None

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(dsn=settings.POSTGRES_DATABASE_URL)


def create_app():
    _app = FastAPI()
    db = Database()
    _app.state.db = db

    @_app.middleware('http')
    async def db_session_middleware(request: Request, call_next):
        request.state.pgpool = db.pool
        return await call_next(request)

    @_app.on_event('startup')
    async def startup():
        await db.create_pool()

    @_app.on_event('shutdown')
    async def shutdown():
        await db.pool.close()

    return _app


app = create_app()

base_routes = [
    APIRoute(path='/ping', endpoint=ping, methods=['GET']),
    APIRoute(path="/api/1.0/insert_data", endpoint=insert_kits, methods=["PUT"]),
    APIRoute(path="/api/1.0/delete_data", endpoint=delete_kits, methods=["POST"]),
    APIRoute(path="/api/1.0/check_article", endpoint=count_articles, methods=["GET"]),
    APIRoute(path="/api/1.0/article_by_kit", endpoint=get_article_by_kit, methods=["GET"]),
    APIRoute(path="/api/1.0/check_integrity", endpoint=check_kit_integrity, methods=["POST"])
]

app.include_router(APIRouter(routes=base_routes))


if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='0.0.0.0')
