import pytest
import os
from enum import Enum
from app import create_app, db
from app.modules.conftest import login, logout
from app.modules.dataset.models import DataSet, DSMetaData, DSRating
from app.modules.profile.models import UserProfile
from app.modules.featuremodel.models import FMMetaData, FeatureModel, FeatureModelRating
from app.modules.hubfile.models import Hubfile
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
            profile = UserProfile(
                user_id=user.id,
                surname="TestSurname",
                name="TestName",
                affiliation="TestAffiliation",
                orcid="0000-0001-2345-6789")
            db.session.add(profile)
            db.session.commit()
            dsmetadata = DSMetaData(
                id=10,
                title="Sample Dataset 11",
                rating=0,
                description="Description for dataset 11",
                publication_type=PublicationType.DATA_MANAGEMENT_PLAN.name,
                staging_area=False)
            db.session.add(dsmetadata)
            dataset = DataSet(id=10, user_id=user.id, ds_meta_data_id=dsmetadata.id)
            db.session.add(dataset)
            db.session.commit()
            dsrating = DSRating(
                id=10,
                user_id=user.id,
                ds_meta_data_id=dsmetadata.id,
                rating=dsmetadata.rating,
                rated_date=datetime(2022, 3, 13))
            db.session.add(dsrating)
            db.session.commit()
            # Crear un dataset en el staging area
            dsmetadata_sa = DSMetaData(
                id=11,
                title="Staging area Dataset",
                description="Description for unique dataset",
                publication_type=PublicationType.DATA_MANAGEMENT_PLAN.name)
            db.session.add(dsmetadata_sa)
            dataset_staging_area = DataSet(id=11, user_id=user.id, ds_meta_data_id=dsmetadata_sa.id)
            db.session.add(dataset_staging_area)
            db.session.commit()
            user1 = User(id=6, email="user6@example.com", password="1234", created_at=datetime(2022, 3, 13))
            db.session.add(user1)
            db.session.commit()
            fm_metadata = FMMetaData(
                id=11,
                uvl_filename="test_model.uvl",
                title="Test Feature Model",
                rating=0,
                description="A feature model for testing purposes",
                publication_type=PublicationType.DATA_MANAGEMENT_PLAN.name,
                publication_doi="",
                tags="test,feature,model",
                uvl_version="1.0"
            )
            db.session.add(fm_metadata)
            db.session.commit()
            fmrating = FeatureModelRating(
                id=11,
                user_id=user.id,
                fm_meta_data_id=fm_metadata.id,
                rating=fm_metadata.rating,
                rated_date=datetime(2022, 3, 13))
            db.session.add(fmrating)
            db.session.commit()

            # Crear un FeatureModel relacionado con un DataSet
            feature_model = FeatureModel(
                id=11,
                data_set_id=dataset.id,
                fm_meta_data_id=fm_metadata.id
            )
            db.session.add(feature_model)
            db.session.commit()

            hubfile = Hubfile(
                id=15,
                name="file9.uvl",
                checksum="checksum1",
                size=128,
                feature_model_id=feature_model.id
            )

            db.session.add(hubfile)
            db.session.commit()

            # Crear el archivo temporal en la ruta esperada
            temp_folder = os.path.join('uploads', 'temp', str(user.id))
            os.makedirs(temp_folder, exist_ok=True)
            with open(os.path.join(temp_folder, 'file9.uvl'), 'w') as f:
                f.write('Temporary file content')

            # Crear las carpetas temporales asociadas a los datasets
            temp_folder2 = os.path.join('uploads', f'user_{user.id}', 'dataset_10')
            os.makedirs(temp_folder2, exist_ok=True)

            with open(os.path.join(temp_folder2, 'file9.uvl'), 'w') as f:
                f.write('Temporary file content')

            temp_folder3 = os.path.join('uploads', f'user_{user.id}', 'dataset_11')
            os.makedirs(temp_folder3, exist_ok=True)

            with open(os.path.join(temp_folder3, 'file9.uvl'), 'w') as f:
                f.write('Temporary file content')

            yield client
            # Limpiar el archivo temporal después de la prueba
            if os.path.exists(os.path.join(temp_folder, 'file9.uvl')):
                os.remove(os.path.join(temp_folder, 'file9.uvl'))
            if os.path.exists(temp_folder):
                os.rmdir(temp_folder)
            if os.path.exists(os.path.join(temp_folder2, 'file9.uvl')):
                os.remove(os.path.join(temp_folder2, 'file9.uvl'))
            if os.path.exists(temp_folder2):
                os.rmdir(temp_folder2)

            db.session.remove()
            db.drop_all()


def test_get_featuremodel_average_rating_no_ratings(client):
    """Prueba obtener el promedio de un dataset sin ratings."""
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = client.get('/feature-models/11/average-rating')

    assert response.status_code == 200, "El código de estado debería ser 200 incluso si no hay calificaciones."
    data = response.get_json()
    assert 'average_rating' in data, "La respuesta debería contener average_rating."
    assert data['average_rating'] == 0, "El promedio debería ser 0 si no hay calificaciones."

    logout(client)


def test_rate_featuremodel(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    # Enviar una calificación para un dataset específico
    rating_data = {'rating': 4}
    print("Enviando request con data:", rating_data)
    response = client.post('/feature-models/11/rate', json=rating_data)
    # Verificar y ver la respuesta del post
    print("Status code de la respuesta:", response.status_code)
    print("Contenido de la respuesta JSON:", response.get_json())
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Rating added'
    assert data['rating']['rating'] == 4

    logout(client)


def test_rate_featuremodel_invalid_rating(client):
    """Prueba enviar un rating inválido."""
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    invalid_rating_data = {'rating': 6}
    response = client.post('/feature-models/11/rate', json=invalid_rating_data)

    assert response.status_code == 400, "El código de estado debería ser 400 para un rating inválido."
    data = response.get_json()
    assert 'error' in data, "La respuesta debería contener un mensaje de error."

    logout(client)


def test_get_featuremodel_average_rating_invalid_dataset(client):
    """Prueba obtener el promedio para un dataset no existente."""
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = client.get('/feature-models/999/average-rating')
    print(response.status_code)
    print(response.get_json())

    assert response.status_code == 404, "El código de estado debería ser 404 para un dataset inexistente."

    logout(client)


def test_rate_featuremodel_unauthorized(client):
    """Prueba enviar un rating sin estar autenticado."""
    rating_data = {'rating': 4}
    response = client.post('/feature-models/11/rate', json=rating_data)

    assert response.status_code == 302, "El código de estado debería ser 302 para usuarios no autenticados."


def test_get_featuremodel_average_rating(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    client.post('/feature-models/11/rate', json={'rating': 4})
    logout(client)

    login_response = login(client, "user6@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."
    client.post('/feature-models/11/rate', json={'rating': 5})

    response = client.get('/feature-models/11/average-rating')
    assert response.status_code == 200
    data = response.get_json()
    assert 'average_rating' in data
    assert data['average_rating'] == 4.5

    logout(client)
