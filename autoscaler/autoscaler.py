import time
import logging
import os
from metrics import PrometheusClient, DockerManager

class AutoScaler:
    def __init__(
        self,
        prom_url: str,
        docker_image: str,
        label: str = 'autoscale_service',
        cpu_threshold: float = 0.7,
        min_instances: int = 0,
        max_instances: int = 10,
        check_interval: int = 30
    ):
        self.prom = PrometheusClient(prom_url)
        self.dock = DockerManager()
        self.image = docker_image
        self.label = label
        self.threshold = cpu_threshold
        self.min = min_instances
        self.max = max_instances
        self.interval = check_interval

    def scale(self) -> None:
        containers = self.dock.list_containers(self.label)
        count = len(containers)

        if count < self.min:
            logging.info(f"Instances below minimum ({count} < {self.min}). Scaling up.")
            self.dock.run_container(self.image, self.label)
            return

        usages = [self.dock.get_container_cpu(c) for c in containers]
        avg_cpu = sum(usages) / count if usages else 0.0
        logging.info(f"Average CPU usage: {avg_cpu:.2f}% across {count} containers.")

        if avg_cpu > (self.threshold * 100) and count < self.max:
            logging.info("CPU above threshold. Scaling up by 1.")
            self.dock.run_container(self.image, self.label)

        elif avg_cpu < (self.threshold * 50) and count > self.min:
            logging.info("CPU below half threshold. Scaling down by 1.")
            for c in reversed(containers):
                if not self.dock._is_fixed(c):
                    self.dock.remove_container(c)
                    break
            else:
                logging.info("No removable container found (only fixed ones).")

    def run(self) -> None:
        logging.info("Starting AutoScaler loop.")
        while True:
            try:
                self.scale()
            except Exception as e:
                logging.error(f"Error during scaling: {e}")
            time.sleep(self.interval)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    prom_url = os.getenv('PROM_URL', 'http://localhost:8001')
    docker_img = os.getenv('DOCKER_IMAGE', '')
    min_i = int(os.getenv('MIN_INSTANCES', 1))
    max_i = int(os.getenv('MAX_INSTANCES', 10))
    cpu_th = float(os.getenv('CPU_THRESHOLD', 0.7))
    interval = int(os.getenv('CHECK_INTERVAL', 30))

    scaler = AutoScaler(prom_url, docker_img, min_instances=min_i,
                        max_instances=max_i, cpu_threshold=cpu_th,
                        check_interval=interval)
    scaler.run()
