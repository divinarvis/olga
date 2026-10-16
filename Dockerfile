FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg curl unzip && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL=/root/.deno
ENV PATH=/root/.deno/bin:$PATH
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -U yt-dlp[default,curl-cffi] && pip install --no-cache-dir -r requirements.txt
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000", "--timeout", "120", "--workers", "1"]
