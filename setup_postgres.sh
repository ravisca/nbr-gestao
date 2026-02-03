#!/bin/bash

# Configuration
DB_NAME="nbr_gestao"
DB_USER="nbr_user"
DB_PASS="nbr_password_secure" # Change this!
ENV_FILE=".env"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting PostgreSQL Setup...${NC}"

# 1. Install PostgreSQL
echo -e "${GREEN}Installing PostgreSQL packages...${NC}"
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib libpq-dev

# 2. Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 3. Create Database and User
echo -e "${GREEN}Creating Database and User...${NC}"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'UTC';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# 4. Update .env file
echo -e "${GREEN}Updating .env file...${NC}"

# Backup .env
cp $ENV_FILE "${ENV_FILE}.bak"

# Uncomment or Append DB config
# We use sed to uncomment if lines exist, or we just append if not found (simplification: assume they are there from my previous edit or just append)

if grep -q "DB_ENGINE=postgresql" "$ENV_FILE"; then
    sed -i 's/# DB_ENGINE=postgresql/DB_ENGINE=postgresql/' "$ENV_FILE"
    sed -i 's/# DB_NAME=nbr_gestao/DB_NAME=nbr_gestao/' "$ENV_FILE"
    sed -i 's/# DB_USER=nbr_user/DB_USER=nbr_user/' "$ENV_FILE"
    sed -i "s|# DB_PASSWORD=secure_password|DB_PASSWORD=$DB_PASS|g" "$ENV_FILE"
    sed -i 's/# DB_HOST=localhost/DB_HOST=localhost/' "$ENV_FILE"
    sed -i 's/# DB_PORT=5432/DB_PORT=5432/' "$ENV_FILE"
else
    echo "DB_ENGINE=postgresql" >> "$ENV_FILE"
    echo "DB_NAME=$DB_NAME" >> "$ENV_FILE"
    echo "DB_USER=$DB_USER" >> "$ENV_FILE"
    echo "DB_PASSWORD=$DB_PASS" >> "$ENV_FILE"
    echo "DB_HOST=localhost" >> "$ENV_FILE"
    echo "DB_PORT=5432" >> "$ENV_FILE"
fi

echo -e "${GREEN}PostgreSQL installed and configured!${NC}"
echo -e "${GREEN}Next steps:${NC}"
echo "1. Dump your SQLite data: python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json"
echo "2. Run migrations: python manage.py migrate"
echo "3. Load data: python manage.py loaddata data.json"
