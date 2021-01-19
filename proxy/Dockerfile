# ---- Base ----
# ---- Python ----
FROM python:3.6 AS build
COPY proxy.py .
COPY wsgi.py .
COPY conf.py .
COPY requirements.txt .
# install app dependencies
RUN pip install  --user -r requirements.txt
ENV PATH=/root/.local/bin:$PATH
ENV URL=https://reqres.in/api/
EXPOSE 8080
CMD [ "gunicorn", "-c", "conf.py", "-b", "0.0.0.0:8080", "wsgi:app", "--chdir", "./", "--preload"]
