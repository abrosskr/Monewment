# EDENVALE 4.0 Standard Queen Container
FROM python:3.12-slim

# Enforce Non-Root for Security
RUN useradd -m edenvale
USER edenvale

# Workdir
WORKDIR /app

# Mount Points (Binding Iron Triangle)
# /monewment/core -> Host MONEWMENT-0 (Read-Only)
# /app/config -> Host QUEEN/config (Read-Only for Ally)
# /app/logic -> Host QUEEN/logic_boundary (Read-Write)

# Environment
ENV PYTHONPATH="/monewment/core"
ENV EDENVALE_MODE="PRODUCTION"

# Dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Logic (This layer changes frequently)
COPY logic_boundary ./logic_boundary
COPY config ./config

# Entry Point
CMD ["python", "logic_boundary/main.py"]
