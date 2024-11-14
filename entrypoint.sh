#!/bin/bash
set -e

# Function to retrieve service IPs
get_service_ip() {
    SERVICE_NAME=$1
    getent hosts $SERVICE_NAME | awk '{ print $1 }'
}

# Retrieve IPs for mitmproxy and test-web-server
MITMPROXY_IP=$(get_service_ip mitmproxy)
TESTWEB_IP=$(get_service_ip test-web-server)

echo "MITMPROXY_IP: $MITMPROXY_IP"
echo "TESTWEB_IP: $TESTWEB_IP"

# Exclude traffic destined to mitmproxy (to prevent loops)
sudo iptables -t nat -A OUTPUT -d $MITMPROXY_IP -j RETURN

# Redirect outgoing HTTP traffic to mitmproxy
sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to-destination $MITMPROXY_IP:8082

# Redirect outgoing HTTPS traffic to mitmproxy
sudo iptables -t nat -A OUTPUT -p tcp --dport 443 -j DNAT --to-destination $MITMPROXY_IP:8082

# Redirect traffic to test-web-server:5000 through mitmproxy
sudo iptables -t nat -A OUTPUT -p tcp -d $TESTWEB_IP --dport 5000 -j DNAT --to-destination $MITMPROXY_IP:8082

# Run the original command as computeruse user
exec /original-entrypoint.sh "$@"
