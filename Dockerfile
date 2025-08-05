FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

ENV PYTHONPATH=/app

ADD . /app

RUN apt-get update && apt-get install -y --no-install-recommends procps

RUN uv sync

RUN chmod +x ./start.sh

ENTRYPOINT ["uv", "run", "./start.sh", "--host", "0.0.0.0", "--tail"]
