FROM python:3.12-slim

# Configure Poetry
ENV POETRY_VERSION=1.8.3
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Install Poetry
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        bash \
        gcc python3-dev \
        curl && \
    python3 -m venv $POETRY_VENV && \
    $POETRY_VENV/bin/pip install -U pip setuptools && \
    $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add Poetry venv to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

# Set the working directory
WORKDIR /app

# Copy Poetry configuration files
COPY pyproject.toml ./
COPY poetry.lock ./

# Install dependencies using Poetry inside configured venv
RUN poetry install --no-cache --no-interaction

# Copy the source code and unit tests
COPY hashmap /app/hashmap/
COPY tests /app/tests/
