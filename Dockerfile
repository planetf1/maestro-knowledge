FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

ENV PYTHONPATH=/app

COPY ./src /app/src
COPY pyproject.toml /app
COPY start.sh /app
COPY stop.sh /app

RUN apt-get update && apt-get install -y --no-install-recommends procps

RUN uv sync

RUN chmod +x ./start.sh

RUN chown -R 1000:1000 /app

EXPOSE 8030
USER 1000:1000

ENTRYPOINT ["uv", "run", "./start.sh", "--host", "0.0.0.0", "--tail"]
