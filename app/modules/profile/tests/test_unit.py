import pytest

from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    for module testing (por example, new users)
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

        user_test2 = User(email='2user@example.com', password='test1234')
        db.session.add(user_test2)
        db.session.commit()

        profile2 = UserProfile(user_id=user_test2.id, name="Name2", surname="Surname2")
        db.session.add(profile2)
        db.session.commit()

    yield test_client


def test_edit_profile_page_get(test_client):
    """
    Tests access to the profile editing page via a GET request.
    """
    login(test_client, "user@example.com", "test1234")

    response = test_client.get("/profile/edit")
    assert response.status_code == 200, "The profile editing page could not be accessed."

    logout(test_client)


def test_user_profile_own_profile(test_client):
    """
    Verifica que el usuario logueado sea redirigido a /profile/summary al intentar acceder a su propio perfil.
    """
    login(test_client, "user@example.com", "test1234")

    user = User.query.filter_by(email="user@example.com").first()
    response = test_client.get(f"/profile/{user.id}")
    assert response.status_code == 302, "Redirection did not occur as expected."

    logout(test_client)


def test_user_profile_nonexistent_user(test_client):
    """
    Verifica que al intentar acceder a un perfil inexistente se redirija a la página principal.
    """
    login(test_client, "user@example.com", "test1234")
    response = test_client.get("/profile/9999")
    assert response.status_code == 404, "Expected 404 for nonexistent user profile."

    logout(test_client)
