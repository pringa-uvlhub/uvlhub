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
            db.drop_all()
            db.create_all()
            user1 = User(id=5, email="user5@example.com", password="1234", created_at=datetime(2022, 3, 13))
            db.session.add(user1)
            db.session.commit()
            user2 = User(id=6, email="user6@example.com", password="1234", created_at=datetime(2022, 3, 13))
            db.session.add(user2)
            db.session.commit()
            profile = UserProfile(
                user_id=user2.id,
                surname="TestSurname",
                name="TestName",
                affiliation="TestAffiliation",
                orcid="0000-0001-2345-6789"
            )
            db.session.add(profile)
            db.session.commit()
            community = Community(
                id=1,
                name="For Test",
                description="For Test description",
                created_at=datetime(2022, 3, 13),
                created_by_id=5,
                admin_by_id=5
            )
            db.session.add(community)
            db.session.commit()
            yield client


def test_create_community(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200

    form_data = {
        "name": "Test Community",
        "description": "A community for testing purposes",
    }

    response = client.post("/community/create", data=form_data)
    assert response.status_code == 302


def test_create_community_empty_form(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200

    form_data = {
        "name": "",
        "description": "",
    }

    response = client.post("/community/create", data=form_data)
    assert response.status_code == 400


def test_show_community(client):
    response = client.get('/community/1')
    assert response.status_code == 200


def test_show_community_not_exist(client):
    response = client.get('/community/10')
    assert response.status_code == 404


def test_delete_community(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200

    response = client.post('/community/1/delete', follow_redirects=True)
    assert response.status_code == 200

    community = Community.query.get(1)
    assert community is None


def test_delete_community_not_exist(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200

    response = client.post('/community/999/delete', follow_redirects=True)
    assert response.status_code == 404


def test_delete_community_not_authorized(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200

    community = Community(
        id=2,
        name="Another Community",
        description="Community for testing permission",
        created_at=datetime(2022, 3, 13),
        created_by_id=5,
        admin_by_id=6
    )
    db.session.add(community)
    db.session.commit()

    response = client.post('/community/2/delete', follow_redirects=True)
    assert response.status_code == 403


def test_join_community(client):
    login_response = login(client, "user6@example.com", "1234")
    assert login_response.status_code == 200

    response = client.post('/community/1/join', follow_redirects=True)
    assert response.status_code == 200


def test_list_members(client):
    response = client.get('/community/1/members')
    assert response.status_code == 200


def test_list_members_community_not_exist(client):
    response = client.get('/community/99/members')
    assert response.status_code == 404


def test_edit_community(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200

    form_data = {
        "name": "Updated Test Community",
        "description": "Updated community description",
    }

    response = client.post('/community/1/edit', data=form_data)
    assert response.status_code == 302


def test_edit_community_not_authorized(client):
    login_response = login(client, "user6@example.com", "1234")
    assert login_response.status_code == 200

    form_data = {
        "name": "Updated Test Community",
        "description": "Updated community description",
    }
    response = client.post('/community/1/edit', data=form_data)
    assert response.status_code == 403


def test_edit_community_not_found(client):
    login_response = login(client, "user5@example.com", "1234")
    assert login_response.status_code == 200

    form_data = {
        "name": "Updated Test Community",
        "description": "Updated community description",
    }
    response = client.post('/community/999/edit', data=form_data)
    assert response.status_code == 404
