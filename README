# Meli Proxy

Este repositorio contiene el diseño e implementación del challenge de mercadolibre para el equipo cloud.

## Diseño inicial


## Implementación



## Como levantar el proyecto

- Buildear imagen de instancia de proxy ejecutando `docker build -t proxy-server:latest .` en el subdirectorio `./proxy`
- Levantar todos los componenentes ejecutando `docker-compose up --build -d --scale redis-sentinel=3 --scale proxy=5` en el directorio raiz del repositorio.

# Como conectar a redis (cache)
docker exec -it redis-sentinel_redis_1 redis-cli -a str0ng_passw0rd


Links
- https://github.com/selcukusta/redis-sentinel-with-haproxy/blob/master/docker-compose.yml
- https://flask-caching.readthedocs.io/en/latest/
- https://flask-limiter.readthedocs.io/en/stable/#deploy-behind-proxy
- https://github.com/fabfuel/circuitbreaker
- https://github.com/rycus86/prometheus_flask_exporter/tree/master/examples/sample-signals
- https://pypi.org/project/prometheus-client/
- https://opensource.com/article/18/4/metrics-monitoring-and-python
- https://prometheus.io/docs/introduction/overview/
- https://medium.com/flask-monitoringdashboard-turtorial/monitor-your-flask-web-application-automatically-with-flask-monitoring-dashboard-d8990676ce83
- https://github.com/flask-dashboard/Flask-MonitoringDashboard
- https://github.com/HealYouDown/flask-statistics
