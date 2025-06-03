from flask import Flask, request
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter
from multiprocessing import Process, Manager, cpu_count
import os
import time
import requests

app = Flask(__name__)
CORS(app)

metrics = PrometheusMetrics(app, group_by='endpoint')
load_request_counter = Counter("load_requests_total", "Total /load POST requests")

TARGET_URL = os.environ.get("LOAD_TARGET", "http://host.docker.internal:5000/load")

# Manager를 사용해 프로세스 간 이벤트 공유
manager = Manager()
stop_event = manager.Event()
load_process = None

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

def _send_requests(rps, duration_sec, urls):
    if not urls:
        return

    interval = 1.0 / rps
    end_time = time.time() + duration_sec
    i = 0
    while time.time() < end_time:
        if stop_event.is_set():
            break

        url = urls[i % len(urls)]
        try:
            requests.post(url, timeout=1)
        except:
            pass

        time.sleep(interval)
        i += 1


def send_http_load_loop(stop_event):
    url = f"{TARGET_URL}?duration=0.2"
    step_duration = 2
    max_rps = 1000
    rps = 200
    rps_increment = 50

    while not stop_event.is_set():
        print(f"[INFO] Sending load: {rps} RPS")
        _send_requests(rps, step_duration, [url])

        if rps < max_rps:
            rps += rps_increment

        if stop_event.is_set():
            break

    print("💤 Load generator stopped")

@app.route('/cpu/toggle', methods=['POST'])
def cpu_toggle():
    global load_process, stop_event

    if load_process is None or not load_process.is_alive():
        # 부하 시작
        stop_event.clear()
        load_process = Process(target=send_http_load_loop, args=(stop_event,))
        load_process.start()
        return "started"
    else:
        # 부하 중지
        stop_event.set()
        load_process.join(timeout=5)
        if load_process.is_alive():
            load_process.terminate()
        load_process = None
        return "stopped"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
