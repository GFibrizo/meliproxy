import os
from circuitbreaker import circuit
from flask import Flask, Response, jsonify, make_response, request
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
#from prometheus_flask_exporter import PrometheusMetrics
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics
from requests import get

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "redis", # Flask-Caching related configs
    "CACHE_REDIS_PASSWORD": 'str0ng_passw0rd',
    "CACHE_REDIS_HOST": os.environ['REDIS_HOST'],
    "CACHE_REDIS_PORT": os.environ['REDIS_PORT'],
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask('__main__')
app.config.from_mapping(config)
cache = Cache(app)
limiter = Limiter(app, key_func=get_remote_address)
URL = os.environ["URL"]
#PrometheusMetrics(app)
metrics = GunicornPrometheusMetrics(app)


@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(jsonify(error="ratelimit exceeded %s" % e.description), 429)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@cache.cached(timeout=50)
@circuit
@limiter.limit("1/second")
def proxy(path):
  app.logger.info("{} - {}".format(request.method, path))
  return get(f'{URL}{path}').content

