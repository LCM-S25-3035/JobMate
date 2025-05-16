#!/bin/bash

# Create necessary directories
mkdir -p logs plugins dags

# Set permissions
chmod -R 777 logs plugins dags

# Start postgres and wait for it to be ready
docker-compose up -d postgres
sleep 10

# Initialize the database
docker-compose run --rm airflow-webserver airflow db init

# Create admin user
docker-compose run --rm airflow-webserver airflow users create \
    --username airflow \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password airflow

# Start all services
docker-compose up -d 