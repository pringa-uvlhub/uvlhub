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
from unittest.mock import patch


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

            profile = UserProfile(user_id=user.id, surname="TestSurname", name="TestName",
                                  affiliation="TestAffiliation", orcid="0000-0000-0000-0001")
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


def test_email_verification_token_generation():
    auth_service = AuthenticationService()
    user_data = {
        "name": "Test",
        "email": "test@example.com",
        "password": "test1234"
    }
    token = auth_service.serializer.dumps(user_data, salt='email-confirmation-salt')
    assert token is not None, "Token was not generated successfully"


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


def test_unverified_user_cannot_login(test_client):
    # Crear usuario sin verificar
    test_client.post(
        "/signup",
        data=dict(name="Foo", surname="Example", email="foo@example.com", password="foo1234"),
        follow_redirects=True,
    )

    # Intentar iniciar sesión sin verificar
    response = test_client.post(
        "/login",
        data=dict(email="foo@example.com", password="foo1234"),
        follow_redirects=True,
    )

    # Comprobar que la autenticación falla
    assert response.request.path == url_for("auth.login"), "Login redirection was incorrect"


def test_confirm_email_invalid_token(test_client):
    # Se define una constante para evitar el hardcoding
    response = test_client.get(url_for('auth.confirm_email', token="invalid_token"))
    assert response.status_code == 302
    with test_client.session_transaction() as session:
        flashes = session['_flashes']
        assert any('Invalid confirmation token.' in flash[1] for flash in flashes)


def test_confirm_email_already_confirmed(test_client):
    user = User(id=11, email="alreadyconfirmed@example.com", password="1234", created_at=datetime(2022, 3, 13))
    db.session.add(user)
    db.session.commit()

    token = AuthenticationService().serializer.dumps({"email": "alreadyconfirmed@example.com"},
                                                     salt='email-confirmation-salt')
    response = test_client.get(url_for('auth.confirm_email', token=token))

    assert response.status_code == 302


def test_signup_success_created_user_verification(test_client):
    response = test_client.post(url_for('auth.show_signup_form'), data={
        'email': 'test@example.com',
        'password': 'password123',
        'name': 'Test',
        'surname': 'User'
    })
    assert response.status_code == 302  # Redirige a la página de confirmación
    assert response.location == url_for('auth.confirmation')
    # Verificar que el usuario no ha sido creado todavía porque la confirmación es necesaria
    user = User.query.filter_by(email='test@example.com').first()
    assert user is None  # El usuario aún no debe existir hasta confirmar el email


def test_signup_existing_email(test_client):
    # Crear un usuario existente
    user = User(email='existing@example.com', password='password', created_at=datetime(2022, 3, 13))
    db.session.add(user)
    db.session.commit()

    # Intentar registrarse con el mismo correo electrónico
    response = test_client.post(url_for('auth.show_signup_form'), data={
        'email': 'existing@example.com',
        'password': 'newpassword',
        'name': 'New',
        'surname': 'User'
    })
    assert response.status_code == 200
    assert b'Email existing@example.com in use' in response.data


def test_signup_missing_fields(test_client):
    response = test_client.post(url_for('auth.show_signup_form'), data={
        'email': '',
        'password': '',
        'name': '',
        'surname': ''
    })
    assert response.status_code == 200
    assert b'This field is required' in response.data  # Verificar que hay errores de validación por campos vacíos


def test_signup_invalid_email_format(test_client):
    response = test_client.post(url_for('auth.show_signup_form'), data={
        'email': 'invalid-email',
        'password': 'password123',
        'name': 'Test',
        'surname': 'User'
    })
    assert response.status_code == 200
    assert b'Invalid email address' in response.data


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
    user = User(id=8, email="foo0@example.com", password="1234", created_at=datetime(2022, 3, 13))
    db.session.add(user)
    db.session.commit()

    test_client.get(url_for('auth.logout'))
    response = test_client.post(url_for('auth.forgot_password'), data={'email': 'foo0@example.com'})

    assert response.status_code == 302
    assert response.location == url_for('auth.login', _external=False)


def test_reset_password_authenticated(test_client):
    user = User(email="test@example.com")
    user.set_password("password")
    login_user(user)

    response = test_client.get(url_for("auth.reset_password", token="some_token"))

    assert response.status_code == 302
    assert response.location == url_for("public.index", _external=False)


def test_reset_password_invalid_or_expired_token(test_client):
    test_client.get(url_for('auth.logout'))

#   codacy-disable-line hardcoded-credentials
    ERROR_MESSAGE_INVALID_TOKEN = "invalid_or_expired_token"  # nosec

    response = test_client.get(url_for("auth.reset_password", token=ERROR_MESSAGE_INVALID_TOKEN))

    assert response.status_code == 302
    assert response.location == url_for("auth.forgot_password", _external=False)

    with test_client.session_transaction() as session:
        assert '_flashes' in session
        flashes = session['_flashes']
        assert any("El enlace de restablecimiento es inválido o ha expirado." in flash[1] for flash in flashes)


def test_reset_password_valid_token_invalid_form(test_client):
    user = User(id=9, email="foo1@example.com", password="1234", created_at=datetime(2022, 3, 13))
    db.session.add(user)
    db.session.commit()

    user = UserRepository().get_by_email("foo1@example.com")

    valid_token = User.generate_reset_token(user)
    test_client.get("/logout", follow_redirects=True)
    response = test_client.get(url_for("auth.reset_password", token=valid_token))

    assert response.status_code == 200
    response = test_client.post(url_for("auth.reset_password", token=valid_token), data={})
    assert response.status_code == 200


def test_reset_password_valid_token_valid_form(test_client):
    user = User(id=10, email="foo2@example.com", password="1234", created_at=datetime(2022, 3, 13))
    db.session.add(user)
    db.session.commit()

    user = UserRepository().get_by_email("foo2@example.com")

    valid_token = User.generate_reset_token(user)
    test_client.get("/logout", follow_redirects=True)
    user = User.query.filter_by(email="foo2@example.com").first()

    response = test_client.get(url_for("auth.reset_password", token=valid_token))
    assert response.status_code == 200

    response = test_client.post(
        url_for("auth.reset_password", token=valid_token),
        data={"password": "newpassword123", "confirm_password": "newpassword123"}
    )

    assert response.status_code == 302
    assert response.location == url_for("auth.login", _external=False)
    user = User.query.filter_by(email="foo2@example.com").first()
    assert user.check_password("newpassword123")
