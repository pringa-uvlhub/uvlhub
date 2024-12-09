import pytest
import os
from enum import Enum
from app import create_app, db
from app.modules.conftest import login, logout
from app.modules.dataset.models import DataSet, DSMetaData, DSRating
from app.modules.profile.models import UserProfile
from app.modules.featuremodel.models import *
from app.modules.auth.models import User
from datetime import datetime


class PublicationType(Enum):
    NONE = 'none'
    ANNOTATION_COLLECTION = 'annotationcollection'
    BOOK = 'book'
    BOOK_SECTION = 'section'
    CONFERENCE_PAPER = 'conferencepaper'
    DATA_MANAGEMENT_PLAN = 'datamanagementplan'
    JOURNAL_ARTICLE = 'article'
    PATENT = 'patent'
    PREPRINT = 'preprint'
    PROJECT_DELIVERABLE = 'deliverable'
    PROJECT_MILESTONE = 'milestone'
    PROPOSAL = 'proposal'
    REPORT = 'report'
    SOFTWARE_DOCUMENTATION = 'softwaredocumentation'
    TAXONOMIC_TREATMENT = 'taxonomictreatment'
    TECHNICAL_NOTE = 'technicalnote'
    THESIS = 'thesis'
    WORKING_PAPER = 'workingpaper'
    OTHER = 'other'


@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            # Configuración de la base de datos en modo de prueba
            db.drop_all()
            db.create_all()
            user = User(id=5, email="user5@example.com", password="1234", created_at=datetime(2022, 3, 13))
            db.session.add(user)
            db.session.commit()
            profile = UserProfile(user_id=user.id, surname="TestSurname", name="TestName", affiliation="TestAffiliation", orcid="0000-0001-2345-6789")
            db.session.add(profile)
            db.session.commit()
            dsmetadata = DSMetaData(id=10, title="Sample Dataset 11", rating=1, description="Description for dataset 11",
                                    publication_type=PublicationType.DATA_MANAGEMENT_PLAN.name, staging_area=False)
            db.session.add(dsmetadata)
            dataset = DataSet(id=10, user_id=user.id, ds_meta_data_id=dsmetadata.id)
            db.session.add(dataset)
            db.session.commit()
            dsrating = DSRating(id=10, user_id=user.id, ds_meta_data_id=dsmetadata.id, rating=dsmetadata.rating, rated_date=datetime(2022, 3, 13))
            db.session.add(dsrating)
            db.session.commit()
            # Crear un dataset en el staging area
            dsmetadata_sa = DSMetaData(id=11, title="Staging area Dataset", description="Description for unique dataset",
                                    publication_type=PublicationType.DATA_MANAGEMENT_PLAN.name)
            db.session.add(dsmetadata_sa)
            dataset_staging_area = DataSet(id=11, user_id=user.id, ds_meta_data_id=dsmetadata_sa.id)
            db.session.add(dataset_staging_area)
            db.session.commit()
            user1 = User(id=6, email="user6@example.com", password="1234", created_at=datetime(2022, 3, 13))
            db.session.add(user1)
            db.session.commit()
            fm_metadata = FMMetaData(
                uvl_filename="test_model.uvl",
                title="Test Feature Model",
                description="A feature model for testing purposes",
                publication_type=PublicationType.DATA_MANAGEMENT_PLAN.name,
                publication_doi="",
                tags="test,feature,model",
                uvl_version="1.0"
            )
            db.session.add(fm_metadata)
            db.session.commit()

            # Crear un FeatureModel relacionado con un DataSet
            feature_model = FeatureModel(
                data_set_id=dataset.id,
                fm_meta_data_id=fm_metadata.id
            )
            db.session.add(feature_model)
            db.session.commit()
            # Crear el archivo temporal en la ruta esperada
            temp_folder = os.path.join('uploads', 'temp', str(user.id))
            os.makedirs(temp_folder, exist_ok=True)
            with open(os.path.join(temp_folder, 'file9.uvl'), 'w') as f:
                f.write('Temporary file content')
            yield client

            # Limpiar el archivo temporal después de la prueba
            if os.path.exists(os.path.join(temp_folder, 'file9.uvl')):
                os.remove(os.path.join(temp_folder, 'file9.uvl'))
            if os.path.exists(temp_folder):
                os.rmdir(temp_folder)

            db.session.remove()
            db.drop_all()


