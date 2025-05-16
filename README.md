# PNU_cloud_computing

## 프로젝트 소개

본 프로젝트는 최소한의 자원으로 안정적인 서비스 제공을 위해, 트래픽 분산을 담당하는 로드밸런서의 개발 및 서버 자원 자동 확장을 위한 오토스케일링 기능을 통합적으로 구현하는 것을 목표로 한다. 로드밸런서는 헬스 체크 기능을 통해 백엔드 서버의 상태를 주기적으로 확인하고, 응답이 없거나 비정상적인 서버를 자동으로 트래픽 분산 대상에서 제외함으로써 안정성을 확보한다. 또한, 단순 라운드로빈 방식에 더해 서버 부하 정보를 반영한 분산 알고리즘을 도입하여, 요청 처리 효율을 높인다. 오토스케일링 기능은 CPU 사용률과 응답 지연 시간 등 시스템 메트릭을 기반으로 하여, 실시간으로 인스턴스를 자동으로 추가하거나 제거함으로써 동적인 자원 활용을 가능하게 한다. 또한 열려있는 서버들의 CPU 사용률 등의 모니터링을 Grafana 및 Prometheus를 활용하여 시각화한다.

## 시작 가이드

### Requirements

### Installation
```bash
$ git clone https://github.com/JAEIL1999/PNU_cloud_computing.git
```

## 디렉토리 구조
```bash
PNU_cloud_computing/
├── backend/
│   ├── Dockerfile
│   └── src/…
│
├── autoscaler/
│   ├── **init**.py
│   ├── autoscaler.py             # AutoScaler 핵심 로직
│   └── metrics.py                # PrometheusClient, DockerManager
│
├── loadbalancer/                 # 직접 구현하는 헬스체크 로드밸런서
│   ├── **init**.py
│   ├── health_check.py           # 개별 백엔드의 헬스 체크 로직
│   ├── balancer.py               # 요청 분배 로직 (round-robin, least-conn 등)
│   └── server.py                 # 외부 접속 인터페이스 (HTTP 서버)
│
├── prometheus/
│   ├── prometheus.yml
│   └── data/
│
├── grafana/
│   └── dashboards/…
│
└── docker-compose.yml
```