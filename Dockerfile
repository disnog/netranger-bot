FROM python:3.12-slim

WORKDIR /app

# Install git for pip git dependencies
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .

# Copy application
COPY network_ranger/ ./network_ranger/

# Run
CMD ["python", "-m", "network_ranger"]
