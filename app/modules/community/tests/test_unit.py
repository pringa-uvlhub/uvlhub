import pytest
from app import create_app, db
from app.modules.community.models import Community
from app.modules.conftest import login
from app.modules.profile.models import UserProfile
from app.modules.auth.models import User
from datetime import datetime


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
            user = User(id=6, email="user6@example.com", password="1234", created_at=datetime(2022, 3, 13))
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
            community = Community(
                id=1,
                name="For Test",
                description="For Test descripction",
                created_at=datetime(2022, 3, 13),
                created_by_id=5,
                admin_by_id=5)
            db.session.add(community)
            db.session.commit()
            yield client


def test_create_community(client):
    # Simular el login
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Datos de ejemplo para el formulario de la comunidad
    form_data = {
        "name": "Test Community",
        "description": "A community for testing purposes",
    }

    # Enviar la solicitud POST con los datos del formulario
    response = client.post("/community/create", data=form_data)

    # Verificar la respuesta
    assert response.status_code == 302, f"Expected status code 302, but got {response.status_code}"


def test_create_community_empty_form(client):
    # Simular el login
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Datos de ejemplo para el formulario de la comunidad
    form_data = {
        "name": "",
        "description": "",
    }

    # Enviar la solicitud POST con los datos del formulario
    response = client.post("/community/create", data=form_data)

    # Verificar la respuesta
    assert response.status_code == 400, f"Expected status code 400, but got {response.status_code}"


def test_show_community(client):
    response = client.get('/community/1')

    # Verificar el código de respuesta
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"


def test_show_community_not_exist(client):
    response = client.get('/community/10')

    # Verificar el código de respuesta
    assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"


def test_delete_community(client):
    # Simular el login como administrador de la comunidad
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Intentar eliminar una comunidad existente y ser el admin
    response = client.post('/community/1/delete', follow_redirects=True)

    # Verificar que la comunidad se ha eliminado correctamente (redirección a la lista de comunidades)
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"

    # Verificar que la comunidad ha sido eliminada de la base de datos
    community = Community.query.get(1)
    assert community is None, "Community was not deleted from the database"


def test_delete_community_not_exist(client):
    # Simular el login como administrador de la comunidad
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Intentar eliminar una comunidad que no existe
    response = client.post('/community/999/delete', follow_redirects=True)

    # Verificar que la respuesta es la esperada (mensaje de comunidad no encontrada)
    assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"


def test_delete_community_not_authorized(client):
    # Simular el login como un usuario no administrador
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Crear una nueva comunidad asignada a un administrador distinto para simular que no tenemos permisos
    community = Community(
        id=2,
        name="Another Community",
        description="Community for testing permission",
        created_at=datetime(2022, 3, 13),
        created_by_id=5,
        admin_by_id=6)
    db.session.add(community)
    db.session.commit()

    # Intentar eliminar una comunidad de la que no somos administradores
    response = client.post('/community/2/delete', follow_redirects=True)

    # Verificar que la respuesta es la esperada (mensaje de no autorizado)
    assert response.status_code == 403, f"Expected status code 403, but got {response.status_code}"


def test_join_community(client):
    # Simular el login como usuario de prueba
    login_response = login(client, "user6@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Unirse a una comunidad
    response = client.post('/community/1/join', follow_redirects=True)
    # Verificar que la respuesta sea un redireccionamiento
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"


def test_list_members(client):
    response = client.get('/community/1/members')

    # Verificar el código de respuesta
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"


def test_list_members_community_not_exist(client):
    response = client.get('/community/99/members')

    # Verificar el código de respuesta
    assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"


def test_edit_community(client):
    # Simular el login como el administrador de la comunidad
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Datos de formulario para editar la comunidad
    form_data = {
        "name": "Updated Test Community",
        "description": "Updated community description",
    }

    # Enviar la solicitud POST con los datos del formulario
    response = client.post('/community/1/edit', data=form_data)

    # Verificar que la comunidad fue actualizada correctamente (redirección)
    assert response.status_code == 302, f"Expected status code 302, but got {response.status_code}"


def test_edit_community_not_authorized(client):
    # Simular el login como un usuario no autorizado (no administrador)
    login_response = login(client, "user6@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Intentar editar la comunidad a la que no pertenecemos como administrador
    form_data = {
        "name": "Updated Test Community",
        "description": "Updated community description",
    }
    response = client.post('/community/1/edit', data=form_data)

    # Verificar que el usuario recibe un mensaje de no autorizado
    assert response.status_code == 403, f"Expected status code 403, but got {response.status_code}"


def test_edit_community_not_found(client):
    # Simular el login como administrador de una comunidad
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Intentar editar una comunidad que no existe
    form_data = {
        "name": "Updated Test Community",
        "description": "Updated community description",
    }
    response = client.post('/community/999/edit', data=form_data)

    # Verificar que la comunidad no existe
    assert response.status_code == 404, f"Expected status code 404, but got {response.status_code}"
