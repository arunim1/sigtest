FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y openssl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY generate_certs.py .

CMD ["python", "generate_certs.py"]