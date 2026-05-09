import string
import pytest
from src.links.crud import (
    generate_short_id,
    create_link,
    get_link_by_short_id,
    update_link,
    search_links
)
from src.links.schemas import LinkCreate
from datetime import datetime, timezone, timedelta
from src.links.exceptions import (
    NotUniqueAliasError,
    AliasLengthError,
    LinkExpiredError,
    PermissionDeniedError,
    InvalidURLFormatError
)
from src.links.crud import create_link, get_link_by_short_id, update_link, search_links

def test_generate_short_id_length():
    result = generate_short_id()
    assert len(result) == 6

def test_generate_short_id_custom_length():
    result = generate_short_id(length=10)
    assert len(result) == 10

def test_generate_short_id_valid_chars():
    allowed = set(string.ascii_letters + string.digits)
    result = generate_short_id()
    assert all(c in allowed for c in result)

def test_generate_short_id_uniqueness():
    results = {generate_short_id() for _ in range(100)}
    assert len(results) > 90

def test_link_create_valid():
    link = LinkCreate(original_url="https://google.com", expire_at=None)
    assert str(link.original_url) == "https://google.com/"

def test_link_expire_at_in_past():
    with pytest.raises(ValueError):
        LinkCreate(original_url="https://google.com", expire_at=datetime.now(timezone.utc) -timedelta(days=1))

def test_link_expire_at_in_future():
    future = datetime.now(timezone.utc) + timedelta(days=30)
    link = LinkCreate(original_url="https://google.com", expire_at=future)
    assert link.expire_at is not None

def test_link_create_invalid_alias():
    with pytest.raises(ValueError):
        LinkCreate(original_url="https://google.com", custom_alias="ab")

def test_link_create_alias_with_spaces():
    with pytest.raises(ValueError):
        LinkCreate(original_url="https://google.com", custom_alias="my_alias")

def test_not_unique_alias_error():
    exc = NotUniqueAliasError("my-link")
    assert exc.status_code == 400
    assert "my-link" in exc.detail


def test_alias_length_error():
    exc = AliasLengthError("ab")
    assert exc.status_code == 400
    assert "ab" in exc.detail


def test_link_expired_error():
    exc = LinkExpiredError("abc123")
    assert exc.status_code == 410
    assert "abc123" in exc.detail

def test_permission_denied_error():
    exc = PermissionDeniedError()
    assert exc.status_code == 403


def test_invalid_url_format_error():
    exc = InvalidURLFormatError("not-a-url")
    assert exc.status_code == 400
    assert "not-a-url" in exc.detail

@pytest.mark.asyncio
async def test_crud_create_and_get(db_session):
    link = await create_link(db_session, "https://google.com", custom_alias="test-crud")
    assert link.short_id == "test-crud"
    assert link.original_url == "https://google.com"

    found = await get_link_by_short_id(db_session, "test-crud")
    assert found is not None
    assert found.short_id == "test-crud"

@pytest.mark.asyncio
async def test_crud_update_link(db_session):
    link = await create_link(db_session, "https://google.com", custom_alias="to-update-crud")
    updated = await update_link(db_session, link, "https://yandex.ru")
    assert updated.original_url == "https://yandex.ru"

@pytest.mark.asyncio
async def test_crud_search_links(db_session):
    await create_link(db_session, "https://github.com/test", user_id=99)
    results = await search_links(db_session, "github", user_id=99)
    assert len(results) > 0