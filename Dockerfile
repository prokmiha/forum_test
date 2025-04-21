FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "forum/manage.py", "runserver", "0.0.0.0:8000"]