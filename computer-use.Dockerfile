FROM ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest

USER root

# Install iptables and SSL libraries
RUN apt-get update && \
    apt-get install -y iptables libpci3 libnss3-tools ca-certificates && \
    rm -rf /var/lib/apt/lists/* 

# Ensure proper X11 permissions
RUN mkdir -p /tmp/.X11-unix && \
    chmod 1777 /tmp/.X11-unix

# Copy the root CA certificate
COPY certs/mitmproxy-ca-cert.cer /usr/local/share/ca-certificates/mitmproxy-ca-cert.crt

# Update certificates
RUN update-ca-certificates -v

# Copy and set permissions for entrypoint scripts
COPY original-entrypoint.sh /original-entrypoint.sh
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /original-entrypoint.sh && \
    chmod +x /entrypoint.sh && \
    chown computeruse:computeruse /original-entrypoint.sh && \
    chown computeruse:computeruse /entrypoint.sh

USER computeruse

ENTRYPOINT ["/entrypoint.sh"]
