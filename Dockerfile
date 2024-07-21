FROM python:3.10-slim@sha256:3be54aca807a43b5a1fa2133b1cbb4b58a018d6ebb1588cf1050b7cbebf15d55

WORKDIR /usr/app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install

RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python

RUN mkdir -p /usr/app && chown python:python /usr/app

USER 999


COPY . .
CMD ["env"]
