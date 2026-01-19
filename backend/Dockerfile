FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright system dependencies
RUN apt-get update && apt-get install -y \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxkbcommon0 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    fonts-noto-color-emoji \
    xdg-utils \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir email-validator>=2.1.0 dnspython>=2.3.0 && \
    pip install --no-cache-dir -r requirements.txt

# Verify email-validator installation
RUN python -c "import email_validator; print('email-validator installed successfully')"

# Install Playwright browsers (without --with-deps since we already installed deps)
RUN playwright install chromium

# Copy application code
COPY . .

# Create migrations directory
RUN mkdir -p /app/migrations

# Expose port
EXPOSE 8000

# Start command with database initialization
CMD if [ "$RENDER_SERVICE_TYPE" = "web" ]; then \
        bash backend/run_migrations.sh && \
        uvicorn app.main:app --host 0.0.0.0 --port $PORT; \
    else \
        exec "$@"; \
    fi
