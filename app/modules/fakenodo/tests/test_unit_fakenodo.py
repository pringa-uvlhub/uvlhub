import pytest
from app import create_app, db


@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.drop_all()
            db.create_all()
            yield client


def test_connection_fakenodo(client):
    response = client.get('/fakenodo/api')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == "success"
    assert data['message'] == "Connected to FakenodoAPI"


def test_delete_deposition(client):
    response = client.delete('/fakenodo/api/deposit/depositions/12345')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == "success"
    assert data['message'] == "Succesfully deleted deposition 12345"


def test_get_all_depositions(client):
    response = client.get('/fakenodo/api/deposit/depositions')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data['depositions'], list)
    assert len(data['depositions']) == 2  # based on the simulated data


def test_upload_file(client):
    response = client.post('/fakenodo/api/deposit/depositions/12345/files')
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == "File uploaded successfully"


def test_publish_deposition(client):
    response = client.post('/fakenodo/api/deposit/depositions/12345/actions/publish')
    assert response.status_code == 202
    data = response.get_json()
    assert data['doi'] == "10.5072/fakenodo.12345"
    assert data['id'] == 12345


def test_get_deposition(client):
    response = client.get('/fakenodo/api/deposit/depositions/12345')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == 12345
    assert 'metadata' in data
    assert 'files' in data


def test_deposition_not_found(client):
    response = client.get('/fakenodo/api/deposit/depositions/99999/nonexistent')
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == "Deposition not found"
