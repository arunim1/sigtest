FROM python:3.9-slim
WORKDIR /app
COPY test-web-server/app.py /app
RUN pip install flask cryptography
EXPOSE 5000
CMD ["python", "app.py"]