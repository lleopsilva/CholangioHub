#!/bin/sh


set -e



mc alias set local \
http://localhost:${MINIO_PORT} \
${MINIO_ROOT_USER} \
${MINIO_ROOT_PASSWORD}



mc mb --ignore-existing local/bronze

mc mb --ignore-existing local/silver

mc mb --ignore-existing local/gold

mc mb --ignore-existing local/documents

mc mb --ignore-existing local/research



echo "CholangioHub buckets initialized"