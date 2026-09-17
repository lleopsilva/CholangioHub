FROM python:3.12-slim

WORKDIR /app

# Copy requirements and app from workspace root
COPY apps/dashboard/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/dashboard/app ./app

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
