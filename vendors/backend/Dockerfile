# 🐳 Vendors Intelligence Engine (Official Image)
# Base: Lightweight Python 3.10
FROM python:3.10-slim

# 1. Environment Setup
WORKDIR /code
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Dependencies
# Cache-friendly pip install
COPY requirements.txt /code/
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 3. Application Code
# Copy the 'app' package
COPY ./app /code/app

# 4. Exposure
# HTTP Port
EXPOSE 80

# 5. Launch
# "The Brain is waking up..."
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]