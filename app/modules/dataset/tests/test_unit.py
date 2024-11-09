import json
import pytest
from enum import Enum
from app import create_app, db
from app.modules.dataset.models import DataSet, DSMetaData, DSRating
# from app.modules.profile.models import UserProfile
from app.modules.auth.models import User
from sqlalchemy import Enum as SQLAlchemyEnum


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
            db.create_all()
            user = User(id=3, email="user3@example.com", password="1234", created_at=13/3/2022)
            # userprofile = UserProfile(id=10, user_id=user.id, name="Test", surname="User")
            db.session.add(user)
            db.session.commit()
            dsmetadata = DSMetaData(id=10, title="Sample Dataset 10", rating=0, description="Description for dataset 10",
                                    publication_type=SQLAlchemyEnum(PublicationType.DATA_MANAGEMENT_PLAN.value))
            db.session.add(dsmetadata)
            dataset = DataSet(id=10, user_id=user.id, ds_meta_data_id=1)
            db.session.add(dataset)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()


def test_rate_dataset(client):
    # Enviar una calificación para un dataset específico
    response = client.post('/datasets/1/rate', json={'rating': 4})

    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Rating added'
    assert data['rating'] == 4


def test_rate_dataset_invalid_data(client):
    response = client.post('/datasets/1/rate', json={})

    # Verificar que el servidor responde con error al faltar el rating
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_get_dataset_average_rating(client):
    client.post('/datasets/1/rate', json={'rating': 4})
    client.post('/datasets/1/rate', json={'rating': 5})

    # Obtener la calificación promedio
    response = client.get('/datasets/1/average-rating')
    assert response.status_code == 200
    data = response.get_json()
    assert 'average_rating' in data
    assert data['average_rating'] == 4.5


# @pytest.fixture
# def client():
#     app = create_app('testing')  # Configuración para el entorno de pruebas
#     with app.test_client() as client:
#         with app.app_context():
#             db.create_all()
#             user = User(id=1001, email="user1001@example.com", password="1234", created_at=13/3/2022)
#             # userprofile = UserProfile(id=10, user_id=user.id, name="Test", surname="User")
#             db.session.add(user)
#             db.session.commit()
#             # dsmetadata = DSMetaData(id=10, title="Sample Dataset 10", description="Description for dataset 10",
#             #                         publication_type=PublicationType.DATA_MANAGEMENT_PLAN)
#             # db.session.add(dsmetadata)
#             # db.session.commit()
#             dataset = DataSet(id=10, user_id=user.id, ds_meta_data_id=1)
#             db.session.add(dataset)
#             db.session.commit()
#         yield client
#         db.session.remove()
#         db.drop_all()


# def test_rate_dataset(client):
#     """Prueba la creación de una nueva calificación para un dataset."""
#     # Calificación de prueba
#     rating_data = {"rating": 4}

#     # Enviar solicitud POST al endpoint de calificación
#     response = client.post(
#         '/dataset',
#     )

#     # Verificar respuesta
#     assert response.status_code == 200
#     response_data = response.get_json()
#     assert response_data['message'] == "Rating added successfully"

#     # Verificar que la calificación se haya almacenado en la base de datos
#     rating = DSRating.query.filter_by(dataset_id=1).first()
#     assert rating is not None
#     assert rating.value == 4


# def test_get_average_rating(client):
#     """Prueba obtener el promedio de calificación de un dataset."""
#     # Agregar calificaciones de ejemplo en la base de datos
#     db.session.add(DSRating(dataset_id=1, value=5))
#     db.session.add(DSRating(dataset_id=1, value=3))
#     db.session.commit()

#     # Enviar solicitud GET al endpoint de promedio de calificación
#     response = client.get(url_for('dataset.get_average_rating', id=1))

#     # Verificar respuesta
#     assert response.status_code == 200
#     response_data = response.get_json()
#     assert 'average_rating' in response_data
#     assert response_data['average_rating'] == 4.0  # Promedio esperado: (5 + 3) / 2
