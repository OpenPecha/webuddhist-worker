# WebBuddhist Worker API

This is the worker backend API for the WebBuddhist application.

## Installation

Follow these steps to set up the project on your local machine:

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/webuddhist-worker.git
    ```
2. Navigate to the project directory:
    ```sh
    cd webuddhist-worker
    ```
3. Install the dependencies:
    ```sh
    poetry install
    ```

## Database Setup

This worker backend shares the same databases as `app-pecha-backend`. Ensure the databases are running:

1. Navigate to the app-pecha-backend local setup directory:
    ```sh
    cd ../app-pecha-backend/local_setup
    ```
2. Start the databases using Docker (if not already running):
    ```sh
    docker-compose up -d
    ```
3. Return to webuddhist-worker directory:
    ```sh
    cd ../../webuddhist-worker
    ```
4. Apply database migrations:
    ```sh
    poetry run alembic upgrade head
    ```

## Running the Application

1. Start the FastAPI development server:
    ```sh
    poetry run uvicorn worker_api.app:api --port 8001 --reload
    ```

The application will be available at `http://127.0.0.1:8001/`.

## API Documentation

You can access the Swagger UI for the API documentation at `http://127.0.0.1:8001/docs`.

## Running Tests

To run tests, execute the following command:
```sh
poetry run pytest
```

To check the coverage:
```sh
poetry run pytest --cov=worker_api
```
```sh
poetry run coverage html 
```

Open the coverage report:
```sh
open htmlcov/index.html  
```

## Alembic Commands

Alembic is used for handling database migrations. Here are some common commands:

1. Create a new migration:
    ```sh
    poetry run alembic revision --autogenerate -m "description of migration"
    ```

2. Apply the latest migrations:
    ```sh
    poetry run alembic upgrade head
    ```

3. Downgrade to a previous migration:
    ```sh
    poetry run alembic downgrade -1
    ```

4. View the current migration history:
    ```sh
    poetry run alembic history
    ```

5. Show the current migration state:
    ```sh
    poetry run alembic current
    ```

## Shared Infrastructure

This worker backend shares the following infrastructure with `app-pecha-backend`:
- PostgreSQL database (port 5434)
- MongoDB database (port 27017)
- Redis/Dragonfly cache (port 6379)
- Elasticsearch (port 9200)

Both backends can run simultaneously:
- `app-pecha-backend`: http://127.0.0.1:8000
- `webuddhist-worker`: http://127.0.0.1:8001

## Transferring Endpoints

When transferring endpoints from `app-pecha-backend`:
1. Copy the relevant models, services, repositories, and views
2. Update imports to use `worker_api` instead of `pecha_api`
3. Add model imports to `migrations/env.py` for Alembic
4. Add document models to `worker_api/db/mongo_database.py` for Beanie
5. Include routers in `worker_api/app.py`
6. Run migrations if needed
7. Update tests accordingly
