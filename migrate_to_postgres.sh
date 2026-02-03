#!/bin/bash

# Script to migrate data from SQLite to PostgreSQL

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

if [ ! -f "db.sqlite3" ]; then
    echo -e "${RED}Error: db.sqlite3 not found!${NC}"
    exit 1
fi

echo -e "${GREEN}1. Dumping data from SQLite...${NC}"
# Temporarily ensure we are using SQLite (unset DB_ENGINE if set in session, though .env matters most)
# Ideally, we run this BEFORE modifying .env, but if .env is already modified, we might fail.
# So we assume .env is currently pointing to SQLite or we force it.

# Running dumpdata
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data_dump.json

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Data dumped successfully to data_dump.json${NC}"
else
    echo -e "${RED}Failed to dump data! Check if you can run manage.py${NC}"
    exit 1
fi

echo -e "${GREEN}2. Running PostgreSQL Setup (Installation & Config)...${NC}"
chmod +x setup_postgres.sh
./setup_postgres.sh

echo -e "${GREEN}3. Applying Migrations to new PostgreSQL DB...${NC}"
python manage.py migrate

echo -e "${GREEN}4. Loading Data into PostgreSQL...${NC}"
python manage.py loaddata data_dump.json

if [ $? -eq 0 ]; then
    echo -e "${GREEN}SUCCESS! Migrated to PostgreSQL.${NC}"
    echo -e "${GREEN}Restarting Service...${NC}"
    sudo systemctl restart nbr-gestao
else
    echo -e "${RED}Failed to load data!${NC}"
    # Revert hint?
fi
