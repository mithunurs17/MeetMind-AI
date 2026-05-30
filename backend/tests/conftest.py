import os
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-tests-only-32chars!!")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_EMAIL",    "admin@meetmind.local")
os.environ.setdefault("ADMIN_PASSWORD", "Admin@12345!")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    # Seed the admin account just like main.py does
    from app.crud.user import create_user, get_user_by_username
    from app.schemas.auth import UserRegister
    from app.models.user import UserRole

    with TestingSessionLocal() as db:
        if get_user_by_username(db, "admin") is None:
            create_user(db, UserRegister(
                email="admin@meetmind.local",
                username="admin",
                password="Admin@12345!",
                role=UserRole.ADMIN,
            ))
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client