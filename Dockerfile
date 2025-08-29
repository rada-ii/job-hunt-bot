FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    unzip \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE $PORT

CMD streamlit run dashboard/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true