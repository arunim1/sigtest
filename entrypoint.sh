#!/bin/bash
set -e

# Function to retrieve service IPs
get_service_ip() {
    SERVICE_NAME=$1
    getent hosts $SERVICE_NAME | awk '{ print $1 }'
}

# Retrieve IPs for nginx-proxy and mitmproxy
MITMPROXY_IP=$(get_service_ip mitmproxy)
echo "MITMPROXY_IP: $MITMPROXY_IP"

# Exclude traffic destined to mitmproxy (to prevent loops)
sudo iptables -t nat -A OUTPUT -d $MITMPROXY_IP -j RETURN

# also http
sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to-destination $MITMPROXY_IP:8082

# Redirect outgoing HTTPS traffic to mitmproxy
sudo iptables -t nat -A OUTPUT -p tcp --dport 443 -j DNAT --to-destination $MITMPROXY_IP:8082

# Run the original command as computeruse user
exec /original-entrypoint.sh "$@"
