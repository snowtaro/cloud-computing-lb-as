from flask import Flask
from prometheus_client import Counter
from flask_cors import CORS 
from prometheus_flask_exporter import PrometheusMetrics
from multiprocessing import Process
import os

app = Flask(__name__)
CORS(app)
metrics = PrometheusMetrics(app)

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests')

running = False
load_processes = []

def load():
    while True:
        _ = sum(i * i for i in range(10000))

@app.route('/cpu/toggle', methods=['POST'])
def cpu_toggle():
    global running, load_processes
    if not running:
        running = True
        load_processes = []
        for _ in range(os.cpu_count()):
            p = Process(target=load)
            p.daemon = True
            p.start()
            load_processes.append(p)
        return "started"
    else:
        running = False
        for p in load_processes:
            p.terminate()
        load_processes = []
        return "stopped"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
