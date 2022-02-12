# Access the API spec here
https://flourish-iot.github.io/Flourish-API/spec/

# Getting Started

# Deployment
Create a .env file:
```
POSTGRES_PASSWORD=YOUR_PASSWORD
```
Run `docker-compose --env-file ./.env run --service-ports flourish flourish-db`