import time
import logging
import os
import multiprocessing
from metrics import PrometheusClient, DockerManager, clear_prometheus_targets
class AutoScaler:
    def __init__(
        self,
        prom_url: str,
        docker_image: str,
        label: str = 'autoscale_service',
        cpu_threshold: float = 0.5,
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

        self.above_since = None
        self.below_since = None

    def scale(self) -> None:
        containers = self.dock.list_containers(self.label)
        autoscaled_containers = [c for c in containers if not self.dock._is_fixed(c)]
        count = len(containers)

        if count < self.min:
            logging.info(f"Instances below minimum ({count} < {self.min}). Scaling up.")
            self.dock.run_container(self.image, self.label)
            self.above_since = None
            self.below_since = None
            return

        usages = [self.dock.get_container_cpu(c) for c in containers]
        raw_avg = sum(usages) / count if usages else 0.0
        normalized_avg = raw_avg / 100

        logging.info(
            f"Avg CPU: {normalized_avg * 100:.2f}% across {count} containers"
        )

        now = time.time()

        if normalized_avg > self.threshold:
            if self.above_since is None:
                self.above_since = now
                logging.debug("CPU above threshold, starting timer for scale-out.")
            elif now - self.above_since >= 30 and count < self.max:
                logging.info("CPU above threshold for ≥ 2 minutes. Scaling up by 1.")
                self.dock.run_container(self.image, self.label)
                self.above_since = None
                self.below_since = None
        else:
            self.above_since = None

        if normalized_avg < self.threshold / 2:
            if self.below_since is None:
                self.below_since = now
                logging.debug("CPU below half-threshold, starting timer for scale-in.")
            elif now - self.below_since >= 15 and len(autoscaled_containers) > 0:
                target = autoscaled_containers[-1]
                logging.info(f"CPU below half-threshold for ≥ 1 minute. Scaling down container: {target.name}")
                self.dock.remove_container(target)
                self.above_since = None
                self.below_since = None
            elif now - self.below_since >= 30:
                logging.info("CPU below half-threshold, but no removable container found (all fixed).")
        else:
            self.below_since = None

    def run(self) -> None:
        logging.info("Starting AutoScaler loop.")
        while True:
            try:
                self.scale()
            except Exception as e:
                logging.error(f"Error during scaling: {e}")
            time.sleep(self.interval)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    clear_prometheus_targets()
    prom_url = os.getenv('PROM_URL', 'http://localhost:8001')
    docker_img = os.getenv('DOCKER_IMAGE', '')
    min_i = int(os.getenv('MIN_INSTANCES', 1))
    max_i = int(os.getenv('MAX_INSTANCES', 10))
    cpu_th = float(os.getenv('CPU_THRESHOLD', 0.7))
    interval = int(os.getenv('CHECK_INTERVAL', 30))

    scaler = AutoScaler(
        prom_url,
        docker_img,
        min_instances=min_i,
        max_instances=max_i,
        cpu_threshold=cpu_th,
        check_interval=interval
    )
    scaler.run()
