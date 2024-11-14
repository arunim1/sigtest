# Dockerfile.mitmproxy
FROM mitmproxy/mitmproxy

# Install the requests library
RUN pip install requests cryptography

COPY certs/private_key.pem /certs/private_key.pem
COPY certs/signed_cert.pem /certs/signed_cert.pem