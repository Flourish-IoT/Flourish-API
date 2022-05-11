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

Updating the server:
```
docker-compose rm -s flourish
docker-compose --env-file ./.env up -d --build flourish
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

# Alembic
All changes to the database should be generated by the SQLAlchemy models and Alembic

Creating a new revision (Always check the migration script before running against the database):
```
alembic revision --autogenerate -m "REVISION_NAME"
```

Upgrading the database (local):
```
alembic upgrade head
```

Upgrading the database:
```
alembic -x database_uri='DATABASE URI' upgrade head
```