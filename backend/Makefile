PACKAGE = app
TEST_DIR := tests
PYTHON_DIRS := $(PACKAGE) $(TEST_DIR)


qa: analyze typecheck test

analyze:
	@echo "Running code analysis..."
	@uv run ruff check $(PYTHON_DIRS)

build-docker:
	@echo "Building Docker image..."
	$(eval IMAGE_VERSION=$(or $(VERSION), latest))
	$(eval VERSION=$(shell git tag --points-at HEAD))
	$(eval VERSION=$(or $(VERSION), (version unavailable)))
	$(eval GIT_VERSION=$(shell git rev-parse HEAD))


	@docker build \
		--build-arg version="$(VERSION)" \
		--build-arg gitVersion="$(GIT_VERSION)" \
		-t siad-stallkarte-backend:$(IMAGE_VERSION) \
		-f Dockerfile .

format:
	@echo "Formatting code..."
	@uv run ruff format $(PYTHON_DIRS)
	@uv run ruff check --fix $(PYTHON_DIRS)

lock:
	@echo "Updating dependency lock..."
	@uv run uv lock

typecheck:
	@echo "Running type checking..."
	@uv run ty check $(PYTHON_DIRS)

test:
	@echo "Running tests..."
	@uv run pytest $(TEST_DIR)

generate-api-schema:
	@uv run generate-api-schema.py

seed-test-data:
	@uv run seed-test-data.py

.PHONY: analyze \
				build-docker \
				format \
				lock \
				qa \
				test \
				typecheck \
				generate-api-schema \
				seed-test-data
