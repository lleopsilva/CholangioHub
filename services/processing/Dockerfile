FROM python:3.13-slim

WORKDIR /app

# PySpark needs a JRE
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-21-jre-headless \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64

# Copy shared package and processing sources from workspace root
COPY shared ./shared
COPY services/processing/pyproject.toml ./pyproject.toml

RUN pip install --upgrade pip \
    && pip install ./shared

# Copy app sources (do not install the package to avoid name collisions)
COPY services/processing/app ./app

EXPOSE 8200

# Install runtime dependencies
# Note: on first run, Spark downloads hadoop-aws/aws-java-sdk-bundle from Maven
# (spark.jars.packages in build_spark_session) - requires outbound internet
# the first time; jars are cached under ~/.ivy2 after that.
RUN pip install pyspark "uvicorn[standard]" fastapi

CMD ["uvicorn", "app.web:app", "--host", "0.0.0.0", "--port", "8200"]
