import pytest

# from app import db
from app.modules.conftest import login, logout
# from app.modules.auth.models import User
# from app.modules.profile.models import UserProfile
# from app.modules.dataset.models import DataSet, DSMetrics


@pytest.fixture(scope='module')
def test_client(test_client):

    with test_client.application.app_context():
        # user_test = User(email='user@example.com', password='test1234', is_admin=False)
        # admin_test = User(email='admin@example.com', password='test1234', is_admin=True)
        # db.session.add(user_test)
        # db.session.add(admin_test)
        # db.session.commit()

        # user_profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        # admin_profile = UserProfile(user_id=admin_test.id, name="Admin", surname="Administrator")
        # db.session.add(user_profile)
        # db.session.add(admin_profile)
        # db.session.commit()

        # ds_metrics = DSMetrics(number_of_models='5', number_of_features='50')
        # db.session.add(ds_metrics)
        # db.session.commit()

        # dataset = DataSet(user_id=user_test.id, ds_meta_data_id=ds_metrics.id)
        # db.session.add(dataset)
        # db.session.commit()
        pass

    yield test_client


def test_success(test_client):
    # Log in
    login_response = login(test_client, "admin@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Access dashboard
    response = test_client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200

    logout(test_client)


# def test_failed(test_client):
#     # Log in
#     login_response = login(test_client, "user@example.com", "test1234")
#     assert login_response.status_code == 200, "Login was unsuccessful."

#     # Access dashboard
#     response = test_client.get('/dashboard', follow_redirects=True)
#     assert response.status_code == 403

#     logout(test_client)
