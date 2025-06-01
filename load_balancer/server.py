from flask import Flask, request
from balancer import choose_backend, selection_mode

app = Flask(__name__)

@app.route('/')
def route_request():
    server = choose_backend()
    if not server:
        return "No healthy servers", 503
    try:
        import requests
        resp = requests.get(server['host'])
        return resp.content, resp.status_code
    except:
        return "Backend error", 500

@app.route('/set_mode/<mode>')
def set_mode(mode):
    from balancer import selection_mode
    if mode in ['round_robin', 'latency']:
        selection_mode = mode
        return f"Selection mode set to {mode}", 200
    else:
        return "Invalid mode", 400

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    from health_check import start_health_check
    start_health_check()  # 헬스체크 스레드 시작
    app.run(host='0.0.0.0', port=8080)
