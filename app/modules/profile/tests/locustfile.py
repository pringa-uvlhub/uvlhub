from locust import HttpUser, TaskSet, task, between


class UserProfileTasks(TaskSet):
    @task
    def view_user_profile(self):
        user_id = 1  
        with self.client.get(f"/profile/{user_id}", name="/profile/[user_id]", catch_response=True) as response:
            if response.status_code == 200 and "user_profile" in response.text:
                response.success()
            else:
                response.failure(f"Failed to load user profile for user_id={user_id}")


class WebsiteUser(HttpUser):
    tasks = [UserProfileTasks]
    wait_time = between(1, 5)
