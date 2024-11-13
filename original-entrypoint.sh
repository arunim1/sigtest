#!/bin/bash
set -e

./start_all.sh
./novnc_startup.sh

python http_server.py > /tmp/server_logs.txt 2>&1 &

# override default certs for Python
# export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt 
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt 

STREAMLIT_SERVER_PORT=8501 python -m streamlit run computer_use_demo/streamlit.py > /tmp/streamlit_stdout.log &

echo "✨ Computer Use Demo is ready!"
echo "➡️  Open http://localhost:8080 in your browser to begin"

# Start firefox to create an initial profile, so we can copy the cert to the firefox profile
/usr/bin/firefox-esr --headless &
FIREFOX_PID=$!

sleep 2

PROFILE_DIR=$(find ~/.mozilla/firefox* -name "cert9.db" | head -n 1 | xargs dirname) && \
    certutil -A -n "mitmproxy" -t "CT,C," -i /usr/local/share/ca-certificates/mitmproxy-ca-cert.crt -d $PROFILE_DIR

kill $FIREFOX_PID

# Keep the container running
tail -f /dev/null