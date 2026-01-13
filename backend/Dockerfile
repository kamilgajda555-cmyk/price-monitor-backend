FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright dependencies
RUN apt-get update && apt-get install -y \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir email-validator>=2.1.0 dnspython>=2.3.0 && \
    pip install --no-cache-dir -r requirements.txt

# Verify email-validator installation
RUN python -c "import email_validator; print('email-validator installed successfully')"

# Install Playwright browsers
RUN playwright install chromium --with-deps

# Copy application code
COPY . .

# Create migrations directory
RUN mkdir -p /app/migrations

# Expose port
EXPOSE 8000

# Start command with database initialization
CMD if [ "$RENDER_SERVICE_TYPE" = "web" ]; then \
        python -c "from app.models.database import engine, Base; Base.metadata.create_all(bind=engine)" && \
        python init_db.py && \
        uvicorn app.main:app --host 0.0.0.0 --port $PORT; \
    else \
        exec "$@"; \
    fi
