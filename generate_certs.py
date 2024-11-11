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
