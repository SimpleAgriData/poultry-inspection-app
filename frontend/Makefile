qa: analyze typecheck

analyze:
	npm run lint

typecheck:
	npm run typecheck

format:
	npm run format

build:
	npm run build

generate-api-schema:
	@cd ../backend && uv run generate-api-schema.py -o ../frontend/src/services/api/generated/schema.json
	@npx -y openapi-typescript src/services/api/generated/schema.json -o src/services/api/generated/schema.d.ts
	@rm ../frontend/src/services/api/generated/schema.json


.PHONY: qa \
				analyze \
				format \
				build \
				typecheck \
				generate-api-schema
