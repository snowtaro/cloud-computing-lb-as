from flask import Flask
from prometheus_client import start_http_server, Counter
from flask_cors import CORS 

app = Flask(__name__)
CORS(app) 


REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests')

@app.route('/')
def hello():
    REQUEST_COUNT.inc()
    return "Hello, this is the backend server!"

if __name__ == '__main__':
    from threading import Thread
    # 8001 포트에 Prometheus 메트릭 서버 따로 띄우기
    start_http_server(8001)

    # Flask 서버는 별도 스레드로 돌린다
    def run_flask():
        app.run(host='0.0.0.0', port=5000)

    flask_thread = Thread(target=run_flask)
    flask_thread.start()
