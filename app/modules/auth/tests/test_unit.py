import pytest
from flask import url_for

from app.modules.auth.services import AuthenticationService
from app.modules.auth.repositories import UserRepository
from app.modules.profile.repositories import UserProfileRepository
from unittest.mock import patch


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Add HERE new elements to the database that you want to exist in the test context.
        # DO NOT FORGET to use db.session.add(<element>) and db.session.commit() to save the data.
        pass

    yield test_client


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
    assert response.request.path == url_for("auth.confirmation"), "Signup was unsuccessful"
    
    
def test_signup_user_sends_verification_email(test_client):
    with patch('app.modules.auth.services.AuthenticationService.send_verification_email') as mock_send_email:
        response = test_client.post(
            "/signup",
            data=dict(name="Foo", surname="Example", email="foo@example.com", password="foo1234"),
            follow_redirects=True,
        )
        # Verificar que el envío de correo fue llamado
        mock_send_email.assert_called_once()
        # Verificar que se redirige correctamente después del registro
        assert response.request.path == url_for("auth.confirmation"), "Signup redirection was incorrect"


#def test_unverified_user_cannot_login(test_client):
    # Crear usuario sin verificar
#    response = test_client.post(
#       "/signup",
#         data=dict(name="Foo", surname="Example", email="foo@example.com", password="foo1234"),
  #       follow_redirects=True,
    # )

    # Intentar iniciar sesión sin verificar
    # response = test_client.post(
      #   "/login",
        # data=dict(email="foo@example.com", password="foo1234"),
        # follow_redirects=True,
    # )
    # print(response.data)
    # Comprobar que la autenticación falla
    # assert b"Please verify your email" in response.data


def test_email_verification_token_generation():
    auth_service = AuthenticationService()
    user_data = {
        "name": "Test",
        "email": "test@example.com",
        "password": "test1234"
    }
    token = auth_service.serializer.dumps(user_data, salt='email-confirmation-salt')
    assert token is not None, "Token was not generated successfully"


def test_email_verification_token_confirmation():
    auth_service = AuthenticationService()
    user_data = {
        "name": "Test",
        "email": "test@example.com",
        "password": "test1234"
    }
    token = auth_service.serializer.dumps(user_data['email'], salt='email-confirmation-salt')
    email = auth_service.confirm_token(token)
    assert email == user_data['email'], "Token confirmation failed"


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
