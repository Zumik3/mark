from starlette.requests import Request
from models import InsertKitModel, ArticleModel, SimpleAnswer, \
    IntegrityAnswer, CountArticlesAnswer, DeleteAnswer


async def ping() -> SimpleAnswer:
    return SimpleAnswer(status=True)


async def insert_kits(request: Request, body: InsertKitModel) -> SimpleAnswer:
    db = request.app.state.db
    async with db.pool.acquire() as connection:
        for element in body.data:
            query = """INSERT INTO km (kit, article)
                       VALUES ($1, $2)
                       ON CONFLICT(kit)
                       DO UPDATE SET kit=$1, article=$2;"""

            await connection.fetch(query, element.kit, element.article)

    return SimpleAnswer(status=True)


async def delete_kits(request: Request, body: ArticleModel) -> DeleteAnswer:
    db = request.app.state.db
    async with db.pool.acquire() as connection:
        counter = 0
        for element in body.data:
            query = f"DELETE FROM km WHERE article = '{element}' RETURNING *"
            result = await connection.fetch(query)
            counter += len(result)

    return DeleteAnswer(status=True, deleted=counter)


async def check_kit_integrity(request: Request, body: ArticleModel) -> IntegrityAnswer:
    db = request.app.state.db
    async with db.pool.acquire() as connection:
        body_to_string = "', '".join(body.data)
        query = f"SELECT article FROM km WHERE article NOT IN('{body_to_string}') GROUP BY article;"
        result = await connection.fetch(query)

    integrity = False if len(result) else True
    return IntegrityAnswer(status=True, data=result, integrity=integrity)


async def count_articles(request: Request, article: str) -> CountArticlesAnswer:
    db = request.app.state.db
    async with db.pool.acquire() as connection:
        query = f"SELECT count(*) FROM km WHERE article = '{article.strip()}';"
        result = await connection.fetch(query)

    quantity = result[0]['count']
    return CountArticlesAnswer(status=True, quantity=quantity)


async def get_article_by_kit(request: Request, kit: str):
    db = request.app.state.db
    async with db.pool.acquire() as connection:
        query = f"SELECT article FROM km WHERE kit ='{kit.strip()}';"
        result = await connection.fetch(query)

    return {'status': True, 'article': result[0]['article'] if len(result) else None}
