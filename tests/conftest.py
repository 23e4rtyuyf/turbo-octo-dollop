import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import all models to register them with Base.metadata before tests run
from app.db.database import Base, get_db
import app.db.database  # noqa: F401

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Provide a test client with an in-memory database."""
    # Create tables on the test engine
    Base.metadata.create_all(bind=test_engine)

    # Patch the database module to use test engine so init_db() uses test engine
    import app.db.database as db_module
    original_engine = db_module.engine
    original_session_local = db_module.SessionLocal
    db_module.engine = test_engine
    db_module.SessionLocal = TestingSessionLocal

    from app.main import app
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    db_module.engine = original_engine
    db_module.SessionLocal = original_session_local
    Base.metadata.drop_all(bind=test_engine)
