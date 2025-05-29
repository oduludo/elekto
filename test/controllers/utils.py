from datetime import datetime

from flask.testing import FlaskClient

from elekto import APP, SESSION, constants
from elekto.models.sql import User


def create_user(token) -> None:
    with APP.app_context():
        SESSION.add(User(username='carson',
                         name='Carson Weeks',
                         token=token,
                         token_expires_at=datetime.max))
        SESSION.commit()


def provision_session(client: FlaskClient, token: str) -> None:
    create_user(token)

    with client.session_transaction() as session:
        session[constants.AUTH_STATE] = token


def is_authenticated(client: FlaskClient) -> bool:
    """
    Test if the client has an authenticated session by calling /login and see what happens.

    If /login responds with HTTP302, the user IS authenticated.
    If /login responds with HTTP200, the user IS NOT authenticated.
    """
    return client.get('/login').status_code == 302


def user_exists(username: str) -> bool:
    with APP.app_context():
        return SESSION.query(User).filter_by(username=username).count() == 1


def get_csrf_token(client: FlaskClient) -> str:
    response = client.get('/login')
    csrf_token = response.data.decode('utf8').split('csrf_token" value="')[1].split('"')[0]
    return csrf_token
