FROM apache/airflow:2.7.3

USER root
RUN python -m pip install --upgrade pip \
    && python -m pip install "psycopg[binary]" psycopg2-binary

USER airflow
