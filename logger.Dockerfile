FROM python:3.9-slim

WORKDIR /app

COPY logger.py .

EXPOSE 8000

CMD ["python", "-u", "logger.py"]