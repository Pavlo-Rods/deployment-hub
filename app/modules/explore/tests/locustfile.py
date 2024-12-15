from locust import HttpUser, TaskSet, task
from core.environment.host import get_host_for_locust_testing


class ExploreBehavior(TaskSet):
    def on_start(self):
        """
        Simulate logging in before starting the tasks.
        """
        self.login()

    @task(2)
    def index(self):
        """
        Simulate accessing the explore index.
        """
        response = self.client.get("/explore")
        if response.status_code != 200:
            print(f"Explore index failed: {response.status_code}")

    @task(3)
    def query_by_tag(self):
        """
        Simulate querying datasets by tags.
        """
        payload = {"query": "tags:tag1", "sorting": "newest", "publication_type": "any"}
        response = self.client.post("/explore", json=payload)
        if response.status_code != 200:
            print(f"Query by tag failed: {response.status_code}")

    @task(3)
    def query_by_author(self):
        """
        Simulate querying datasets by author.
        """
        payload = {"query": "author:Thor Odinson", "sorting": "newest", "publication_type": "any"}
        response = self.client.post("/explore", json=payload)
        if response.status_code != 200:
            print(f"Query by author failed: {response.status_code}")

    @task(1)
    def invalid_query(self):
        """
        Simulate sending an invalid query.
        """
        payload = {"query": "invalid_field:1234", "sorting": "newest", "publication_type": "any"}
        response = self.client.post("/explore", json=payload)
        if response.status_code != 200:
            print(f"Invalid query failed: {response.status_code}")

    def login(self):
        """
        Simulate user login.
        """
        login_payload = {"email": "user@example.com", "password": "test1234"}
        response = self.client.post("/login", data=login_payload)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")


class ExploreUser(HttpUser):
    tasks = [ExploreBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
