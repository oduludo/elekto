from datetime import datetime
from flask.testing import FlaskClient
from pytest_mock import MockerFixture

from elekto import APP, SESSION, constants
from elekto.models.sql import User


def test_dashboard(client: FlaskClient):
    token="token"
    with APP.app_context():
        SESSION.add(User(username="carson",
                             name="Carson Weeks",
                             token=token,
                             token_expires_at=datetime.max))
        SESSION.commit()
    with client.session_transaction() as session:
        session[constants.AUTH_STATE] = token
    response = client.get("/app")
    assert response.status_code == 200
    assert b'Welcome! Carson Weeks' in response.data
    assert b'Sit back and Relax, there is not to do yet.' in response.data

def test_unauthenticated_dashboard(client: FlaskClient):
    with client.session_transaction() as session:
        session[constants.AUTH_STATE] = None
    response = client.get("/app")
    assert response.status_code == 302

def test_elections_running_dashboard(client: FlaskClient, mocker: MockerFixture):
    mocker.patch("elekto.meta.Election.where", return_value=[{"name": "Demo Election", 
                                                              "organization": "kubernetes", 
                                                              "start_datetime": datetime.min, 
                                                              "end_datetime": datetime.max}])
    token="token"
    with APP.app_context():
        SESSION.add(User(username="carson",
                             name="Carson Weeks",
                             token=token,
                             token_expires_at=datetime.max))
        SESSION.commit()
    with client.session_transaction() as session:
        session[constants.AUTH_STATE] = token
    response = client.get("/app")
    assert response.status_code == 200
    assert b"Demo Election" in response.data 
    assert not b"Sit back and Relax, there is not to do yet." in response.data