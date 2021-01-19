# Meli Proxy

Este repositorio contiene el diseño e implementación del challenge de mercadolibre para el equipo cloud.

## Diseño inicial
![Diseño de API Proxy](https://github.com/GFibrizo/meliproxy/blob/main/images/Meli%20Challenge.png)

### Load Balancer

### Instancias de API Proxy
- Se quiere poder tener varias instancias del API Proxy para poder manejar mas volumen de requests paralelizando y distribuyendo la carga entre las diferentes intancias.
- Se quiere poder escalar horizontalmente, es decir poder aumentar y reducir la cantidad de instancias dependiendo variación de la cantidad de requests por unidad de tiempo.
- Tener varias instancias distribuyendose la carga también sirve para evitar tener un punto único de fallo.
- Ante la falla de una instancia, otra debería levantarse en su lugar.
- Las instancias no deberían mantener estado relevante para la experiencia del cliente del API proxy, para que sean intercambiables y no importe si alguna se destruye o reemplaza por otra.

### Cache
- Se quiere una caché para almacenar temporalmente requests hechos a cada instancia de API Proxy y sus correspondientes respuestas desde api.mercadolibre.com
- Cachear requests con responses permite obtener una respuesta mas rápida y aliviana la carga de los servicios que estan detras de api.mercadolibre.com
- La caché debería ser unificada para todas las instancias de API Proxy, para poder aprovechar los requests que hayan hecho ya las otras instancias.
- Se eligió redis como caché debido a que es una base de datos clave-valor en memoria que dá respuestas al menos un orden de magnitud mas rápido que bases de datos relacionales.
- Además, redis permite tener alta disponibilidad por medio de un esquema llamado Redis Sentinel.

#### Redis Sentinel



### Estadisticas



## Implementación



### Como levantar el proyecto

- Buildear imagen de instancia de proxy ejecutando `docker build -t proxy-server:latest .` en el subdirectorio `./proxy`
- Levantar todos los componenentes ejecutando `docker-compose up --build -d --scale redis-sentinel=3 --scale proxy=5` en el directorio raiz del repositorio.

### Como conectar a redis (cache)
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
