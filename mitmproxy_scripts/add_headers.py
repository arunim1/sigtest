from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509
from mitmproxy import http
import time
import base64

with open("/certs/private_key.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
    )

with open("/certs/signed_cert.pem", "rb") as cert_file: 
    cert = x509.load_pem_x509_certificate(cert_file.read())

def sign(request_id):
    timestamp = str(int(time.time()))
    
    # Create and sign message
    message = f"{timestamp} | {request_id}"
    # print(f"Signing message: {message}", flush=True)
    signature = private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    # print(f"Signature: {signature.hex()}", flush=True)
    
    # Return headers instead of JSON
    return timestamp, signature.hex()

def request(flow: http.HTTPFlow) -> None:
    # print(flow.request.pretty_url, flush=True)

    # Get request ID
    request_id = "12309"
    flow.request.headers["agent-id"] = request_id

    timestamp, signature = sign(request_id)

    # Add headers to the request
    flow.request.headers["agent-timestamp"] = timestamp
    flow.request.headers["agent-signature"] = signature
    
    # Encode certificate in DER format and then Base64
    cert_der = cert.public_bytes(serialization.Encoding.DER)
    cert_b64 = base64.b64encode(cert_der).decode()
    flow.request.headers["agent-cert"] = cert_b64
    
    # print(flow.request.headers, flush=True)
