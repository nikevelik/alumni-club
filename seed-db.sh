#!/bin/bash
# Seeds the database with a test table and a single row.
# Run from the repo root: bash etc/seed-db.sh

set -e

cd ~/alumni-club

if [ ! -f .env ]; then
  echo "Error: .env file not found."
  exit 1
fi

source .env

echo "Waiting for database to be ready..."
until docker exec lamp_db mariadb -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1" &>/dev/null; do
  sleep 1
done

docker exec -i lamp_db mariadb -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" <<SQL
CREATE TABLE IF NOT EXISTS test (
  message VARCHAR(255) NOT NULL
);

DELETE FROM test;
INSERT INTO test (message) VALUES ('Hello from the database!');
SQL

echo "Done."
