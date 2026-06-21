FROM python:3.11-slim

WORKDIR /app

# psutil may need to be compiled on some platforms such as Linux ARM64.
# Install build tools so pip can build psutil if a prebuilt wheel is not
#   available.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY system_app.py .

CMD ["python", "system_app.py"]