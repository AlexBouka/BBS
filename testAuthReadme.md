# Testing Authentication in FastAPI Bus Booking System

This guide covers setting up Docker containers and running automated tests for authentication features.

## Prerequisites
- **Docker and Docker Compose**: Ensure Docker is installed and running.
- **Environment Variables**: Create a `.env` file in the project root with the required variables (e.g., `docker_postgres_user`, `docker_postgres_password`, etc., as referenced in `docker-compose.yml`). Also include test admin credentials like `test_admin_username`, `test_admin_email`, `test_admin_password` (used in `tests/test_utils.py` and `tests/test_auth.py`).
- **Python Dependencies**: Install pytest and httpx if running tests locally: `pip install pytest httpx`.
- **Project Code**: Ensure all files are in place, including `main.py`, routers, models, etc.

## Step 1: Set Up Docker Containers

1. **Start the Main Database (for development/manual testing)**:
   - Run: `docker-compose up -d postgres pgadmin`
   - This starts PostgreSQL on port 5432 and PgAdmin on port 5050.
   - Wait for the health check to pass (check logs: `docker-compose logs postgres`).

2. **Start the Test Database (for automated tests)**:
   - Run: `docker-compose --profile test up -d test-postgres`
   - This starts a separate PostgreSQL instance on port 5433 for tests.
   - Wait for the health check to pass.

3. **Verify Containers**:
   - Run: `docker ps` to confirm `bus_booking_db` and `bus_booking_test_db` are running.
   - Access PgAdmin at `http://localhost:5050` (use credentials from `.env`) to inspect the main DB if needed.

## Step 2: Run Automated Tests

The tests in `tests/test_auth.py` cover user registration, admin registration, login, and validation using pytest and httpx.

1. **Run All Auth Tests**:
   - Ensure the test DB is running (from Step 1).
   - Run: `pytest tests/test_auth.py -v`
   - This will:
      - Set up the test DB (via `conftest.py`).
      - Create a test admin user (via `test_utils.py`).
      - Test endpoints like `/api/auth/register`, `/api/auth/login`, `/api/auth/register/admin`.
      - Clean up the DB after tests.

2. **Run Specific Tests**:
   - Example: `pytest tests/test_auth.py::test_login_admin_user_success -v` to test admin login only.

3. **Expected Output**:
   - Tests should pass if auth logic is correct. Look for status codes (e.g., 201 for registration, 200 for login, 400/422 for errors).
   - If failures occur, check logs for details (e.g., DB connection issues).

## Clean Up
   - Stop containers: `docker-compose down` (for main) and `docker-compose --profile test down` (for test).
   - If needed, reset DB: Use PgAdmin or run `scripts/recreate_db.py`.
