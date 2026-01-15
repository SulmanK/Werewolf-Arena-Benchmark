# Basic Dockerfile for Werewolf benchmark
FROM python:3.11-slim
WORKDIR /app
COPY . /app
# Install deps if present
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi
# Default command: single run; override in CI to run smoke/multi as needed
CMD ["python", "-m", "benchmark.runner", "--seed", "123"]
