# AutoScaler

Prometheus로 수집한 CPU 사용률 메트릭을 기반으로 Docker Container를 자동으로 Scaling하는 Python 기반 AutoScaler입니다.

## 기능

- Prometheus에서 라벨 기준으로 CPU 사용률 수집
- 사용자 정의 임계치 기반 Scale Out/In
- 최소 및 최대 인스턴스 수 설정 가능
- 주기적 검사 및 로그 기록

## 구성

- AutoScaler
- PrometheusClient
- DockerManager

