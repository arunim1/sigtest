# Comprehensive Explanation of the Codebase

This codebase sets up a Docker-based environment that includes a computer-use demo application, a logging server, a reverse proxy using Nginx, and certificate generation for secure communications. Below is a detailed walkthrough of each component and its respective code.

## Table of Contents

1. [Overview](#overview)
2. [Dockerfiles](#dockerfiles)
   - [computer-use.Dockerfile](#computer-usedockerfile)
   - [logger.Dockerfile](#loggerdockerfile)
   - [certgen.Dockerfile](#certgendockerfile)
3. [Python Scripts](#python-scripts)
   - [logger.py](#loggerpy)
   - [generate_certs.py](#generate_certspy)
4. [Nginx Configuration](#nginx-configuration)
   - [nginx.conf](#nginxconf)
5. [Shell Script](#shell-script)
   - [entrypoint.sh](#entrypointsh)
6. [Docker Compose](#docker-compose)
   - [docker-compose.yml](#docker-composeyml)
7. [Summary](#summary)

---

## Overview

The system is composed of several Docker containers orchestrated using Docker Compose. The primary components include:

- **computer-use-demo**: The main application container.
- **nginx-proxy**: Acts as a reverse proxy to handle HTTP requests and inject custom headers.
- **logging-server**: A simple HTTP server that logs incoming requests.
- **cert-gen**: (Commented out) Generates SSL certificates for secure communication.

Additionally, custom scripts and configurations manage networking, certificate generation, and request logging.

---

## Dockerfiles

### `computer-use.Dockerfile`

This Dockerfile builds the `computer-use-demo` container, which sets up the environment for the main application.

```dockerfile
FROM ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest

USER root

# Install iptables
RUN apt-get update && \
    apt-get install -y iptables && \
    rm -rf /var/lib/apt/lists/* 

# Copy the CA certificate
COPY ./ca/rootCA.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

# Ensure proper X11 permissions
RUN mkdir -p /tmp/.X11-unix && \
    chmod 1777 /tmp/.X11-unix

# Copy the original entrypoint script
RUN cp /entrypoint.sh /original-entrypoint.sh

# Copy the new entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    chown computeruse:computeruse /entrypoint.sh
    
USER computeruse

ENTRYPOINT ["/entrypoint.sh"]
```

**Line-by-Line Explanation:**

1. **Base Image**:  
   ```dockerfile
   FROM ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest
   ```  
   - Uses a base image from Anthropic's GitHub Container Registry tailored for the computer-use demo.

2. **Switch to Root User**:  
   ```dockerfile
   USER root
   ```  
   - Grants administrative privileges to perform system-level tasks.

3. **Install `iptables`**:  
   ```dockerfile
   RUN apt-get update && \
       apt-get install -y iptables && \
       rm -rf /var/lib/apt/lists/* 
   ```  
   - Updates package lists, installs `iptables` for network traffic management, and cleans up to reduce image size.

4. **Copy CA Certificate**:  
   ```dockerfile
   COPY ./ca/rootCA.crt /usr/local/share/ca-certificates/
   RUN update-ca-certificates
   ```  
   - Adds a custom Certificate Authority (CA) certificate to the system and updates the certificate store.

5. **Set Up X11 Permissions**:  
   ```dockerfile
   RUN mkdir -p /tmp/.X11-unix && \
       chmod 1777 /tmp/.X11-unix
   ```  
   - Creates the X11 Unix socket directory with appropriate permissions for GUI applications.

6. **Manage Entrypoint Scripts**:  
   ```dockerfile
   RUN cp /entrypoint.sh /original-entrypoint.sh
   COPY entrypoint.sh /entrypoint.sh
   RUN chmod +x /entrypoint.sh && \
       chown computeruse:computeruse /entrypoint.sh
   ```  
   - Backs up the original entrypoint script, replaces it with a custom `entrypoint.sh`, makes it executable, and changes ownership to the `computeruse` user.

7. **Switch Back to Non-Root User**:  
   ```dockerfile
   USER computeruse
   ```  
   - Enhances security by running the container with a non-root user.

8. **Set Entrypoint**:  
   ```dockerfile
   ENTRYPOINT ["/entrypoint.sh"]
   ```  
   - Specifies the custom entrypoint script to execute when the container starts.

---

### `logger.Dockerfile`

This Dockerfile builds the `logging-server` container, which logs incoming HTTP requests.

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY logger.py .

EXPOSE 8000

CMD ["python", "logger.py"]
```

**Line-by-Line Explanation:**

1. **Base Image**:  
   ```dockerfile
   FROM python:3.9-slim
   ```  
   - Uses a lightweight Python 3.9 image.

2. **Set Working Directory**:  
   ```dockerfile
   WORKDIR /app
   ```  
   - Sets `/app` as the current working directory inside the container.

3. **Copy Application Code**:  
   ```dockerfile
   COPY logger.py .
   ```  
   - Copies the `logger.py` script into the container's working directory.

4. **Expose Port**:  
   ```dockerfile
   EXPOSE 8000
   ```  
   - Opens port `8000` for incoming connections.

5. **Define Command**:  
   ```dockerfile
   CMD ["python", "logger.py"]
   ```  
   - Specifies the command to run the `logger.py` script using Python.

---

### `certgen.Dockerfile`

This Dockerfile builds the `cert-gen` container, responsible for generating SSL certificates.

```dockerfile
FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y openssl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY generate_certs.py .

CMD ["python", "generate_certs.py"]
```

**Line-by-Line Explanation:**

1. **Base Image**:  
   ```dockerfile
   FROM python:3.9-slim
   ```  
   - Uses a lightweight Python 3.9 image.

2. **Install OpenSSL**:  
   ```dockerfile
   RUN apt-get update && \
       apt-get install -y openssl && \
       rm -rf /var/lib/apt/lists/*
   ```  
   - Updates package lists, installs OpenSSL for certificate generation, and cleans up to reduce image size.

3. **Set Working Directory**:  
   ```dockerfile
   WORKDIR /app
   ```  
   - Sets `/app` as the current working directory inside the container.

4. **Copy Certificate Generation Script**:  
   ```dockerfile
   COPY generate_certs.py .
   ```  
   - Copies the `generate_certs.py` script into the container's working directory.

5. **Define Command**:  
   ```dockerfile
   CMD ["python", "generate_certs.py"]
   ```  
   - Specifies the command to run the `generate_certs.py` script using Python.

---

## Python Scripts

### `logger.py`

A simple HTTP server that logs incoming requests in JSON format.

```python
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer


class LoggingHandler(BaseHTTPRequestHandler):
    def _handle_request(self):
        # Log request details
        timestamp = datetime.now().isoformat()
        request_info = {
            "timestamp": timestamp,
            "method": self.command,
            "path": self.path,
            "headers": dict(self.headers),
            "client_address": self.client_address[0],
        }

        print(json.dumps(request_info, indent=2))

        # Send a simple response
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Request logged")

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def do_PUT(self):
        self._handle_request()

    def do_DELETE(self):
        self._handle_request()

    def do_PATCH(self):
        self._handle_request()


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), LoggingHandler)
    print("Starting logging server on port 8000...")
    server.serve_forever()
```

**Line-by-Line Explanation:**

1. **Imports**:  
   - `json`, `datetime` for handling time and formatting logs.  
   - `BaseHTTPRequestHandler`, `HTTPServer` for creating the HTTP server.

2. **LoggingHandler Class**:  
   ```python
   class LoggingHandler(BaseHTTPRequestHandler):
       def _handle_request(self):
           ...
       
       def do_GET(self):
           self._handle_request()
       
       def do_POST(self):
           self._handle_request()
       
       def do_PUT(self):
           self._handle_request()
       
       def do_DELETE(self):
           self._handle_request()
       
       def do_PATCH(self):
           self._handle_request()
   ```  
   - Inherits from `BaseHTTPRequestHandler` to handle HTTP requests.
   - The `_handle_request` method logs request details and sends a response.
   - The HTTP methods (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`) all delegate to `_handle_request`.

3. **Handling Requests**:  
   ```python
   def _handle_request(self):
       # Log request details
       timestamp = datetime.now().isoformat()
       request_info = {
           "timestamp": timestamp,
           "method": self.command,
           "path": self.path,
           "headers": dict(self.headers),
           "client_address": self.client_address[0],
       }

       print(json.dumps(request_info, indent=2))

       # Send a simple response
       self.send_response(200)
       self.send_header("Content-Type", "text/plain")
       self.end_headers()
       self.wfile.write(b"Request logged")
   ```  
   - Captures the current timestamp.
   - Gathers request details: HTTP method, path, headers, and client IP address.
   - Prints the request information as a formatted JSON string to the console.
   - Sends a `200 OK` response with a plain text message.

4. **Running the Server**:  
   ```python
   if __name__ == "__main__":
       server = HTTPServer(("0.0.0.0", 8000), LoggingHandler)
       print("Starting logging server on port 8000...")
       server.serve_forever()
   ```  
   - Initializes the HTTP server to listen on all interfaces (`0.0.0.0`) at port `8000`.
   - Prints a startup message.
   - Begins serving requests indefinitely.

---

### `generate_certs.py`

This script generates a root Certificate Authority (CA) and a wildcard certificate signed by this CA using OpenSSL.

```python
import subprocess
from pathlib import Path

CA_DIR = Path("/ca")
CERTS_DIR = Path("/certs")


def run_openssl(command):
    subprocess.run(["openssl"] + command, check=True)


def generate_ca():
    """Generate root CA certificate and private key"""
    if not (CA_DIR / "rootCA.key").exists():
        # Generate CA private key
        run_openssl(["genrsa", "-out", str(CA_DIR / "rootCA.key"), "4096"])

        # Generate CA certificate
        run_openssl(
            [
                "req",
                "-x509",
                "-new",
                "-nodes",
                "-key",
                str(CA_DIR / "rootCA.key"),
                "-sha256",
                "-days",
                "3650",
                "-out",
                str(CA_DIR / "rootCA.crt"),
                "-subj",
                "/C=US/ST=State/L=City/O=Proxy CA/CN=Proxy Root CA",
            ]
        )


def generate_wildcard_cert():
    """Generate wildcard certificate signed by our CA"""
    if not (CERTS_DIR / "proxy.key").exists():
        # Generate private key
        run_openssl(["genrsa", "-out", str(CERTS_DIR / "proxy.key"), "2048"])

        # Generate CSR
        run_openssl(
            [
                "req",
                "-new",
                "-key",
                str(CERTS_DIR / "proxy.key"),
                "-out",
                str(CERTS_DIR / "proxy.csr"),
                "-subj",
                "/C=US/ST=State/L=City/O=Proxy/CN=*.proxy.local",
            ]
        )

        # Create config file for SAN
        with open(CERTS_DIR / "proxy.cnf", "w") as f:
            f.write(
                """[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name

[req_distinguished_name]

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = *.proxy.local
DNS.2 = *.com
DNS.3 = *.org
DNS.4 = *.net
DNS.5 = *.io
DNS.6 = *.*
"""
            )

        # Generate certificate
        run_openssl(
            [
                "x509",
                "-req",
                "-in",
                str(CERTS_DIR / "proxy.csr"),
                "-CA",
                str(CA_DIR / "rootCA.crt"),
                "-CAkey",
                str(CA_DIR / "rootCA.key"),
                "-CAcreateserial",
                "-out",
                str(CERTS_DIR / "proxy.crt"),
                "-days",
                "365",
                "-sha256",
                "-extfile",
                str(CERTS_DIR / "proxy.cnf"),
                "-extensions",
                "v3_req",
            ]
        )


def main():
    # Create directories
    CA_DIR.mkdir(exist_ok=True)
    CERTS_DIR.mkdir(exist_ok=True)

    # Generate certificates
    generate_ca()
    generate_wildcard_cert()


if __name__ == "__main__":
    main()
```

**Line-by-Line Explanation:**

1. **Imports and Path Setup**:  
   ```python
   import subprocess
   from pathlib import Path

   CA_DIR = Path("/ca")
   CERTS_DIR = Path("/certs")
   ```  
   - Imports `subprocess` for running shell commands and `Path` for path manipulations.
   - Defines directories for storing CA and certificate files.

2. **Utility Function `run_openssl`**:  
   ```python
   def run_openssl(command):
       subprocess.run(["openssl"] + command, check=True)
   ```  
   - Prepends the `openssl` command to the provided arguments and executes it.
   - Raises an error if the command fails.

3. **Generate Root CA**:  
   ```python
   def generate_ca():
       ...
   ```  
   - Checks if `rootCA.key` exists. If not, generates a 4096-bit RSA private key and a corresponding self-signed CA certificate valid for 10 years.

4. **Generate Wildcard Certificate**:  
   ```python
   def generate_wildcard_cert():
       ...
   ```  
   - Checks if `proxy.key` exists. If not, generates a 2048-bit RSA private key.
   - Creates a Certificate Signing Request (CSR) for a wildcard domain (`*.proxy.local`).
   - Writes a configuration file (`proxy.cnf`) to specify Subject Alternative Names (SANs).
   - Generates the wildcard certificate (`proxy.crt`) signed by the previously created root CA.

5. **Main Execution**:  
   ```python
   def main():
       # Create directories
       CA_DIR.mkdir(exist_ok=True)
       CERTS_DIR.mkdir(exist_ok=True)

       # Generate certificates
       generate_ca()
       generate_wildcard_cert()

   if __name__ == "__main__":
       main()
   ```  
   - Ensures that the CA and certificates directories exist.
   - Initiates the certificate generation process.

---

## Nginx Configuration

### `nginx.conf`

Configures Nginx as a reverse proxy that mirrors incoming requests to the logging server and handles request routing.

```nginx
events {
    worker_connections 1024;
}

# test with curl -X POST "https://httpbin.org/anything" 

http {
    log_format debug_log '[$time_local] $remote_addr - $remote_user - $server_name '
                        'to: $upstream_addr: $request upstream_response_time $upstream_response_time '
                        'request_time $request_time '
                        'status: $status request_body: $request_body '
                        'custom_header: $http_custom_header '
                        'host: $http_host '
                        'uri: $request_uri';

    access_log /dev/stdout debug_log;
    error_log /dev/stdout debug;

    # Resolve DNS using Docker's DNS server
    resolver 127.0.0.11 valid=30s ipv6=off;

    server {
        listen 80;
        # Remove SSL configuration for now since we don't have certificates
        # listen 443 ssl;
        server_name _;

        # Comment out SSL configuration
        # ssl_certificate /certs/proxy.crt;
        # ssl_certificate_key /certs/proxy.key;

        set $logging_backend "logging-server:8000";

        # Define a mirror location
        location = /_mirror {
            internal;
            proxy_pass http://$logging_backend$request_uri;
            proxy_set_header Host $http_host; 
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header custom-header "intercepted";
            
            # Don't wait for logging server response
            proxy_ignore_client_abort on;
            proxy_read_timeout 1s;
            proxy_connect_timeout 1s;
        }

        location / {
            # Mirror the request to the logging location
            mirror /_mirror;
            mirror_request_body on;

            # Remove HTTPS handling since we're only doing HTTP for now
            proxy_set_header custom-header "intercepted";
            proxy_set_header Host $http_host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_pass http://$http_host$request_uri;
            # proxy_pass http://logging-server:8000;
        }
    }
}
```

**Line-by-Line Explanation:**

1. **Events Block**:  
   ```nginx
   events {
       worker_connections 1024;
   }
   ```  
   - Defines the maximum number of simultaneous connections Nginx can handle.

2. **HTTP Block**:  
   ```nginx
   http {
       ...
   }
   ```  
   - Encloses all HTTP-related configurations.

3. **Log Format**:  
   ```nginx
   log_format debug_log '[$time_local] $remote_addr - $remote_user - $server_name '
                       'to: $upstream_addr: $request upstream_response_time $upstream_response_time '
                       'request_time $request_time '
                       'status: $status request_body: $request_body '
                       'custom_header: $http_custom_header '
                       'host: $http_host '
                       'uri: $request_uri';
   ```  
   - Defines a custom log format named `debug_log` that captures various request and response details, including custom headers.

4. **Access and Error Logs**:  
   ```nginx
   access_log /dev/stdout debug_log;
   error_log /dev/stdout debug;
   ```  
   - Directs access and error logs to standard output using the defined log formats.

5. **DNS Resolver**:  
   ```nginx
   resolver 127.0.0.11 valid=30s ipv6=off;
   ```  
   - Configures Nginx to use Docker's internal DNS resolver for service discovery.
   - Sets DNS entries to be valid for 30 seconds and disables IPv6.

6. **Server Block**:  
   ```nginx
   server {
       listen 80;
       # Remove SSL configuration for now since we don't have certificates
       # listen 443 ssl;
       server_name _;

       # Comment out SSL configuration
       # ssl_certificate /certs/proxy.crt;
       # ssl_certificate_key /certs/proxy.key;

       set $logging_backend "logging-server:8000";

       ...
   }
   ```  
   - Listens on port `80` for HTTP requests.
   - SSL configurations are commented out as certificates are not currently set up.
   - Defines a variable `$logging_backend` pointing to the `logging-server` service on port `8000`.

7. **Mirror Location**:  
   ```nginx
   location = /_mirror {
       internal;
       proxy_pass http://$logging_backend$request_uri;
       proxy_set_header Host $http_host; 
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_set_header custom-header "intercepted";
       
       # Don't wait for logging server response
       proxy_ignore_client_abort on;
       proxy_read_timeout 1s;
       proxy_connect_timeout 1s;
   }
   ```  
   - Defines an internal location `/mirror` used for mirroring requests.
   - Proxies the mirrored request to the logging server.
   - Sets various headers, including a custom header `custom-header`.
   - Configured to not wait for the logging server's response to prevent delays.

8. **Main Location Block**:  
   ```nginx
   location / {
       # Mirror the request to the logging location
       mirror /_mirror;
       mirror_request_body on;

       # Remove HTTPS handling since we're only doing HTTP for now
       proxy_set_header custom-header "intercepted";
       proxy_set_header Host $http_host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       
       proxy_pass http://$http_host$request_uri;
       # proxy_pass http://logging-server:8000;
   }
   ```  
   - Mirrors incoming requests to the `/mirror` location for logging.
   - Enables mirroring of the request body.
   - Sets various headers, including the `custom-header`.
   - Proxies the original request to the intended destination (`$http_host$request_uri`).

---

## Shell Script

### `entrypoint.sh`

A custom entrypoint script that sets up `iptables` rules to redirect HTTP and HTTPS traffic through the Nginx proxy.

```bash
#!/bin/bash
set -e

# Switch to root to set up iptables
NGINX_IP=$(getent hosts nginx-proxy | awk '{ print $1 }')
echo "NGINX_IP: $NGINX_IP"
sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to-destination $NGINX_IP:80
sudo iptables -t nat -A OUTPUT -p tcp --dport 443 -j DNAT --to-destination $NGINX_IP:80

# Run the original command as computeruse user
exec /original-entrypoint.sh "$@"
```

**Line-by-Line Explanation:**

1. **Shebang and Options**:  
   ```bash
   #!/bin/bash
   set -e
   ```  
   - Specifies the script to be run using Bash.
   - `set -e` ensures that the script exits immediately if any command exits with a non-zero status.

2. **Retrieve Nginx Proxy IP**:  
   ```bash
   NGINX_IP=$(getent hosts nginx-proxy | awk '{ print $1 }')
   echo "NGINX_IP: $NGINX_IP"
   ```  
   - Uses `getent` to resolve the hostname `nginx-proxy` to its IP address.
   - Stores the IP in the `NGINX_IP` variable and prints it for debugging purposes.

3. **Set Up iptables Rules**:  
   ```bash
   sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to-destination $NGINX_IP:80
   sudo iptables -t nat -A OUTPUT -p tcp --dport 443 -j DNAT --to-destination $NGINX_IP:80
   ```  
   - Adds NAT rules to redirect all outgoing TCP traffic on ports `80` (HTTP) and `443` (HTTPS) to the Nginx proxy's IP on port `80`.

4. **Execute Original Entrypoint**:  
   ```bash
   exec /original-entrypoint.sh "$@"
   ```  
   - Replaces the current shell with the original entrypoint script, passing along any arguments.
   - Ensures that the main application starts after setting up the network rules.

---

## Docker Compose

### `docker-compose.yml`

Defines and configures all Docker services, networks, and dependencies.

```yaml
services:
  computer-use-demo:
    build:
      context: .
      dockerfile: computer-use.Dockerfile
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DISPLAY=:1
      - XAUTHORITY=/home/computeruse/.Xauthority
    volumes:
      - $HOME/.anthropic:/home/computeruse/.anthropic
      - /tmp/.X11-unix:/tmp/.X11-unix
    ports:
      - "5901:5901"
      - "8501:8501"
      - "6080:6080"
      - "8080:8080"
    networks:
      - app_net
    cap_add:
      - NET_ADMIN
    depends_on:
      # - cert-gen
      - nginx-proxy

  # cert-gen:
  #   build:
  #     context: .
  #     dockerfile: certgen.Dockerfile
  #   volumes:
  #     - ./ca:/ca
  #     - ./certs:/certs

  # Nginx reverse proxy for header injection and routing
  nginx-proxy:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/certs:ro
    networks:
      - app_net
    depends_on:
      - logging-server

  # Simple logging web server
  logging-server:
    build: 
      context: .
      dockerfile: logger.Dockerfile
    networks:
      - app_net
    ports:
      - "127.0.0.1:8000:8000"

networks:
  app_net:
    driver: bridge
```

**Section-by-Section Explanation:**

1. **Services Definition**:  
   ```yaml
   services:
     computer-use-demo:
       ...
     # cert-gen:
       ...
     nginx-proxy:
       ...
     logging-server:
       ...
   ```  
   - Defines all services used in the application.
   - The `cert-gen` service is currently commented out, indicating it may not be in use.

2. **`computer-use-demo` Service**:  
   ```yaml
   computer-use-demo:
     build:
       context: .
       dockerfile: computer-use.Dockerfile
     environment:
       - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
       - DISPLAY=:1
       - XAUTHORITY=/home/computeruse/.Xauthority
     volumes:
       - $HOME/.anthropic:/home/computeruse/.anthropic
       - /tmp/.X11-unix:/tmp/.X11-unix
     ports:
       - "5901:5901"
       - "8501:8501"
       - "6080:6080"
       - "8080:8080"
     networks:
       - app_net
     cap_add:
       - NET_ADMIN
     depends_on:
       # - cert-gen
       - nginx-proxy
   ```  
   - **Build Configuration**:  
     - Builds the image using `computer-use.Dockerfile` from the current context.
   
   - **Environment Variables**:  
     - `ANTHROPIC_API_KEY`: Injected from the host environment.
     - `DISPLAY`: Sets the display for GUI applications (`:1`).
     - `XAUTHORITY`: Points to the X11 authentication file.
   
   - **Volumes**:  
     - Mounts the `.anthropic` directory from the host to the container.
     - Mounts the X11 Unix socket for GUI support.
   
   - **Ports**:  
     - Exposes multiple ports:
       - `5901`: Typically used for VNC.
       - `8501`: Commonly used for services like Streamlit.
       - `6080`: Often used for web-based VNC clients.
       - `8080`: General-purpose HTTP port.
   
   - **Networks**:  
     - Connects to the `app_net` network.
   
   - **Capabilities**:  
     - Adds `NET_ADMIN` capability to manage network configurations (`iptables`).
   
   - **Dependencies**:  
     - Depends on the `nginx-proxy` service.
     - The `cert-gen` service is commented out and not currently a dependency.

3. **`cert-gen` Service** (Commented Out):  
   ```yaml
   # cert-gen:
   #   build:
   #     context: .
   #     dockerfile: certgen.Dockerfile
   #   volumes:
   #     - ./ca:/ca
   #     - ./certs:/certs
   ```  
   - Intended to build and run the certificate generation process.
   - Mounts local directories for CA and certificates.
   - Currently disabled by being commented out.

4. **`nginx-proxy` Service**:  
   ```yaml
   nginx-proxy:
     image: nginx:alpine
     volumes:
       - ./nginx.conf:/etc/nginx/nginx.conf:ro
       - ./certs:/certs:ro
     networks:
       - app_net
     depends_on:
       - logging-server
   ```  
   - **Image**:  
     - Uses the lightweight `nginx:alpine` image.
   
   - **Volumes**:  
     - Mounts the custom `nginx.conf` as a read-only file.
     - Mounts the `certs` directory as read-only for SSL configurations (currently not in use).
   
   - **Networks**:  
     - Connects to the `app_net` network.
   
   - **Dependencies**:  
     - Depends on the `logging-server` service to ensure it's running first.

5. **`logging-server` Service**:  
   ```yaml
   logging-server:
     build: 
       context: .
       dockerfile: logger.Dockerfile
     networks:
       - app_net
     ports:
       - "127.0.0.1:8000:8000"
   ```  
   - **Build Configuration**:  
     - Builds the image using `logger.Dockerfile` from the current context.
   
   - **Networks**:  
     - Connects to the `app_net` network.
   
   - **Ports**:  
     - Forwards port `8000` from the container to `127.0.0.1:8000` on the host, making it accessible only locally.

6. **Networks Definition**:  
   ```yaml
   networks:
     app_net:
       driver: bridge
   ```  
   - Defines a custom bridge network named `app_net` for inter-service communication.

---

## Summary

This codebase establishes a Dockerized environment comprising:

1. **Main Application (`computer-use-demo`)**:  
   - Built from a specialized Anthropic base image.
   - Configured with network management (`iptables`) to redirect HTTP/HTTPS traffic through a reverse proxy.
   - Supports GUI applications via X11 forwarding.

2. **Reverse Proxy (`nginx-proxy`)**:  
   - Utilizes Nginx to handle incoming HTTP requests.
   - Mirrors requests to the `logging-server` for logging purposes.
   - Prepares for SSL implementation, though currently operating over HTTP.

3. **Logging Server (`logging-server`)**:  
   - Runs a simple Python-based HTTP server that logs incoming requests in JSON format.
   - Accessible only from the host machine.

4. **Certificate Generation (`cert-gen`)**:  
   - Although currently disabled, this service is designed to generate a root CA and wildcard certificates for secure communications.
   - Facilitates SSL configurations in the future.

5. **Networking**:  
   - All services communicate over a custom bridge network (`app_net`), ensuring isolation and controlled connectivity.
   - The main application container has elevated network permissions to manage traffic routing effectively.

6. **Entrypoint Script**:  
   - Custom script in the main application container modifies `iptables` to ensure all outbound HTTP/HTTPS traffic is routed through the Nginx proxy, enabling centralized request handling and logging.

This setup is modular, allowing for easy scaling and addition of services as needed. The use of Docker Compose simplifies the orchestration of these containers, managing dependencies and network configurations seamlessly.