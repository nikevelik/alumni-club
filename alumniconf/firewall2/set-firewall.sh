#!/bin/bash
gcloud compute firewall-rules update default-allow-http --source-ranges="${1}/32"

