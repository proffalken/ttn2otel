FROM python:3.10-slim@sha256:3be54aca807a43b5a1fa2133b1cbb4b58a018d6ebb1588cf1050b7cbebf15d55

# Set our environment variables
## OTEL Endpoint, defaults to localhost via HTTP
ENV OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
ENV OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
ENV OTEL_EXPORTER_OTLP_HEADERS=""
## What do we want the service name to be called (defaults to "ttn2otel")
ENV SERVICE_NAME=ttn2otel

WORKDIR /usr/app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY ./src/* .
RUN touch /usr/app/config.yaml
CMD exec poetry run opentelemetry-instrument --traces_exporter console,otlp --metrics_exporter console,otlp --logs_exporter console,otlp --service_name ${SERVICE_NAME} python ttn2otel.py
