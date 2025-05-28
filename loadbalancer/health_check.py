import requests
import time
from typing import Dict

class HealthChecker:
    def __init__(self, targets: Dict[str, int], interval: int = 5, timeout: int = 2):
        """
        :param targets: {"http://127.0.0.1:8001": 0, "http://127.0.0.1:8002": 0}
        :param interval: health check 간격 (초)
        :param timeout: 요청 timeout 시간
        """
        self.targets = targets
        self.interval = interval
        self.timeout = timeout
        self.healthy = {target: True for target in self.targets}

    def check_once(self):
        for target in self.targets:
            try:
                res = requests.get(f"{target}/health", timeout=self.timeout)
                self.healthy[target] = (res.status_code == 200)
            except Exception:
                self.healthy[target] = False

    def start_loop(self):
        while True:
            self.check_once()
            print(f"[HealthCheck] 상태: {self.healthy}")
            time.sleep(self.interval)

    def is_healthy(self, target: str) -> bool:
        return self.healthy.get(target, False)

    def get_healthy_targets(self):
        return [t for t, ok in self.healthy.items() if ok]
