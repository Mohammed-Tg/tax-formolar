import pytest
from app import create_app
from app.config import Config
from app.extensions import db as _db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEV_USER_ENABLED = False
    MAIL_SUPPRESS_SEND = True


@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    return app.test_client()


@pytest.fixture(scope='function')
def db(app):
    return _db


def create_user(db, **kwargs):
    from app.models.user import User
    user = User(
        first_name=kwargs.get('first_name', 'Test'),
        last_name=kwargs.get('last_name', 'User'),
        username=kwargs.get('username', 'test.user'),
        email=kwargs.get('email', 'test@example.com'),
        password='')
    user.set_password(kwargs.get('password', 'password'))
    user.verification_code = ''
    user.is_verified = True
    db.session.add(user)
    db.session.commit()
    return user
