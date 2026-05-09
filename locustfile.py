from locust import HttpUser, task, between


class ShortistUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def create_link(self):
        self.client.post("/links/shorten", json={
            "original_url": "https://google.com",
            "expire_at": None
        })

    @task(5)
    def redirect_link(self):
        self.client.get("/links/abc123", allow_redirects=False)

    @task(1)
    def redirect_nonexistent(self):
        self.client.get("/links/nonexistent", allow_redirects=False)