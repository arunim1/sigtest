FROM python:3.9-slim

RUN pip install flask cryptography

WORKDIR /app
COPY signer.py .

CMD ["python", "signer.py"] 