def test_create_dataset(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    # Datos de ejemplo para el formulario
    form_data = {
        "title": "test",
        "desc": "test",
        "publication_type": "none",
        "publication_doi": "",
        "dataset_doi": "",
        "tags": "",
        "authors-0-name": "Author Name",
        "authors-0-affiliation": "Author Affiliation",
        "authors-0-orcid": "0000-0001-2345-6789",
        "feature_models-0-uvl_filename": "file9.uvl",
        "feature_models-0-title": "Feature Model Title",
        "feature_models-0-desc": "Feature Model Description",
        "feature_models-0-publication_type": "none",
        "feature_models-0-publication_doi": "",
        "feature_models-0-tags": "",
        "feature_models-0-version": "1.0",
        "feature_models-0-authors-0-name": "FM Author Name",
        "feature_models-0-authors-0-affiliation": "FM Author Affiliation",
        "feature_models-0-authors-0-orcid": "0000-0002-3456-7890"
    }

    # Enviar la solicitud POST con los datos del formulario
    response = client.post('/dataset/create', data=form_data)

    # Verificar la respuesta
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    data = response.get_json()
    assert data["message"] == "Everything works!", f"Expected message 'Everything works!', but got {data['message']}"
    logout(client)
    
    
def test_upload_dataset_zenodo(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Datos de ejemplo para crear el dataset
    form_data = {
        "title": "test dataset in zenodo",
        "desc": "test description",
        "publication_type": "none",
        "publication_doi": "",
        "dataset_doi": "",
        "tags": "",
        "authors-0-name": "Author Name",
        "authors-0-affiliation": "Author Affiliation",
        "authors-0-orcid": "0000-0001-2345-6789",
        "feature_models-0-uvl_filename": "file9.uvl",
        "feature_models-0-title": "Feature Model Title",
        "feature_models-0-desc": "Feature Model Description",
        "feature_models-0-publication_type": "none",
        "feature_models-0-publication_doi": "",
        "feature_models-0-tags": "",
        "feature_models-0-version": "1.0",
        "feature_models-0-authors-0-name": "FM Author Name",
        "feature_models-0-authors-0-affiliation": "FM Author Affiliation",
        "feature_models-0-authors-0-orcid": "0000-0002-3456-7890"
    }

    # Enviar la solicitud POST con los datos del formulario para crear el dataset
    response = client.post('/dataset/upload', data=form_data)
    assert response.status_code == (200 or 403), f"Expected status code 200 or 403, but got {response.status_code}"

    # Verificar que el dataset se haya creado correctamente
    dataset = DataSet.query.join(DSMetaData).filter(DSMetaData.title == "test dataset in zenodo").first()
    assert dataset is not None, "Dataset was not created"

    # Hacer una solicitud GET a la ruta /dataset/list para verificar que el dataset se encuentra en el listado de datasets
    response = client.get('/dataset/list')
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    # Verificar que el dataset se encuentra en el listado de datasets
    html_data = response.data.decode('utf-8')
    assert "test dataset in zenodo" in html_data, "The created dataset is not in the list of datasets"

    logout(client)


def test_create_and_list_unprepared_dataset(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    
    # Datos de ejemplo para el formulario
    form_data = {
        "title": "test",
        "desc": "test",
        "publication_type": "none",
        "publication_doi": "",
        "dataset_doi": "",
        "tags": "",
        "authors-0-name": "Author Name",
        "authors-0-affiliation": "Author Affiliation",
        "authors-0-orcid": "0000-0001-2345-6789",
        "feature_models-0-uvl_filename": "file9.uvl",
        "feature_models-0-title": "Feature Model Title",
        "feature_models-0-desc": "Feature Model Description",
        "feature_models-0-publication_type": "none",
        "feature_models-0-publication_doi": "",
        "feature_models-0-tags": "",
        "feature_models-0-version": "1.0",
        "feature_models-0-authors-0-name": "FM Author Name",
        "feature_models-0-authors-0-affiliation": "FM Author Affiliation",
        "feature_models-0-authors-0-orcid": "0000-0002-3456-7890"
    }

    # Enviar la solicitud POST con los datos del formulario para crear el dataset
    response = client.post('/dataset/create', data=form_data)
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    data = response.get_json()
    assert data["message"] == "Everything works!", f"Expected message 'Everything works!', but got {data['message']}"

    # Hacer una solicitud GET a la ruta /dataset/list para obtener la lista de datasets
    response = client.get('/dataset/list')
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    # Verificar que el dataset esta en el listado de datasets
    html_data = response.data.decode('utf-8')
    assert "test" in html_data, "The created dataset is not in the unprepared_datasets"

    logout(client)


def test_update_staging_area_dataset(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Obtener el ID del dataset creado en la fixture
    dataset = DataSet.query.join(DSMetaData).filter(DSMetaData.title == "Staging area Dataset").first()
    assert dataset is not None, "Dataset with title 'Staging area Dataset' not found"
    dataset_id = dataset.id

    # Hacer una solicitud GET a la ruta /dataset/staging-area/<int:dataset_id> para obtener el formulario de actualización
    response = client.get(f'/dataset/staging-area/{dataset_id}')
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    # Datos de ejemplo para actualizar el dataset
    form_data_update = {
        "title": "updated unique dataset",
        "desc": "updated description",
        "publication_type": "none",
        "publication_doi": "",
        "dataset_doi": "",
        "tags": "",
        "authors-0-name": "Updated Author Name",
        "authors-0-affiliation": "Updated Author Affiliation",
        "authors-0-orcid": "0000-0001-2345-6789",
        "feature_models-0-uvl_filename": "file9.uvl",
        "feature_models-0-title": "Updated Feature Model Title",
        "feature_models-0-desc": "Updated Feature Model Description",
        "feature_models-0-publication_type": "none",
        "feature_models-0-publication_doi": "",
        "feature_models-0-tags": "",
        "feature_models-0-version": "1.0",
        "feature_models-0-authors-0-name": "Updated FM Author Name",
        "feature_models-0-authors-0-affiliation": "Updated FM Author Affiliation",
        "feature_models-0-authors-0-orcid": "0000-0002-3456-7890"
    }

    # Enviar la solicitud POST con los datos del formulario para actualizar el dataset
    response = client.post(f'/dataset/staging-area/{dataset_id}', data=form_data_update)
    assert response.status_code == 302, f"Expected status code 302, but got {response.status_code}"

    # Verificar que las propiedades del dataset se hayan actualizado correctamente
    updated_dataset = DataSet.query.get(dataset_id)
    assert updated_dataset.ds_meta_data.title == "updated unique dataset", f"Expected title 'updated unique dataset', but got {updated_dataset.ds_meta_data.title}"
    assert updated_dataset.ds_meta_data.description == "updated description", f"Expected description 'updated description', but got {updated_dataset.ds_meta_data.description}"
    assert updated_dataset.ds_meta_data.authors[0].name == "TestSurname, TestName", f"Expected author name 'TestSurname, TestName', but got {updated_dataset.ds_meta_data.authors[0].name}"
    assert updated_dataset.ds_meta_data.authors[1].name == "Updated Author Name", f"Expected author name 'Updated Author Name', but got {updated_dataset.ds_meta_data.authors[0].name}"

    logout(client)
    
    
def test_upload_dataset_zenodo_from_staging(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    dataset = DataSet.query.join(DSMetaData).filter(DSMetaData.title == "Staging area Dataset").first()
    assert dataset is not None, "Dataset with title 'Staging area Dataset' not found"
    dataset_id = dataset.id

    # Datos de ejemplo para actualizar el dataset
    form_data_update = {
        "title": "updated unique dataset",
        "desc": "updated description",
        "publication_type": "none",
        "publication_doi": "",
        "dataset_doi": "",
        "tags": "",
        "authors-0-name": "Updated Author Name",
        "authors-0-affiliation": "Updated Author Affiliation",
        "authors-0-orcid": "0000-0001-2345-6789",
        "feature_models-0-uvl_filename": "file9.uvl",
        "feature_models-0-title": "Updated Feature Model Title",
        "feature_models-0-desc": "Updated Feature Model Description",
        "feature_models-0-publication_type": "none",
        "feature_models-0-publication_doi": "",
        "feature_models-0-tags": "",
        "feature_models-0-version": "1.0",
        "feature_models-0-authors-0-name": "Updated FM Author Name",
        "feature_models-0-authors-0-affiliation": "Updated FM Author Affiliation",
        "feature_models-0-authors-0-orcid": "0000-0002-3456-7890",
        "csrf_token": "ImM4Y2YwNzA1NGYxNGZhMDlhMjE3ZjQ4NDRjMTVkNTc5ZmY5ZWQwMjQi.Z0tv3Q.IA3Me8feSsE3T5juVZT6k9StAj4"
    }

    # Enviar la solicitud POST con los datos del formulario para actualizar el dataset
    response = client.post(f'/dataset/upload/{dataset_id}', data=form_data_update)
    
    # Espera 200 en caso de que se suba satisfactoramente a zenodo o 403 en caso de que zenodo rechace la conexion
    assert response.status_code == (200 or 403), f"Expected status code 200 or 403, but got {response.status_code}"
    
    # Se espera que tenga el valor de False en staging_area
    assert dataset.ds_meta_data.staging_area == False, f"Expected staging_area False, but got {dataset.staging_area}"

    # Hacer una solicitud GET a la ruta /dataset/list para verificar que el dataset se encuentra en la sección local_datasets
    response = client.get('/dataset/list')
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    # Verificar que el dataset esta en el listado de datasets
    html_data = response.data.decode('utf-8')
    assert "updated unique dataset" in html_data, "The updated dataset is not in the local_datasets"

    logout(client)


def test_rate_dataset(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    # Enviar una calificación para un dataset específico
    rating_data = {'rating': 4}
    print("Enviando request con data:", rating_data)
    response = client.post('/datasets/10/rate', json=rating_data)
    # Verificar y ver la respuesta del post
    print("Status code de la respuesta:", response.status_code)
    print("Contenido de la respuesta JSON:", response.get_json())
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Rating added'
    assert data['rating']['rating'] == 4

    logout(client)


# def test_rate_dataset_invalid_data(client):
#     login_response = login(client, "user5@example.com", "1234")
#     assert login_response.status_code == 200, "Login was unsuccessful."

#     response = client.post('/datasets/10/rate', json={})

#     # Verificar que el servidor responde con error al faltar el rating
#     assert response.status_code == 400
#     data = response.get_json()
#     assert 'error' in data

#     logout(client)


def test_get_dataset_average_rating(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    client.post('/datasets/10/rate', json={'rating': 4})
    logout(client)

    login_response = login(client, "user6@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    client.post('/datasets/10/rate', json={'rating': 5})

    # Obtener la calificación promedio
    response = client.get('/datasets/10/average-rating')
    assert response.status_code == 200
    data = response.get_json()
    assert 'average_rating' in data
    assert data['average_rating'] == 4.5

    logout(client)


def test_create_empty_dataset(client):
    # Iniciar sesión como el usuario de prueba
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    
    feature_model_id = 1
    response = client.post(f"/dataset/build_empty/{feature_model_id}")
    
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    data = response.get_json()
    assert "message" in data, "Response JSON does not contain 'message'"
    assert data["message"] == "Empty dataset created successfully and UVL file added."
    assert "dataset_id" in data, "Response JSON does not contain 'dataset_id'"
    
    dataset = DataSet.query.get(data["dataset_id"])
    assert dataset is not None, "Dataset was not created in the database."
    
    logout(client)


def test_create_empty_dataset_with_invalid_id(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    
    invalid_feature_model_id = 999  
    response = client.post(f"/dataset/build_empty/{invalid_feature_model_id}")
    
    assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"
    data = response.get_json()
    assert "error" in data, "Response JSON does not contain 'error'"
    assert data["error"] == "Exception while processing dataset"
    
    logout(client)
