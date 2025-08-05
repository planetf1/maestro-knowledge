FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

ENV PYTHONPATH=/app
ENV UV_CACHE_DIR=/app/cache

ADD . /app

RUN apt-get update && apt-get install -y --no-install-recommends procps

RUN uv sync

RUN chmod +x ./start.sh
RUN chmod -R 777 /app

RUN chown -R 1000:100 /app &&\
    mkdir -p /app/cache && chown 1000:100 /app/cache

USER 1000:100

ENTRYPOINT ["uv", "run", "./start.sh", "--host", "0.0.0.0", "--tail"]
