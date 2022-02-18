# Access the API spec here
https://flourish-iot.github.io/Flourish-API/spec/

# Getting Started

# Deployment
Create a .env file containing
```
POSTGRES_PASSWORD=YOUR_PASSWORD
```
Run
```
docker-compose --env-file ./.env up flourish-db flourish
```

Run detached
```
docker-compose --env-file ./.env up -d flourish-db flourish
```

Running just the database:
```
docker-compose --env-file ./.env up -d flourish-db
```