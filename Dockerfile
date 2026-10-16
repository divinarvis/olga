FROM python:3.11-slim
RUN apt-get update && apt-get install -y ffmpeg curl unzip
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"
WORKDIR /app
COPY . .
RUN pip install -U yt-dlp && pip install -r requirements.txt
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:10000"]
