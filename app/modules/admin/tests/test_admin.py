import pytest
# import os
import uuid
from enum import Enum
from bs4 import BeautifulSoup
from app import create_app, db
from app.modules.conftest import login, logout
from app.modules.dataset.models import DSDownloadRecord
from app.modules.dataset.models import DataSet, DSMetaData
# from app.modules.profile.models import UserProfile
# from app.modules.hubfile.models import Hubfile
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
            db.drop_all()
            db.create_all()
            admin = User(id=9,
                         email="adminprueba@example.com",
                         password="password",
                         is_admin=True,
                         created_at=datetime.now())
            db.session.add(admin)
            db.session.commit()
            user_test = User(id=10,
                             email="usertest@example.com",
                             password="password",
                             is_admin=False,
                             created_at=datetime.now())
            db.session.add(user_test)
            db.session.commit()
            dsmetadata_test = DSMetaData(
                id=15,
                title="Sample Dataset Test 15",
                rating=0,
                description="This is a test dataset",
                publication_type=PublicationType.DATA_MANAGEMENT_PLAN.name,
                staging_area=False,
            )
            db.session.add(dsmetadata_test)
            db.session.commit()
            yield client


def test_admin_dashboard_no_data(client):
    login_response = login(client, "adminprueba@example.com", "password")
    assert login_response.status_code == 200, "Login successful"
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/no_data' in response.location

    logout(client)


def test_admin_dashboard_with_data(client):
    login_response = login(client, "adminprueba@example.com", "password")
    assert login_response.status_code == 200, "Login successful"
    with client.application.app_context():
        admin = User.query.filter_by(email="adminprueba@example.com").first()
        dsmetadata = DSMetaData(
            id=10,
            title="Sample Dataset 11",
            rating=0,
            description="Description for dataset 11",
            publication_type=PublicationType.DATA_MANAGEMENT_PLAN.name,
            staging_area=False)
        db.session.add(dsmetadata)
        dataset = DataSet(id=10, user_id=admin.id, ds_meta_data_id=dsmetadata.id)
        db.session.add(dataset)
        db.session.commit()
        # Simular la descarga del dataset por parte de un usuario
        download = DSDownloadRecord(
            dataset_id=dataset.id,
            user_id=admin.id,  # ID del usuario admin creado en init_database
            download_date=datetime.now(),
            download_cookie=str(uuid.uuid4())
        )
        db.session.add(download)
        db.session.commit()

    response = client.get('/dashboard')
    if response.status_code == 302:
        # Seguir la redirección
        response = client.get(response.headers['Location'])
    assert response.status_code == 200
    assert b'Dashboard' in response.data

    logout(client)


def test_no_data_page(client):
    login_response = login(client, "adminprueba@example.com", "password")
    assert login_response.status_code == 200, "Login successful"
    response = client.get('/no_data')
    assert response.status_code == 200
    assert b'No Data Available' in response.data
    logout(client)


def test_bottom_go_to_home(client):
    login_response = login(client, "adminprueba@example.com", "password")
    assert login_response.status_code == 200, "Login successful"

    response = client.get('/no_data')
    assert response.status_code == 200

    # Analizar el HTML de la respuesta
    soup = BeautifulSoup(response.data, 'html.parser')
    go_home_button = soup.find('a', text='Go Back to Home')

    assert go_home_button is not None, "Go Home button not found"

    # Obtener la URL del botón
    go_home_url = go_home_button['href']

    # Realizar una solicitud GET a la URL obtenida
    response = client.get(go_home_url)
    assert response.status_code == 200


def test_dashboard_not_accesible(client):
    login_response = login(client, "usertest@example.com", "1234")
    assert login_response.status_code == 200, "Login successful"

    response = client.get('/dashboard')
    print(response.data.decode('utf-8'))

    # Verificar que el contenido de la respuesta contiene el mensaje de error
    assert "<h1>Redirecting...</h1>" in response.data.decode('utf-8'), "Expected '<h1>Redirecting...</h1>' not found"
    logout(client)
