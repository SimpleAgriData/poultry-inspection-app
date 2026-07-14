FROM python:3.14-slim-bookworm

ARG version
ARG gitVersion

RUN if [ -z "$version" ]; then \
    	echo "version is not set"; \
    	exit 1; \
    fi
RUN if [ -z "$gitVersion" ]; then \
    	echo "gitVersion is not set"; \
    	exit 1; \
		fi


COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /stallkarte

COPY ./pyproject.toml ./uv.lock ./Makefile /stallkarte/

RUN uv sync

# This is done after installing dependencies to leverage Docker layer caching
COPY ./app /stallkarte/app

COPY ./res/stallkarte_template.xlsx /stallkarte/res/stallkarte_template.xlsx

ENV STALLKARTE_TEMPLATE_FILE="/stallkarte/res/stallkarte_template.xlsx"
ENV STALLKARTE_TEMPLATE_FILE_DEFAULT_WORKSHEET="Stallkarte TEMPLATE"
ENV APP_VERSION=${version}
ENV APP_GIT_VERSION=${gitVersion}

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
