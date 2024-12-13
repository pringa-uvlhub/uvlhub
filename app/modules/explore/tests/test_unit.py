import pytest
from app import create_app, db
from app.modules.dataset.models import DSMetrics, DSMetaData, PublicationType, Author, DataSet
from app.modules.featuremodel.models import FMMetaData, FeatureModel
from app.modules.auth.models import User
from datetime import datetime, timezone, timedelta


@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            # Configuración de la base de datos en modo de prueba
            db.drop_all()
            db.create_all()

            ds_metrics = [
                DSMetrics(id=1, number_of_models='5', number_of_features='50'),
                DSMetrics(id=2, number_of_models='7', number_of_features='40')
            ]

            for metric in ds_metrics:
                db.session.add(metric)
                db.session.commit()

            ds_meta_data_list = [
                DSMetaData(
                    id=i+1,
                    deposition_id=1 + i,
                    title=f'Sample dataset {i+1}',
                    description=f'Description for dataset {i+1}',
                    publication_type=PublicationType.BOOK if i == 1 else PublicationType.DATA_MANAGEMENT_PLAN,
                    publication_doi=f'10.1234/dataset{i+1}',
                    build=False,
                    dataset_doi=f'10.1234/dataset{i+1}',
                    tags='tag1, tag2' if i == 2 else 'tag3',
                    staging_area=False,
                    ds_metrics_id=ds_metrics[0].id if i == 1 else ds_metrics[1].id
                ) for i in range(4)
            ]

            for meta_data in ds_meta_data_list:
                db.session.add(meta_data)
                db.session.commit()

            authors = [
                Author(
                    id=i+1,
                    name=f'Author {i+1}',
                    affiliation=f'Affiliation {i+1}',
                    orcid=f'0000-0000-0000-000{i}',
                    ds_meta_data_id=ds_meta_data_list[i % 4].id
                ) for i in range(4)
            ]

            for author in authors:
                db.session.add(author)
                db.session.commit()

            users = [
                User(
                    id=1,
                    email="user1@example.com",
                    password="scrypt:32768:8:1$3MJHBrH1F2YxJSos$1465633477bd4b3af03f5e7cd8b46dd984ff8a36dcac2f2f" +
                             "884130a7660faff964c206699cb07d5fffa9821b67f5ed4cc8dd532ed838b6c0d442a8d1772c5f21",
                    created_at=datetime.now(timezone.utc)
                ),
                User(
                    id=2,
                    email="user2@example.com",
                    password=(
                        "scrypt:32768:8:1$OxiU6qWqrIbVJvFY$79b92bf223fd3d97f442c021f1f7dc3e6f403c855c3290498976e" +
                        "f4d8ea3c60677befb91755a0d7ff87b78060943424b0b80afb35499b563133e96e6e43516f6"
                    ),
                    created_at=datetime.now(timezone.utc)
                )
            ]

            for user in users:
                db.session.add(user)
                db.session.commit()

            datasets = [
                DataSet(
                    id=i+1,
                    user_id=users[0].id if i % 2 == 0 else users[1].id,
                    ds_meta_data_id=ds_meta_data_list[i].id,
                    created_at=datetime.now(timezone.utc) - timedelta(days=i)
                ) for i in range(4)
            ]

            for dataset in datasets:
                db.session.add(dataset)
                db.session.commit()

            fm_meta_data_list = [
                FMMetaData(
                    id=i+1,
                    uvl_filename=f'file{i+1}.uvl',
                    title=f'Feature Model {i+1}',
                    description=f'Description for feature model {i+1}',
                    publication_type=PublicationType.SOFTWARE_DOCUMENTATION,
                    publication_doi=f'10.1234/fm{i+1}',
                    tags='tag1, tag2',
                    uvl_version='1.0'
                ) for i in range(12)
            ]

            for fm_meta_data in fm_meta_data_list:
                db.session.add(fm_meta_data)
                db.session.commit()

            fm_authors = [
                Author(
                    id=i+5,
                    name=f'Author {i+5}',
                    affiliation=f'Affiliation {i+5}',
                    orcid=f'0000-0000-0000-000{i+5}',
                    fm_meta_data_id=fm_meta_data_list[i].id
                ) for i in range(12)
            ]

            for fm_author in fm_authors:
                db.session.add(fm_author)
                db.session.commit()

            feature_models = [
                FeatureModel(
                    data_set_id=datasets[i // 3].id,
                    fm_meta_data_id=fm_meta_data_list[i].id
                ) for i in range(12)
            ]

            for feature_model in feature_models:
                db.session.add(feature_model)
                db.session.commit()

            yield client
            db.session.remove()
            db.drop_all()


def test_get_explore(client):
    response = client.get('/explore')
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


def test_filter_publication_type(client):
    # Simula el envío del filtro "publication_type" con el valor "book".
    response = client.post('/explore', json={
        'csrf_token': 'dummy_token',
        'query': '',
        'queryAuthor': '',
        'queryTag': '',
        'queryFeatures': '',
        'queryModels': '',
        'publication_type': 'book',
        'sorting': 'newest',
    })

    # Verifica que la respuesta sea exitosa.
    assert response.status_code == 200

    data = response.get_json()

    # Verifica que solo se devuelve un dataset y es el "Sample dataset 2".
    assert len(data) == 1
    assert data[0]['title'] == "Sample dataset 2"


def test_sorting(client):
    # Simula el envío del filtro "sorting" con el valor "newest".
    response = client.post('/explore', json={
        'csrf_token': 'dummy_token',
        'query': '',
        'queryAuthor': '',
        'queryTag': '',
        'queryFeatures': '',
        'queryModels': '',
        'publication_type': '',
        'sorting': 'newest',
    })

    # Verifica que la respuesta sea exitosa.
    assert response.status_code == 200

    data = response.get_json()

    # Verifica que se devuelven 4 datasets.
    assert len(data) == 4

    # Verifica el orden de los datasets.
    for i in range(len(data) - 1):
        assert data[i]['title'] == "Sample dataset " + str(i+1)

    # Simula el envío del filtro "sorting" con el valor "oldest".
    response = client.post('/explore', json={
        'csrf_token': 'dummy_token',
        'query': '',
        'queryAuthor': '',
        'queryTag': '',
        'queryFeatures': '',
        'queryModels': '',
        'publication_type': '',
        'sorting': 'oldest',
    })

    # Verifica que la respuesta sea exitosa.
    assert response.status_code == 200

    data = response.get_json()

    # Verifica que se devuelven 4 datasets.
    assert len(data) == 4

    # Verifica el orden de los datasets.
    for i in range(3, -1, -1):
        assert data[3 - i]['title'] == "Sample dataset " + str(i+1)
