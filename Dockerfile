FROM python:3.9.5-slim
COPY ./ app/
RUN chmod 777 app/data
RUN pip install -r app/requirements.txt
ENTRYPOINT python app/bazos.py