import pytest


kit_list = [{'kit': '0104640179541735215eJrQSuZF(aDd', 'article': '132123/03-01'},
            {'kit': '0104640179541742215eR=j)R_+4uCj', 'article': '132123/03-01'},
            {'kit': '0104640179541759215Zj"KdUS*DhOS', 'article': '132123/03-02'}]


@pytest.mark.asyncio
async def test_ping(test_client):
    response = test_client.get('/ping')
    resp_json = response.json()
    assert response.status_code == 200
    assert resp_json['status']


@pytest.mark.asyncio
async def test_insert_kits(test_db, test_client):
    insert_data = {"data": kit_list}
    response = test_client.put('/api/1.0/insert_data', json=insert_data)
    resp_json = response.json()
    assert response.status_code == 200
    assert resp_json['status']

    async with test_db.acquire() as connection:
        result = await connection.fetch("SELECT count(*) FROM km")
        assert result[0]['count'] == 3

        query = "SELECT count(*) FROM km WHERE article = '132123/03-01';"
        result = await connection.fetch(query)
        assert result[0]['count'] == 2

        # await connection.execute("TRUNCATE TABLE km;")


@pytest.mark.asyncio
async def test_delete_kits(test_db, test_client):
    insert_data = {"data": kit_list}
    test_client.put('/api/1.0/insert_data', json=insert_data)

    article_list = ['132123/03-01', '132123/03-02']
    delete_data = {"data": article_list}

    async with test_db.acquire() as connection:
        response = test_client.post('/api/1.0/delete_data', json=delete_data)
        resp_json = response.json()
        assert response.status_code == 200
        assert resp_json['status']

        query = "SELECT count(*) FROM km WHERE article = '132123/03-01';"
        result = await connection.fetch(query)
        assert result[0]['count'] == 0

        result = await connection.fetch(f"SELECT count(*) FROM km;")
        assert result[0]['count'] == 0


@pytest.mark.asyncio
async def test_check_article(test_db, test_client):
    struct_data = {"data": kit_list}
    test_client.put('/api/1.0/insert_data', json=struct_data)

    article = '132123/03-01'
    response = test_client.get(f'/api/1.0/check_article?article={article}')
    resp_json = response.json()
    assert response.status_code == 200
    assert resp_json['status']
    assert resp_json['quantity'] == 2

    async with test_db.acquire() as connection:
        result = await connection.fetch(f"SELECT count(*) FROM km WHERE article = '{article}';")
        assert result[0]['count'] == 2

        await connection.execute("TRUNCATE TABLE km;")


@pytest.mark.asyncio
async def test_get_article_by_kit(test_db, test_client):
    struct_data = {"data": kit_list}
    test_client.put('/api/1.0/insert_data', json=struct_data)

    kit = '0104640179541759215Zj"KdUS*DhOS'
    article = '132123/03-02'
    response = test_client.get(f'/api/1.0/article_by_kit?kit={kit}')
    resp_json = response.json()
    assert response.status_code == 200
    assert resp_json['status']
    assert resp_json['article'] == article

    async with test_db.acquire() as connection:
        result = await connection.fetch(f"SELECT article FROM km WHERE kit ='{kit}'")
        assert result[0]['article'] == article

        await connection.execute("TRUNCATE TABLE km;")


@pytest.mark.asyncio
async def test_check_integrity(test_db, test_client):
    struct_data = {"data": kit_list}
    test_client.put('/api/1.0/insert_data', json=struct_data)

    article_list1 = ['132123/03-01', '132123/03-02']
    integrity_data1 = {"data": article_list1}

    article_list2 = ['132123/03-01']
    integrity_data2 = {"data": article_list2}

    response = test_client.post('/api/1.0/check_integrity', json=integrity_data1)
    resp_json = response.json()
    assert response.status_code == 200
    assert resp_json['status']
    assert resp_json['integrity']
    assert len(resp_json['data']) == 0

    response = test_client.post('/api/1.0/check_integrity', json=integrity_data2)
    resp_json = response.json()
    assert response.status_code == 200
    assert resp_json['status']
    assert resp_json['integrity'] is False
    assert resp_json['data'][0]['article'] == '132123/03-02'
