FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg curl

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Auto update yt-dlp on container start
CMD pip install --upgrade yt-dlp && python bot.py
