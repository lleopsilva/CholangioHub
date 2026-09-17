FROM python:3.12-slim

WORKDIR /app

# Copy shared package and API sources from the workspace root (build context is repo root)
COPY shared ./shared
COPY apps/api/pyproject.toml ./pyproject.toml

RUN pip install --upgrade pip \
    && pip install ./shared

# Install API package
COPY apps/api ./app_src
RUN pip install ./app_src

COPY apps/api/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]