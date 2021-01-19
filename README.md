# Meli Proxy

Este repositorio contiene el diseño e implementación del challenge de mercadolibre para el equipo cloud.

## Diseño inicial
![Diseño de API Proxy](https://github.com/GFibrizo/meliproxy/blob/main/images/Meli%20Challenge.png)

### Load Balancer
- Se quiere poder distribuir la carga entre diferentes instancias clones del API Proxy. De esta manera logramos atender una mayor cantidad de requests por unidad de tiempo y evitamos tener un punto unico de fallo en el API Proxy.
- El algoritmo de load balancing tiene que ser capaz de distribuir la carga de manera de no sobrecargar a ninguna instancia. Para eso, una alternativa podría ser el algoritmo de **Least Connections**.
- Se quiere tener alta disponibilidad del Load Balancer para evitar que se vuelva un punto único de fallo. Para eso, se propone un esquema Active-Passive, donde al fallar el Load Balancer activo, el pasivo toma el rol del Activo inmediatamente. Para esto es necesario de algún orquestador externo.


#### Least Connections
En una situación donde todas las instancias que se reparten carga tienen las mismas especificaciones (son clones), puede servir este algoritmo para evitar que una instancia acumule muchas conexiones abiertas. El caso de esta acumulación podria ser porque se dió que varios usuarios estan realizando consultas que tardan bastante tiempo y justo fueron a parar a la misma instancia.
El algoritmo de Least Connections podría alivianar esta situación enviando a otras instancias nuevas conexiones que de otra forma hubieran ido al server sobrecargado.


### Instancias de API Proxy
- Se quiere poder tener varias instancias del API Proxy para poder manejar mas volumen de requests paralelizando y distribuyendo la carga entre las diferentes intancias.
- Se quiere poder escalar horizontalmente, es decir poder aumentar y reducir la cantidad de instancias dependiendo variación de la cantidad de requests por unidad de tiempo.
- Tener varias instancias distribuyendose la carga también sirve para evitar tener un punto único de fallo.
- Ante la falla de una instancia, otra debería levantarse en su lugar.
- Las instancias no deberían mantener estado relevante para la experiencia del cliente del API proxy, para que sean intercambiables y no importe si alguna se destruye o reemplaza por otra.

Como mecanismos de control para regular la cantidad de requests a los diferentes paths (servicios) de api.mercadolibre.com se propone:
- **[Circuit Breaker](https://docs.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker):** Mecanismo para recuperación ante fallos en requests, via apertura del circuito por una cierta cantidad de tiempo para darle tiempo al sistema que produjo el fallo de recuperarse, y luego mediante requests de prueba probar su estado y reanudar la comunicación normal (cerrar el circuito) una vez que el request de prueba fue exitoso. 
- **Rate Limiter:** Limitar la cantidad de requests que un cierto path pueda recibir en una cierta cantidad de tiempo. También limitar la cantidad de requests que un origen pueda enviar, de esta manera evitamos casos como ataques de denegacion de servicios.


### Cache
- Se quiere una caché para almacenar temporalmente requests hechos a cada instancia de API Proxy y sus correspondientes respuestas desde api.mercadolibre.com
- Cachear requests con responses permite obtener una respuesta mas rápida y aliviana la carga de los servicios que estan detras de api.mercadolibre.com
- La caché debería ser unificada para todas las instancias de API Proxy, para poder aprovechar los requests que hayan hecho ya las otras instancias.
- Se eligió redis como caché debido a que es una base de datos clave-valor en memoria que dá respuestas al menos un orden de magnitud mas rápido que bases de datos relacionales.
- Además, redis permite tener alta disponibilidad por medio de un esquema llamado Redis Sentinel.

#### Redis Sentinel
<p align="center"><img src="https://github.com/GFibrizo/meliproxy/blob/main/images/RedisSentinel.png" width="500"></p>
Este esquema permite tener alta disponibilidad de la base de datos redis.
En el caso de que el master se caiga, los redis sentinels se dan cuenta por medio de un mecanismo de healthcheck y mediante consenso. Como respuesta, promueven al slave a nuevo master y notifican al cliente de la base de datos quien es el nuevo master.

Es decir, cada redis sentinel realiza tareas de:
- **Monitoreo:** checkean si el master y slave estan corriendo y funcionando correctamente
- **Notificación:** notifica a quien tenga que hacerlo mediante una API cuando alguna de las instancias monitoreadas falla.
- **Recuperación automatica de fallos:** ante una falla del master, promueve un slave a master, y hace que el resto de los slaves conozcan el nuevo master.


### Estadisticas
- Para el diseño se eligió modelar esta parte mediante una API de estadisticas a la cual cada instancia de API proxy enviará estadisticas de requests agregadas en un cierto periodo de tiempo. Se elige agregar localmente en cada instacia esas métricas durante un periodo de tiempo (por ej. 30s o 1m) para evitar sobrecargar la API de estadisticas.
- Otras opciones consideradas para el diseño podrían haber sido utilizar una cola de mensajes


## Implementación

### Load Balancer
Como Load Balancer se utilizó Nginx, aunque para poder rutear los requests a las diferentes instancias de API Proxy se utilizó una configuración de Nginx que se aprovecha del nombre de la red docker donde estan levantadas y del hecho de que todas funcionan en el mismo puerto.
El punto de entrada termina siendo Nginx pero termina siendo Docker, entonces, quien termina realizando el balanceo de carga por medio de un esquema Round Robin.

### API Proxy
Las instancias de API proxy son APIs desarrollados en Python usando Flask y varias librerias los otros requeriemientos de métricas y mecanismos de control.

Se utilizaron las librerias:
- **[fabfuel/circuitbreaker](https://github.com/fabfuel/circuitbreaker):** Se utilizo con su configuración por defecto por lo que:
  - monitorea la ejecución de la función y cuenta las fallas
  - resetea el contador de fallos leugo de cada ejecución exitosa
  - abre el circuito y previene de futuras ejecuciones luego de 5 fallas consecutivas
  - cambia a el circuito a medio abierto y permite una ejecución de prueba luego de 30s de recovery
  - cierra el circuito si la ejecución de prueba fue exitosa 
- **[prometheus_flask_exporter](https://github.com/rycus86/prometheus_flask_exporter):** expone en un puerto de la aplicación (9090 por defecto) un endpoint para que se sea consultado por un server Prometheus y así le disponibiliza una serie de métricas para que éste consuma.
- **[alisaifee/flask-limiter](https://flask-limiter.readthedocs.io/en/stable/):** limita la cantidad de requests que un endpoint recibe luego de superado un threshold. 


### Cache

### Estadisticas

Se utilizó un server Prometheus para recolectar métricas de las diferentes instancias API Proxy y Grafana como herramienta para el Dashboard.

![Dashboard de estadisticas](https://github.com/GFibrizo/meliproxy/blob/main/images/Dashboard.png)

#### Prometheus
- Es un servidor para realizar tareas de monitoreo.
- Permite varios esquemas para recolectar métricas como hacer polling o recibir pushes.
- Elegí realizar polling de las instancias API Proxy por ser lo más rápido para desarrollar.
- Por medio de la configuración de Prometheus podemos definir IP y puerto de cada servicio del cual querramos colectar métricas, además de cada cuanto tiempo queremos realizar dicha colecta.
- Por defecto trae un [storage local](https://prometheus.io/docs/prometheus/latest/storage/#storage) que es una base de datos time series


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
