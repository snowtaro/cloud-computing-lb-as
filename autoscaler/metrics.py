import requests
import docker
import os

class PrometheusClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def get_metric(self, query: str) -> float:
        """Query Prometheus HTTP API and return the first value"""
        url = f"{self.base_url}/api/v1/query"
        resp = requests.get(url, params={'query': query})
        resp.raise_for_status()
        data = resp.json()
        if data.get('status') != 'success' or not data['data']['result']:
            return 0.0
        return float(data['data']['result'][0]['value'][1])

class DockerManager:
    def __init__(self):
        self.client = docker.from_env()

    def list_containers(self, label: str):
        return self.client.containers.list(filters={'label': label})

    def run_container(self, image: str, label: str):
        project = os.getenv('COMPOSE_PROJECT_NAME', 'pnu_cloud_computing')
        service = label
        compose_labels = {
            'com.docker.compose.project': project,
            'com.docker.compose.service': service,
            'com.docker.compose.oneoff': 'False',
            'autoscale_service': label,
        }
        return self.client.containers.run(
            image,
            labels=compose_labels,
            detach=True
        )

    def remove_container(self, container) -> None:
        container.stop()
        container.remove()

    def get_container_cpu(self, container) -> float:
        stats = container.stats(stream=False)
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
        system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
        if system_delta > 0.0:
            num_cpus = len(stats['cpu_stats']['cpu_usage'].get('percpu_usage', []))
            return (cpu_delta / system_delta) * num_cpus * 100.0
        return 0.0