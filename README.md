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

# Testing
To run all tests
```
pytest ./src [--db]
```

To run unit tests
```
pytest ./src/tests/unit [--db]
```
To run integration tests
```
pytest ./src/tests/integration [--db]
```

## Options:

	--db		Run tests that require a database connection