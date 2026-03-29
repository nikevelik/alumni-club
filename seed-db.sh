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

CREATE TABLE IF NOT EXISTS users (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  name            VARCHAR(127) CHARACTER SET ascii,
  email           VARCHAR(255) CHARACTER SET ascii,
  password_hash   VARCHAR(255) CHARACTER SET ascii,
  graduation_year SMALLINT,
  field_of_study  VARCHAR(127) CHARACTER SET ascii,
  current_role    VARCHAR(127) CHARACTER SET ascii,
  company         VARCHAR(127) CHARACTER SET ascii,
  location        VARCHAR(127) CHARACTER SET ascii,
  bio             VARCHAR(127) CHARACTER SET ascii,
  profile_picture VARCHAR(255) CHARACTER SET ascii
);

DELETE FROM users;
SQL

docker cp users.csv lamp_db:/tmp/users.csv

docker exec -i lamp_db mariadb -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" <<SQL
LOAD DATA INFILE '/tmp/users.csv'
INTO TABLE users
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(id, name, email, password_hash, graduation_year, field_of_study, current_role, company, location, bio, profile_picture);
SQL

echo "Done."
