from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from mitmproxy import http
import time

with open("/certs/private_key.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
    )

def sign(request_id):
    timestamp = str(int(time.time()))
    
    # Create and sign message
    message = f"{timestamp} | {request_id}"
    print(f"Signing message: {message}", flush=True)
    signature = private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    print(f"Signature: {signature.hex()}", flush=True)
    
    # Return headers instead of JSON
    return timestamp, signature.hex()

def request(flow: http.HTTPFlow) -> None:
    print(flow.request.pretty_url, flush=True)

    # Get request ID
    request_id = "12309"
    flow.request.headers["Agent-ID"] = request_id

    timestamp, signature = sign(request_id)

    # Add headers to the request
    flow.request.headers["Agent-Timestamp"] = timestamp
    flow.request.headers["Agent-Signature"] = signature
    print(flow.request.headers, flush=True)
