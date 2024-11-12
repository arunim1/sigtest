from flask import Flask, request
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import time

app = Flask(__name__)

# Load the private key at startup
with open("/certs/private_key.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
    )

@app.route('/sign', methods=['GET'])
def sign():
    request_id = request.args.get('id', '')
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
    response = app.make_response('')
    response.headers['X-Timestamp'] = timestamp
    response.headers['X-Signature'] = signature.hex()
    return response

if __name__ == '__main__':
    print("Starting signer service...", flush=True)
    app.run(host='0.0.0.0', port=8001) 