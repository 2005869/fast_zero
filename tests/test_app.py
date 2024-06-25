import time
from http import HTTPStatus

from sqlalchemy import select

from fast_zero.models import User
from fast_zero.schemas import UserPublic


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo'}


def test_deve_retornar_ok_e_html(client):
    response = client.get('/html')

    assert response.status_code == HTTPStatus.OK
    assert response.text == """<h1>Olá Mundo</h1>"""


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'alice',
            'email': 'alice@exemplo.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@exemplo.com',
        'id': 1,
    }


def test_error_create_user_username_already_exists(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'Teste',
            'email': 'alice@exemplo.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_error_create_user_email_already_exists(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'alice',
            'email': 'teste@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Email already exists'}


def test_read_users(client):
    response = client.get('/users')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users')

    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'bob',
        'email': 'bob@example.com',
        'id': 1,
    }


def test_update_user_not_found_maior_que_database(client):
    response = client.put(
        '/users/5',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user_not_found_menor_que_database(client):
    response = client.put(
        '/users/0',
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client, user):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_get_user_with_id(client, user):
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Teste',
        'email': 'teste@test.com',
        'id': 1,
    }


def test_get_user_with_invalid_id(client):
    response = client.get('/users/5')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user_not_found_maior_que_database(client):
    response = client.delete('/users/5')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user_not_found_menor_que_database(client):
    response = client.delete('/users/0')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user_not_exist(client):
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_field_update_at(client, user, session):
    first_update = user.update_at
    time.sleep(1)
    client.put(
        '/users/1',
        json={
            'username': 'Teste2',
            'email': 'teste2@test.com',
            'password': 'mynewpassword',
        },
    )
    new_data = session.scalar(select(User).where(User.id == 1))
    second_update = new_data.update_at
    assert first_update != second_update
