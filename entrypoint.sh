#!/bin/bash
set -e

# Switch to root to set up iptables
NGINX_IP=$(getent hosts nginx-proxy | awk '{ print $1 }')
echo "NGINX_IP: $NGINX_IP"
sudo iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to-destination $NGINX_IP:80
sudo iptables -t nat -A OUTPUT -p tcp --dport 443 -j DNAT --to-destination $NGINX_IP:80

# Run the original command as computeruse user
exec /original-entrypoint.sh "$@"
