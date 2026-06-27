#!/bin/bash
# Updates the GCP firewall rule for port 80 to only allow specific IPs.
# Usage: add IPs to allowed-ips.txt (one per line), then run this script once.

RULE_NAME="default-allow-http"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IP_FILE="$SCRIPT_DIR/allowed-ips.txt"

if [ ! -f "$IP_FILE" ]; then
  echo "Error: $IP_FILE not found."
  exit 1
fi

# Read IPs, strip comments and blank lines
mapfile -t ALLOWED_IPS < <(grep -v '^\s*#' "$IP_FILE" | grep -v '^\s*$')

if [ ${#ALLOWED_IPS[@]} -eq 0 ]; then
  echo "Error: no IPs found in $IP_FILE."
  exit 1
fi

RANGES=$(IFS=,; echo "${ALLOWED_IPS[*]}")

echo "Updating firewall rule '$RULE_NAME' to allow: $RANGES"
gcloud compute firewall-rules update "$RULE_NAME" --source-ranges="$RANGES"
echo "Done."

