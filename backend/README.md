# Run Stallkarte Backend

This is the backend for the SIAD Stallkarte project, which provides an API for managing and retrieving information about
Stallkarten. The backend is built using FastAPI and is designed to be easily deployable and scalable.

The core concepts of the backend include:

- **Domain Driven Design (DDD)**: The codebase is organized around the core domain concepts of the application, such as
	`Stallkarte`, `User`, and `AgriculturalHolding`.
- **Command Query Responsibility Segregation (CQRS)**: The application separates read and write operations, allowing for
	scalability and maintainability. HTTP-verbs other than `GET` for queries and `POST` for commands are not used, to keep
	the API simple and consistent.
- **Event Sourcing (Stallkate only)**: The state of `Stallkarte` entities is stored as a sequence of events, allowing
	for auditability and the ability to reconstruct the state at any point in time. This keeps the read-model dynamic and
	extensible.
- **Strict Semantic Responsibility**: Classes may seem to have duplicate code, but they are designed to have a single
	responsibility and to be easily testable. For example, just because the Database Model has the same fields as the
	Domain Model,
	doesn't mean they are the same thing. The Database Model is responsible for persistence, while the Domain Model is
	responsible for business logic and rules.

## Development Setup

### Requirements

- [uv](https://github.com/astral-sh/uv) (for managing Python installations, venvs, and dependencies)
- [make](https://www.gnu.org/software/make/) (for QA, formatting, and cleaning)
- [docker](https://www.docker.com/) (for development database and Docker build)

### Getting the project running

#### Project setup

Copy the `.env.example` file to `.env` and adjust any necessary environment variables. The default should work with the
production auth provider and the development database from below.

To install dependencies and set up the virtual environment, run:

```bash
uv sync
```

#### Setup the development database

You can use the [`docker-compose.yml`](./docker-compose.yml) file to start a local PostgreSQL database.
Simply run:

```bash
docker compose up -d
```

This should work out of the box with the default environment variables in the `.env` file.

#### Starting the development server

The development server can be started using `uv` and `uvicorn`, even if the virtual environment is not activated:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Access `http://localhost:8000`

### Makefile commands

For quality assurance, run:

```bash
make qa
```

To format the code, run:

```bash
make format
```

## Build with Docker

```bash
make docker-build

docker run -p 8000:8000 siad-stallkarte-backend:latest
```

Access [http://localhost:8000/](http://localhost:8000/)

## Documentation

### Swagger UI

Open the browser under [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs)

### ReDocs UI

Open the browser under [http://0.0.0.0:8000/redoc](http://0.0.0.0:8000/redoc)
