#!/bin/bash
set -e

cd ~/alumni-club

if [ ! -f .env ]; then
  echo "Error: .env file not found. Create it before running this script."
  exit 1
fi

docker-compose down
git pull
docker-compose up -d

