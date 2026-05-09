from fastapi.testclient import TestClient

def test_create_link(client):
    response = client.post("/links/shorten", json={
        "original_url": "https://google.com",
        "expire_at": None
    })
    assert response.status_code == 200
    data = response.json()
    assert data["short_id"] is not None
    assert "google.com" in data["original_url"]

def test_create_link_with_alias(client):
    response = client.post("/links/shorten", json={
        "original_url": "https://google.com",
        "custom_alias": "my-link",
        "expire_at": None
    })
    assert response.status_code == 200
    data = response.json()
    assert data["short_id"] == "my-link"

def test_create_link_invalid_url(client):
    response = client.post("/links/shorten", json={
        "original_url": "not-a-url",
        "expire_at": None
    })
    assert response.status_code == 422

def test_redirect_link(client):
    client.post("/links/shorten", json={
        "original_url": "https://google.com",
        "custom_alias": "test-redirect",
        "expire_at": None
    })
    response = client.get("/links/test-redirect", follow_redirects=False)
    assert response.status_code == 307
    assert "google.com" in response.headers["location"]

def test_redirect_link_not_found(client):
    response = client.get("/links/nonexistent", follow_redirects=False)
    assert response.status_code == 404

def test_get_stats_unauthorized(client):
    client.post("/links/shorten", json={
        "original_url": "https://google.com",
        "custom_alias": "test-stats",
        "expire_at": None
    })
    response = client.get("/links/test-stats/stats")
    assert response.status_code == 401

def test_delete_link(auth_client):
    auth_client.post("/links/shorten", json={
        "original_url": "https://google.com",
        "custom_alias": "to-delete",
        "expire_at": None
    })
    response = auth_client.delete("/links/to-delete")
    assert response.status_code == 200
    response = auth_client.get("/links/to-delete", follow_redirects=False)
    assert response.status_code == 404


def test_delete_link_unauthorized(client):
    client.post("/links/shorten", json={
        "original_url": "https://google.com",
        "custom_alias": "to-delete-unauth",
        "expire_at": None
    })
    response = client.delete("/links/to-delete-unauth")
    assert response.status_code == 401


def test_update_link(auth_client):
    auth_client.post("/links/shorten", json={
        "original_url": "https://google.com",
        "custom_alias": "to-update",
        "expire_at": None
    })
    response = auth_client.put("/links/to-update", json={
        "original_url": "https://yandex.ru",
        "expire_at": None
    })
    assert response.status_code == 200
    assert "yandex.ru" in response.json()["original_url"]


def test_search_links(auth_client):
    auth_client.post("/links/shorten", json={
        "original_url": "https://github.com",
        "expire_at": None
    })
    response = auth_client.get("/links/search/?original_url=github")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_delete_link_not_found(auth_client):
    response = auth_client.delete("/links/nonexistent")
    assert response.status_code == 404


def test_update_link_not_found(auth_client):
    response = auth_client.put("/links/nonexistent", json={
        "original_url": "https://yandex.ru",
        "expire_at": None
    })
    assert response.status_code == 404


def test_get_stats_not_found(auth_client):
    response = auth_client.get("/links/nonexistent/stats")
    assert response.status_code == 404