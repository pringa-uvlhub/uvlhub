import random
from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing


class CommunityBehavior(TaskSet):
    def on_start(self):
        self.index()
        self.client.post("/login", data={
            "email": "user1@example.com",
            "password": "1234"
        })

    @task(13)
    def view_communities(self):
        search_terms = ["Bio", "science", "AI", ""]
        search_term = random.choice(search_terms)
        params = {"search": search_term} if search_term else {}
        response = self.client.get("/communities", params=params)

        if response.status_code == 200:
            print(f"Viewed communities successfully with search term: '{search_term}'")
        else:
            print(f"Failed to view communities with search term '{search_term}': {response.status_code}")

    @task(12)
    def remove_user(self):
        community_id = 6
        user_id = 1
        response = self.client.post(f"/community/{community_id}/remove_user/{user_id}")
        if response.status_code == 200:
            print(f"User {user_id} removed from community {community_id} successfully")
        else:
            print(f"Failed to remove user {user_id} from community {community_id}: {response.json()}")

    @task(11)
    def edit_community(self):
        community_id = random.choice([1, 3, 6])
        form_data = {
            "name": "test community update",
            "description": "test community update",
        }
        response = self.client.post(f"/community/{community_id}/edit", data=form_data)
        if response.status_code == 200:
            print(f"Community {community_id} edited successfully")
        else:
            print(f"Failed to edit community {community_id}: {response.json()}")

    @task(10)
    def grant_admin(self):
        community_id = 6
        user_id = 1
        response = self.client.post(f"/community/{community_id}/grant_admin/{user_id}")
        if response.status_code == 200:
            print(f"Admin rights granted to user {user_id} in community {community_id}")
        else:
            print(f"Failed to grant admin rights to user {user_id} in community {community_id}: {response.json()}")

    @task(9)
    def leave_community(self):
        community_id = 5
        response = self.client.post(f"/community/{community_id}/leave")
        if response.status_code == 200:
            print(f"Successfully left community {community_id}")
        else:
            print(f"Failed to leave community {community_id}: {response.json()}")

    @task(8)
    def list_members(self):
        community_id = random.randint(1, 4)
        response = self.client.get(f"/community/{community_id}/members")
        if response.status_code == 200:
            print(f"Members listed for community {community_id}")
        else:
            print(f"Failed to list members for community {community_id}: {response.json()}")

    @task(7)
    def join_community(self):
        community_id = random.choice([2, 4])
        response = self.client.post(f"/community/{community_id}/join")
        if response.status_code == 200:
            print(f"Successfully joined community {community_id}")
        else:
            print(f"Failed to join community {community_id}: {response.json()}")

    @task(6)
    def delete_community(self):
        community_id = random.choice([1, 3])
        response = self.client.post(f"/community/{community_id}/delete")
        if response.status_code == 200:
            print(f"Community {community_id} deleted successfully")
        else:
            print(f"Failed to delete community {community_id}: {response.json()}")

    @task(5)
    def show_community(self):
        community_id = random.randint(1, 4)
        response = self.client.get(f"/community/{community_id}")
        if response.status_code == 200:
            print(f"Viewed details of community {community_id}")
        else:
            print(f"Failed to view community {community_id}: {response.json()}")

    @task(4)
    def create_community(self):
        form_data = {
            "name": "test community",
            "description": "test community",
        }
        response = self.client.post("/community/create", data=form_data)
        if response.status_code == 200:
            print("Community created successfully")
        else:
            print(f"Failed to create community: {response.status_code}")

    @task(3)
    def index_my_communities(self):
        response = self.client.get("/my_communities")
        if response.status_code == 200:
            print("My communities indexed successfully")
        else:
            print(f"Failed to index my communities: {response.status_code}")

    @task(2)
    def index_my_joined_communities(self):
        response = self.client.get("/my_joined_communities")
        if response.status_code == 200:
            print("My joined communities indexed successfully")
        else:
            print(f"Failed to index my joined communities: {response.status_code}")

    @task(1)
    def index(self):
        response = self.client.get("/community")
        if response.status_code == 200:
            print("Community index page loaded successfully")
        else:
            print(f"Failed to load community index page: {response.status_code}")


class CommunityUser(HttpUser):
    tasks = [CommunityBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
