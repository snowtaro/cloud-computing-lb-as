import requests
import docker
import json
import time
import logging
import os
import uuid

FLASK_TARGET_PATH = '/etc/prometheus/targets/flask.json'

class PrometheusClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def get_metric(self, query: str) -> float:
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
        containers = self.client.containers.list(filters={'label': label})
        for c in containers:
            logging.debug(f"Container {c.name} ({c.short_id}) - fixed={c.labels.get('fixed')}")
        return containers

    def run_container(self, image: str, label: str):
        project = os.getenv('COMPOSE_PROJECT_NAME', 'pnu_cloud_computing')
        service = label
        compose_labels = {
            'com.docker.compose.project': project,
            'com.docker.compose.service': service,
            'com.docker.compose.oneoff': 'False',
            'autoscale_service': label,
        }
        labels = {'autoscale_service': label}
        existing = self.list_containers(label)
        if not any(self._is_fixed(c) for c in existing):
            labels['fixed'] = 'true'

        labels = {**compose_labels, **labels}
        container_name = f"{label}-{uuid.uuid4().hex[:5]}"

        container = self.client.containers.run(
            image,
            name=container_name,
            labels=labels,
            detach=True,
            ports={'5000/tcp': None},
            network='pnu_cloud_computing_mynet'
        )
        self.update_prometheus_targets(label)
        return container

    def remove_container(self, container):
        if self._is_fixed(container):
            logging.info(f"Skipping fixed container: {container.name} ({container.short_id})")
            return
        logging.info(f"Removing container: {container.name} ({container.short_id})")
        container.stop()
        container.remove()
        self.update_prometheus_targets(container.labels.get('autoscale_service'))

    def get_container_cpu(self, container):
        stats_stream = container.stats(stream=True, decode=True)
        first = next(stats_stream)
        time.sleep(1)
        second = next(stats_stream)
        del stats_stream

        cpu_delta = second['cpu_stats']['cpu_usage']['total_usage'] - first['cpu_stats']['cpu_usage']['total_usage']
        system_delta = second['cpu_stats']['system_cpu_usage'] - first['cpu_stats']['system_cpu_usage']

        if system_delta > 0.0 and cpu_delta > 0.0:
            num_cpus = len(second['cpu_stats']['cpu_usage'].get('percpu_usage', [])) or 1
            return (cpu_delta / system_delta) * num_cpus * 100.0
        return 0.0

    def update_prometheus_targets(self, label: str):
        containers = self.list_containers(label)
        targets = []

        for c in containers:
            if not self._is_fixed(c):
                targets.append(f"{c.name}:5000")

        os.makedirs(os.path.dirname(FLASK_TARGET_PATH), exist_ok=True)
        with open(FLASK_TARGET_PATH, 'w') as f:
            json.dump([{"targets": targets, "labels": {"job": "flask-autoscaled"}}], f)


    def _is_fixed(self, container) -> bool:
        return str(container.labels.get('fixed', '')).lower() == 'true'

def clear_prometheus_targets():
    os.makedirs(os.path.dirname(FLASK_TARGET_PATH), exist_ok=True)
    with open(FLASK_TARGET_PATH, 'w') as f:
        json.dump([{"targets": [], "labels": {"job": "flask-autoscaled"}}], f)
