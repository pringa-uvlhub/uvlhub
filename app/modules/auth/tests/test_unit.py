import pytest
from flask import url_for
from flask_login import login_user

from app.modules.auth.services import AuthenticationService
from app.modules.auth.models import User
from app.modules.auth.repositories import UserRepository
from app.modules.profile.repositories import UserProfileRepository
from datetime import datetime, timezone

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
    assert response.request.path == url_for("public.index"), "Signup was unsuccessful"

def test_service_create_with_profile_success(clean_database):
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

    test_client.get(url_for('auth.logout'))
    response = test_client.post(url_for('auth.forgot_password'), data={'email': 'test@example.com'})

    assert response.status_code == 302
    assert response.location == url_for('auth.login', _external=False)
