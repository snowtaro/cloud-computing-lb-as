from flask import Flask, request
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter
from multiprocessing import Process, Value, cpu_count
import os
import time
import requests

app = Flask(__name__)
CORS(app)

metrics = PrometheusMetrics(app, group_by='endpoint')

load_request_counter = Counter("load_requests_total", "Total /load POST requests")

TARGET_URL = os.environ.get("LOAD_TARGET", "http://host.docker.internal:5000/load")

load_process = None
increasing = Value('b', True)
active = Value('b', False)

def cpu_stress_worker(duration):
    end = time.time() + duration
    while time.time() < end:
        for _ in range(10000):
            _ = sum(i * i for i in range(1000))

@app.route('/load', methods=['POST'])
def load_handler():
    load_request_counter.inc()
    duration = float(request.args.get("duration", "0.2"))
    num_cores = cpu_count()
    processes = []

    for _ in range(num_cores):
        p = Process(target=cpu_stress_worker, args=(duration,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    return "ok"

def _send_requests(rps, duration_sec, url):
    interval = 1.0 / rps if rps > 0 else 1.0
    total_requests = int(rps * duration_sec)
    for _ in range(total_requests):
        try:
            requests.post(url, timeout=1)
        except:
            pass
        time.sleep(interval)

# send_http_load_loop 내부
def send_http_load_loop(increasing, active):
    url = f"{TARGET_URL}?duration=0.2"
    rps = 0
    max_rps = 40
    step = 2
    step_duration = 2

    active.value = True

    while active.value:  # <== active로 loop 제어
        if increasing.value:
            if rps < max_rps:
                rps += step
                rps = min(rps, max_rps)
            print(f"[RPS ↑] {rps}")
            _send_requests(rps, step_duration, url)
        else:
            if rps > 0:
                rps -= step
                rps = max(rps, 0)
                print(f"[RPS ↓] {rps}")
                _send_requests(rps, step_duration, url)
            else:
                print("[RPS] reached 0, exiting...")
                break

    print("💤 Load generator stopped.")
    active.value = False

@app.route('/cpu/toggle', methods=['POST'])
def cpu_toggle():
    global load_process, increasing, active

    if not active.value:
        increasing.value = True
        load_process = Process(target=send_http_load_loop, args=(increasing, active))
        load_process.start()
        return "started"
    else:
        increasing.value = False
        active.value = False
        if load_process is not None:
            load_process.terminate()
            load_process.join()
            load_process = None
        return "stopped"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
