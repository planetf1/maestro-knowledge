# Start with the slim base image
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory and environment variables
WORKDIR /app
ENV PYTHONPATH=/app
ENV UV_CACHE_DIR=/app/cache

# 1. Install system packages and create the non-root user and app directory.
# This layer changes infrequently.
RUN apt-get update && \
    apt-get install -y --no-install-recommends procps && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --shell /bin/bash appuser --uid 1000 && \
    chown -R 1000:1000 /app

# Switch to the non-root user
USER appuser

# 2. Copy only the dependency definition file.
COPY --chown=1000:1000 pyproject.toml .

# 3. Install Python dependencies.
# This layer will now only be rebuilt if 'pyproject.toml' changes,
# not every time you change a source file.
RUN uv sync

# 4. Copy the rest of the application code.
# This is the most frequently changed part, so it comes last.
COPY --chown=1000:1000 ./src /app/src
COPY --chown=1000:1000 start.sh stop.sh /app/
RUN chmod +x /app/start.sh

# Define the port and the final command to run the application
EXPOSE 8030
ENTRYPOINT ["uv", "run", "./start.sh", "--host", "0.0.0.0", "--tail"]