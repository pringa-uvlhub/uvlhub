import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_get_explore(test_client):
    response = test_client.get('/explore')
    assert response.status_code == 200
    assert b'<form' in response.data
    assert b'name="query"' in response.data
    assert b'value=""' in response.data


def test_filter_by_author(client):
    # Simula el envío del filtro "queryAuthor" con el valor "Author 3".
    response = client.post('/explore', json={
        'csrf_token': 'dummy_token',
        'query': '',
        'queryAuthor': 'Author 3',
        'queryTag': '',
        'queryFeatures': '',
        'queryModels': '',
        'publication_type': 'any',
        'sorting': 'newest',
    })

    # Verifica que la respuesta sea exitosa.
    assert response.status_code == 200

    data = response.get_json()

    # Verifica que solo se devuelve un dataset con el autor "Author 3".
    assert len(data) == 1
    assert data[0]['authors'][0]['name'] == 'Author 3'


def test_filter_by_author_empty(client):
    # Simula el envío del filtro "queryAuthor" con el valor "Author empty".
    response = client.post('/explore', json={
        'csrf_token': 'dummy_token',
        'query': '',
        'queryAuthor': 'Author empty',
        'queryTag': '',
        'queryFeatures': '',
        'queryModels': '',
        'publication_type': 'any',
        'sorting': 'newest',
    })

    # Verifica que la respuesta sea exitosa.
    assert response.status_code == 200

    data = response.get_json()

    # Verifica que no se devuelve ningun dataset.
    assert len(data) == 0


def test_filter_by_tag(client):
    # Simula el envío del filtro "queryTag" con el valor "tag3".
    response = client.post('/explore', json={
        'csrf_token': 'dummy_token',
        'query': '',
        'queryAuthor': '',
        'queryTag': 'tag3',
        'queryFeatures': '',
        'queryModels': '',
        'publication_type': 'any',
        'sorting': 'newest',
    })

    # Verifica que la respuesta sea exitosa.
    assert response.status_code == 200

    data = response.get_json()

    # Verifica que los datasets contienen la etiqueta "tag3".
    assert len(data) == 3
    for dataset in data:
        assert 'tag3' in dataset['tags']


def test_filter_by_tag_empty(client):
    # Simula el envío del filtro "queryTag" con el valor "tag empty".
    response = client.post('/explore', json={
        'csrf_token': 'dummy_token',
        'query': '',
        'queryAuthor': '',
        'queryTag': 'tag empty',
        'queryFeatures': '',
        'queryModels': '',
        'publication_type': 'any',
        'sorting': 'newest',
    })

    # Verifica que la respuesta sea exitosa.
    assert response.status_code == 200

    data = response.get_json()

    # Verifica que no se devuelve ningun dataset.
    assert len(data) == 0


def test_filter_by_number_of_models(client):
    # Simula el envío del filtro "queryModels" con el valor "5".
    response = client.post('/explore', json={
        'csrf_token': 'dummy_token',
        'query': '',
        'queryAuthor': '',
        'queryTag': '',
        'queryFeatures': '',
        'queryModels': '5',
        'publication_type': 'any',
        'sorting': 'newest',
    })

    # Verifica que la respuesta sea exitosa.
    assert response.status_code == 200

    data = response.get_json()

    # Verifica que solo se devuelve un dataset y es el "Sample dataset 2".
    assert len(data) == 1
    assert data[0]['title'] == "Sample dataset 2"


def test_filter_by_number_of_models_empty(client):
    # Simula el envío del filtro "queryModels" con el valor "9".
    response = client.post('/explore', json={
        'csrf_token': 'dummy_token',
        'query': '',
        'queryAuthor': '',
        'queryTag': '',
        'queryFeatures': '',
        'queryModels': '9',
        'publication_type': 'any',
        'sorting': 'newest',
    })

    # Verifica que la respuesta sea exitosa.
    assert response.status_code == 200

    data = response.get_json()

    # Verifica que no se devuelve ningun dataset.
    assert len(data) == 0


def test_filter_by_number_of_features(client):
    # Simula el envío del filtro "queryFeatures" con el valor "40".
    response = client.post('/explore', json={
        'csrf_token': 'dummy_token',
        'query': '',
        'queryAuthor': '',
        'queryTag': '',
        'queryFeatures': '40',
        'queryModels': '',
        'publication_type': 'any',
        'sorting': 'newest',
    })

    # Verifica que la respuesta sea exitosa.
    assert response.status_code == 200

    data = response.get_json()

    # Verifica que se devuelven 3 datasets.
    assert len(data) == 3


def test_filter_by_number_of_features_empty(client):
    # Simula el envío del filtro "queryFeatures" con el valor "100".
    response = client.post('/explore', json={
        'csrf_token': 'dummy_token',
        'query': '',
        'queryAuthor': '',
        'queryTag': '',
        'queryFeatures': '100',
        'queryModels': '',
        'publication_type': 'any',
        'sorting': 'newest',
    })

    # Verifica que la respuesta sea exitosa.
    assert response.status_code == 200

    data = response.get_json()

    # Verifica que no se devuelve ningun dataset.
    assert len(data) == 0


def test_filter_combination(client):
    response = client.post('/explore', json={
        'csrf_token': 'dummy_token',
        'query': '',
        'queryAuthor': '',
        'queryTag': 'tag3',
        'queryFeatures': '40',
        'queryModels': '7',
        'publication_type': 'any',
        'sorting': 'newest',
    })

    # Verifica que la respuesta sea exitosa.
    assert response.status_code == 200

    data = response.get_json()

    # Verifica que se devuelven 2 datasets.
    assert len(data) == 2
