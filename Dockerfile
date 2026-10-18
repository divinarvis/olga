FROM python:3.10-slim

# Dépendances système
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Port par défaut si non spécifié
ENV PORT=5000
EXPOSE $PORT

# Lancer gunicorn en écoutant sur 0.0.0.0:$PORT
CMD gunicorn --bind 0.0.0.0:$PORT app:app
