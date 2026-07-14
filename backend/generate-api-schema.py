import argparse
import json
import sys

from fastapi import FastAPI

from app.router import router

parser = argparse.ArgumentParser(description="Generate OpenAPI schema for the API")
parser.add_argument(
    "--output",
    "-o",
    nargs="?",
    default=None,
    help="Output file for the OpenAPI schema (defaults to stdout)",
)

if __name__ == "__main__":
    args = parser.parse_args()

    output = args.output

    app = FastAPI()
    app.include_router(router)

    schema = app.openapi()
    schema_str = json.dumps(schema, indent=2)

    if output:
        with open(output, "w") as f:
            f.write(schema_str)
    else:
        sys.stdout.write(schema_str)
