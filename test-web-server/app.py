# app.py
from flask import Flask, request, abort, jsonify
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography import x509
import datetime
import base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # print("arrived", flush=True)
    # print(dict(request.headers), flush=True)
    
    # Inspect the headers using lowercase keys
    agent_cert = request.headers.get('agent-cert')
    agent_signature = request.headers.get('agent-signature')
    agent_timestamp = request.headers.get('agent-timestamp')
    agent_id = request.headers.get('agent-id')

    if not all([agent_cert, agent_signature, agent_timestamp, agent_id]):
        print("failed missing headers", flush=True)
        # Print which ones are missing
        if not agent_cert:
            print("agent-cert is missing", flush=True)
        if not agent_signature:
            print("agent-signature is missing", flush=True)
        if not agent_timestamp:
            print("agent-timestamp is missing", flush=True)
        if not agent_id:
            print("agent-id is missing", flush=True)
        abort(403)  # Missing headers

    message = f"{agent_timestamp} | {agent_id}"
    try:
        # Decode the Base64-encoded DER certificate
        cert_der = base64.b64decode(agent_cert)
        cert = x509.load_der_x509_certificate(cert_der)
        # Get public key
        public_key = cert.public_key()
        # Verify signature
        public_key.verify(
            bytes.fromhex(agent_signature),
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
    except Exception as e:
        print("failed", flush=True)
        print(e, flush=True)
        abort(403)

    # Access granted - return some protected data
    protected_data = {
        "message": f"Hello, {agent_id}! The current server time is {datetime.datetime.now()}."
    }
    return jsonify(protected_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')
