from locust import HttpUser, task, between

class TaskUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def enqueue_and_check(self):
        res = self.client.post("/tasks/enqueue?payload=LocustTest")
        if res.status_code == 200:
            task_id = res.json().get("task_id")
            self.client.get(f"/tasks/{task_id}")