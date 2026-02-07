FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir .

# Copy application
COPY network_ranger/ ./network_ranger/

# Run
CMD ["python", "-m", "network_ranger"]
