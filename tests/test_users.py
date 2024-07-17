from datetime import datetime, timedelta
from http import HTTPStatus

from freezegun import freeze_time
from sqlalchemy import select

from fast_zero.models import User
from fast_zero.schemas import UserPublic


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
            'username': user.username,
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
            'email': user.email,
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


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
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
        'id': user.id,
    }


def test_update_other_user(client, user, token):
    response = client.put(
        '/users/5',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_get_user_with_id(client, user, token):
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': user.username,
        'email': user.email,
        'id': user.id,
    }


def test_get_user_with_invalid_id(client, user, token):
    response = client.get('/users/5')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_other_user(client, user, token):
    response = client.delete('/users/5')

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_field_update_at(client, user, session, token):
    first_update = user.update_at
    frozen_time = datetime.now() + timedelta(minutes=15)

    with freeze_time(frozen_time):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'Teste5',
                'email': 'teste5@test.com',
                'password': 'mynewpassword',
            },
        )
        # session.expire(user)
        user_up = session.scalar(select(User).where(User.id == user.id))
        second_update = user_up.update_at

    assert response.status_code == HTTPStatus.OK
    assert first_update != second_update


def test_update_user_with_wrong_user(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
