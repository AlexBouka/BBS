import pytest
import httpx

from core.config import settings


@pytest.mark.asyncio
async def test_register_user_success(client: httpx.AsyncClient) -> None:
    """Test successful user registration."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser{unique_id}"
    email = f"testuser{unique_id}@example.com"
    response = await client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": "TestPass123",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == username
    assert data["email"] == email
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert data["role"] == "CUSTOMER"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "full_name" in data


@pytest.mark.asyncio
async def test_register_user_duplicate_username(
        client: httpx.AsyncClient) -> None:
    """Test registration fails with duplicate username."""
    # First registration
    await client.post(
        "/api/auth/register",
        json={
            "username": "duplicateuser",
            "email": "user1@example.com",
            "password": "TestPass123"
        }
    )

    # Second registration with same username
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "duplicateuser",
            "email": "user2@example.com",
            "password": "TestPass123"
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "Username already exists" in data["detail"]


@pytest.mark.asyncio
async def test_register_user_duplicate_email(
        client: httpx.AsyncClient) -> None:
    """Test registration fails with duplicate email."""
    # First registration
    await client.post(
        "/api/auth/register",
        json={
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "TestPass123"
        }
    )

    # Second registration with same email
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "user2",
            "email": "duplicate@example.com",
            "password": "TestPass123"
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "Email already exists" in data["detail"]


@pytest.mark.asyncio
async def test_register_user_invalid_username(
        client: httpx.AsyncClient) -> None:
    """Test registration fails with invalid username."""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "abc",  # Too short
            "email": "test@example.com",
            "password": "TestPass123"
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_user_weak_password(client: httpx.AsyncClient) -> None:
    """Test registration fails with weak password."""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "weak"  # Too short, no uppercase, no digit
        }
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_admin_success(client: httpx.AsyncClient) -> None:
    """Test successful admin registration by admin user."""
    # First login as admin to get token
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username_or_email": settings.test_admin_username,
            "password": settings.test_admin_password
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Register new admin
    response = await client.post(
        "/api/auth/register/admin",
        json={
            "username": "newadmin",
            "email": "newadmin@example.com",
            "password": "AdminPass123!",
            "first_name": "New",
            "last_name": "Admin",
            "phone_number": "+1234567890"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newadmin"
    assert data["email"] == "newadmin@example.com"
    assert data["role"] == "ADMIN"
    assert data["is_active"] is True
    assert data["is_verified"] is True


@pytest.mark.asyncio
async def test_register_admin_unauthorized(
        client: httpx.AsyncClient) -> None:
    """Test admin registration fails without admin auth."""
    response = await client.post(
        "/api/auth/register/admin",
        json={
            "username": "newadmin",
            "email": "newadmin@example.com",
            "password": "AdminPass123!"
        }
    )

    assert response.status_code == 403  # forbidden


@pytest.mark.asyncio
async def test_login_admin_user_success(
        client: httpx.AsyncClient) -> None:
    """
    Test that logging in with the test admin user credentials
    returns a successful response with an access token.
    """
    response = await client.post(
        "/api/auth/login",
        json={
            "username_or_email": settings.test_admin_username,
            "password": settings.test_admin_password
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
