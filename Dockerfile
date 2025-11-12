FROM python:3.11-slim

WORKDIR /app

# Install dependencies + Chrome (same as above...)
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl ca-certificates \
    fonts-liberation libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcairo2 libcups2 libdbus-1-3 \
    libgbm1 libglib2.0-0 libgtk-3-0 libnss3 \
    libx11-6 libxcomposite1 libxcursor1 libxdamage1 \
    libxrandr2 libxrender1 xdg-utils \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get update && apt-get install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb && rm -rf /var/lib/apt/lists/*

RUN CHROME_VER=$(google-chrome --version | awk '{print $3}' | cut -d. -f1) \
    && wget -q "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_VER" -O /tmp/ver || echo "142" > /tmp/ver \
    && VER=$(cat /tmp/ver) \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/$VER/linux64/chromedriver-linux64.zip" -O /tmp/cd.zip \
    && unzip -q /tmp/cd.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver && rm -rf /tmp/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p logs debug

EXPOSE 8080
ENV PYTHONUNBUFFERED=1

# Use exec form with PORT defaulting to 8080
ENTRYPOINT ["sh", "-c"]
CMD ["gunicorn app:app --bind 0.0.0.0:${PORT:-8080} --timeout 300 --workers 1"]
