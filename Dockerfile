FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

ENV PYTHONPATH=/app
ENV UV_CACHE_DIR=/app/cache

COPY --chown=1000:1000 ./src /app/src
COPY --chown=1000:1000 pyproject.toml /app
COPY --chown=1000:1000 start.sh /app
COPY --chown=1000:1000 stop.sh /app

RUN apt-get update && apt-get install -y --no-install-recommends procps

RUN uv sync

RUN chmod +x ./start.sh && \
  mkdir -p /app/cache && chown 1000:1000 /app/cache

EXPOSE 8030
USER 1000:1000

ENTRYPOINT ["uv", "run", "./start.sh", "--host", "0.0.0.0", "--tail"]
