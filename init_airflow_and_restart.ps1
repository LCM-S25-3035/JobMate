# Initialize Airflow DB
docker exec -i jobmate-airflow-webserver-1 airflow db init

# Restart all services to apply changes
docker-compose restart
