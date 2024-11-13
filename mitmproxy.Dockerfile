# Dockerfile.mitmproxy
FROM mitmproxy/mitmproxy

# Install the requests library
RUN pip install requests cryptography

COPY certs/private_key.pem /certs/private_key.pem