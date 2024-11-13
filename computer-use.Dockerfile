FROM ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest

USER root

# Install iptables
RUN apt-get update && \
    apt-get install -y iptables && \
    apt-get install -y libpci3 libnss3-tools && \
    rm -rf /var/lib/apt/lists/* 

# Ensure proper X11 permissions
RUN mkdir -p /tmp/.X11-unix && \
    chmod 1777 /tmp/.X11-unix

# Install ca-certificates if not present
RUN apt-get update && apt-get install -y ca-certificates

# Copy the root CA certificate
COPY certs/mitmproxy-ca-cert.cer /usr/local/share/ca-certificates/mitmproxy-ca-cert.crt

# Copy the root cert to firefox's CA store
RUN mkdir -p ~/.mozilla/firefox/certificates && \
    certutil -A -n "mitmproxy" -t "C,," -i /usr/local/share/ca-certificates/mitmproxy-ca-cert.crt -d ~/.mozilla/firefox/certificates

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
