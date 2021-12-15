FROM python:3.9.5-slim
COPY ./ app/
WORKDIR app
RUN pip install -r requirements.txt
RUN chmod 777 /data
ENTRYPOINT python bazos.py