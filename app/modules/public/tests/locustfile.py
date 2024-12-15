from locust import HttpUser, task, between
import random


class DashboardUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.client.post("/login", data={
            "email": "user@example.com",
            "password": "test1234"
        })

    @task(3)
    def view_dashboard(self):
        with self.client.get("/dashboard", catch_response=True) as response:
            if response.status_code == 200:
                print("Dashboard loaded successfully.")
            else:
                print(f"Error loading dashboard: {response.status_code}")
                response.failure(f"Got status code {response.status_code}")

    @task(2)
    def view_dashboard_metrics(self):
        with self.client.get("/dashboard/metrics", catch_response=True) as response:
            if response.status_code == 200:
                print("Dashboard metrics loaded successfully.")
            else:
                print(f"Error loading dashboard metrics: {response.status_code}")
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def update_dashboard_data(self):
        new_data = {
            "total_datasets": random.randint(1, 1000),
            "total_feature_models": random.randint(1, 500),
            "total_downloads": random.randint(1, 10000),
            "total_views": random.randint(1, 5000)
        }
        with self.client.post("/dashboard/update", data=new_data, catch_response=True) as response:
            if response.status_code == 200:
                print("Dashboard data updated successfully.")
            else:
                print(f"Error updating dashboard data: {response.status_code}")
                response.failure(f"Got status code {response.status_code}")

    def on_stop(self):
        self.client.get("/logout")
