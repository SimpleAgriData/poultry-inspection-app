# SiAD Stallkarte Frontend

This mobile-first web application serves as the frontend for the SiAD Stallkarte application. It is designed to provide users with an intuitive interface to manage and view Stallkarten.

## Development Setup

### Requirements

- [Node.js](https://nodejs.org/) (version 22 or higher)
- [make](https://www.gnu.org/software/make/) (optional, for using the Makefile)

### Project setup

Copy the `.env.example` file to `.env` and adjust any necessary environment variables. The default should work with the
production auth provider and the development backend (http://localhost:8000).

To install dependencies, run:

```bash
npm install
```

### Running the Application
To start the development server, run:

```bash
npm run dev
```

Access: [http://localhost:3000/](http://localhost:3000/)

### Makefile commands

For quality assurance, run:

```bash
make qa
```

To format the code, run:

```bash
make format
```

### API Schema
The frontend uses a generated API schema based on the OpenAPI specification provided by the backend. The schema should
stay up-to-date with the backend API, and any changes to the API should be reflected in the schema.

To generate the API schema, run:

```bash
make generate-api-schema
```

## Building for Production
To build the application for production, run:

```bash
npm run build

or

make build
```


