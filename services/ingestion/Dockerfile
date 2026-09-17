FROM python:3.13-slim

WORKDIR /app

# Copy shared package and ingestion sources from workspace root
COPY shared ./shared
COPY services/ingestion/pyproject.toml ./pyproject.toml

RUN pip install --upgrade pip \
    && pip install ./shared

# Copy app sources (do not install the package to avoid name collisions)
COPY services/ingestion/app ./app

EXPOSE 8100

# Install runtime dependencies
RUN pip install fastapi requests minio "uvicorn[standard]"

CMD ["uvicorn", "app.web:app", "--host", "0.0.0.0", "--port", "8100"]
