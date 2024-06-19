from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app


def test_root_deve_retornar_ok_e_ola_mundo():
    client = TestClient(app)
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo'}


def test_deve_retornar_ok_e_html():
    client = TestClient(app)
    response = client.get('/html')

    assert response.status_code == HTTPStatus.OK
    assert response.text == """<h1>Olá Mundo</h1>"""
