from flask_login import login_user
import pytest
from flask import url_for
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile
from app.modules.auth.services import AuthenticationService
from app.modules.auth.repositories import UserRepository
from app.modules.profile.repositories import UserProfileRepository
from app import create_app, db
from datetime import datetime


@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            # Configuración de la base de datos en modo de prueba
            db.drop_all()
            db.create_all()

            user = User(id=1, email="user1@example.com", password="1234", created_at=datetime(2022, 3, 13))
            db.session.add(user)
            db.session.commit()

            profile = UserProfile(user_id=user.id, surname="TestSurname", name="TestName", affiliation="TestAffiliation", orcid="0000-0000-0000-0001")
            db.session.add(profile)
            db.session.commit()

            yield client

            db.session.remove()
            db.drop_all()


def test_login_success(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path != url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_email(test_client):
    response = test_client.post(
        "/login", data=dict(email="bademail@example.com", password="test1234"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_login_unsuccessful_bad_password(test_client):
    response = test_client.post(
        "/login", data=dict(email="test@example.com", password="basspassword"), follow_redirects=True
    )

    assert response.request.path == url_for("auth.login"), "Login was unsuccessful"

    test_client.get("/logout", follow_redirects=True)


def test_signup_user_no_name(test_client):
    response = test_client.post(
        "/signup", data=dict(surname="Foo", email="test@example.com", password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert b"This field is required" in response.data, response.data


def test_signup_user_unsuccessful(test_client):
    email = "test@example.com"
    response = test_client.post(
        "/signup", data=dict(name="Test", surname="Foo", email=email, password="test1234"), follow_redirects=True
    )
    assert response.request.path == url_for("auth.show_signup_form"), "Signup was unsuccessful"
    assert f"Email {email} in use".encode("utf-8") in response.data


def test_signup_user_successful(test_client):
    response = test_client.post(
        "/signup",
        data=dict(name="Foo", surname="Example", email="foo@example.com", password="foo1234"),
        follow_redirects=True,
    )
    assert response.request.path == url_for("public.index"), "Signup was unsuccessful"


def test_service_create_with_profie_success(clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "service_test@example.com",
        "password": "test1234"
    }

    AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 1
    assert UserProfileRepository().count() == 1


def test_service_create_with_profile_fail_no_email(clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "",
        "password": "1234"
    }

    with pytest.raises(ValueError, match="Email is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_service_create_with_profile_fail_no_password(clean_database):
    data = {
        "name": "Test",
        "surname": "Foo",
        "email": "test@example.com",
        "password": ""
    }

    with pytest.raises(ValueError, match="Password is required."):
        AuthenticationService().create_with_profile(**data)

    assert UserRepository().count() == 0
    assert UserProfileRepository().count() == 0


def test_forgot_password_authenticated(test_client):
    user = User(email='test@example.com')
    user.set_password('password')
    login_user(user)

    response = test_client.get(url_for('auth.forgot_password'))

    assert response.status_code == 302
    assert response.location == url_for('public.index', _external=False)


def test_forgot_password_get(test_client):
    test_client.get(url_for('auth.logout'))

    response = test_client.get(url_for('auth.forgot_password'))
    assert response.status_code == 200


def test_forgot_password_post_invalid_form(test_client):
    test_client.get(url_for('auth.logout'))
    response = test_client.post(url_for('auth.forgot_password'), data={})

    assert response.status_code == 200


def test_forgot_password_post_email_not_exist(test_client):
    test_client.get(url_for('auth.logout'))

    response = test_client.post(url_for('auth.forgot_password'), data={'email': 'nonexistent@example.com'})

    assert response.status_code == 302
    assert response.location == url_for('auth.forgot_password')


def test_forgot_password_post_email_exist(test_client):
    test_client.post(
        "/signup",
        data=dict(name="Foo", surname="Example", email="test@example.com", password="foo1234"),
        follow_redirects=True,
    )

    response = test_client.post(url_for('auth.forgot_password'), data={'email': 'test@example.com'})

    assert response.status_code == 302


def test_reset_password_authenticated(test_client):
    user = User(email="test@example.com")
    user.set_password("password")
    login_user(user)

    response = test_client.get(url_for("auth.reset_password", token="some_token"))

    assert response.status_code == 302
    assert response.location == url_for("public.index", _external=False)


def test_reset_password_invalid_or_expired_token(test_client):
    test_client.get(url_for('auth.logout'))

    invalid_token = "invalid_or_expired_token"

    response = test_client.get(url_for("auth.reset_password", token=invalid_token))

    assert response.status_code == 302
    assert response.location == url_for("auth.forgot_password", _external=False)

    with test_client.session_transaction() as session:
        assert '_flashes' in session
        flashes = session['_flashes']
        assert any("El enlace de restablecimiento es inválido o ha expirado." in flash[1] for flash in flashes)


def test_reset_password_valid_token_invalid_form(test_client):
    response = test_client.post(
        "/login", data=dict(email="user1@example.com", password="test1234"), follow_redirects=True
    )

    user = UserRepository().get_by_email("user1@example.com")

    valid_token = User.generate_reset_token(user)
    test_client.get("/logout", follow_redirects=True)
    response = test_client.get(url_for("auth.reset_password", token=valid_token))

    assert response.status_code == 200
    response = test_client.post(url_for("auth.reset_password", token=valid_token), data={})
    assert response.status_code == 200


def test_reset_password_valid_token_valid_form(test_client):
    response = test_client.post(
        "/login", data=dict(email="user1@example.com", password="1234"), follow_redirects=True
    )

    user = UserRepository().get_by_email("user1@example.com")

    valid_token = User.generate_reset_token(user)
    test_client.get("/logout", follow_redirects=True)
    user = User.query.filter_by(email="user1@example.com").first()

    response = test_client.get(url_for("auth.reset_password", token=valid_token))
    assert response.status_code == 200

    response = test_client.post(
        url_for("auth.reset_password", token=valid_token),
        data={"password": "newpassword123", "confirm_password": "newpassword123"}
    )

    assert response.status_code == 302
    assert response.location == url_for("auth.login", _external=False)
    user = User.query.filter_by(email="user1@example.com").first()
    assert user.check_password("newpassword123")
