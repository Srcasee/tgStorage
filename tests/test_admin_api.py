from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_admin_accounts_endpoint_exists():
    response = client.get('/api/v2/admin/accounts')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_sources_endpoint_exists():
    response = client.get('/api/v2/admin/sources')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_resources_endpoint_exists():
    response = client.get('/api/v2/admin/resources')
    assert response.status_code == 200
    assert isinstance(response.json(), list)
