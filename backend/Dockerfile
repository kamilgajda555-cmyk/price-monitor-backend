FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies with font packages
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libglib2.0-0 \
    fonts-liberation \
    fonts-noto-color-emoji \
    fonts-unifont \
    libxshmfence1 \
    libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Upgrade pip and install email-validator FIRST (critical dependency)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir email-validator>=2.1.0 dnspython>=2.3.0

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Verify email-validator is installed
RUN python -c "import email_validator; print('email-validator installed successfully')"

# Install Playwright browsers (without separate install-deps - already handled above)
RUN playwright install chromium --with-deps || playwright install chromium

# Copy application code
COPY . .

# Create directory for migrations
RUN mkdir -p /app/migrations

# Expose port
EXPOSE 8000

# Run database migrations on startup (for web service)
CMD if [ "$RENDER_SERVICE_TYPE" = "web" ]; then \
        python -c "from app.models.database import engine, Base; Base.metadata.create_all(bind=engine)" && \
        uvicorn app.main:app --host 0.0.0.0 --port $PORT; \
    else \
        exec "$@"; \
    fi
