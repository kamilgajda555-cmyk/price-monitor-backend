# 🚀 Wdrożenie na Render.com - Przewodnik Krok po Kroku

## 📋 Wymagania

- Konto GitHub
- Konto Render.com (darmowe)
- Aplikacja na Netlify (już masz ✅)

---

## Krok 1: Przygotowanie repozytorium GitHub

### 1.1 Utwórz nowe repozytorium na GitHub

1. Idź na https://github.com/new
2. Nazwa: `price-monitor-backend`
3. Widoczność: Private (zalecane) lub Public
4. **NIE** zaznaczaj "Initialize with README"
5. Kliknij **Create repository**

### 1.2 Wypakuj i prześlij kod

```bash
# Rozpakuj aplikację
tar -xzf price-monitor-app.tar.gz
cd price-monitor-app

# Zamień Dockerfile na wersję dla Render
cp /path/to/backend-Dockerfile-render backend/Dockerfile

# Inicjalizuj git
git init
git add .
git commit -m "Initial commit - Price Monitor Backend"

# Dodaj remote (zamień na swój URL)
git remote add origin https://github.com/TWOJ-USERNAME/price-monitor-backend.git

# Wyślij kod
git branch -M main
git push -u origin main
```

---

## Krok 2: Konfiguracja na Render.com

### 2.1 Utwórz konto i połącz GitHub

1. Idź na https://render.com
2. Kliknij **Get Started for Free**
3. Zaloguj się przez GitHub
4. Autoryzuj Render do dostępu do repozytoriów

### 2.2 Utwórz PostgreSQL Database

1. W Dashboard kliknij **New +** → **PostgreSQL**
2. Wypełnij:
   - **Name**: `price-monitor-db`
   - **Database**: `pricedb`
   - **User**: `priceuser`
   - **Region**: Frankfurt (lub najbliższy)
   - **Plan**: Free
3. Kliknij **Create Database**
4. **WAŻNE**: Zapisz **Internal Database URL** (będzie potrzebny)

### 2.3 Utwórz Redis

1. Kliknij **New +** → **Redis**
2. Wypełnij:
   - **Name**: `price-monitor-redis`
   - **Region**: Frankfurt
   - **Plan**: Free
   - **Maxmemory Policy**: allkeys-lru
3. Kliknij **Create Redis**
4. **WAŻNE**: Zapisz **Internal Redis URL**

### 2.4 Utwórz Web Service (Backend API)

1. Kliknij **New +** → **Web Service**
2. Wybierz **Build and deploy from a Git repository**
3. Wybierz swoje repo: `price-monitor-backend`
4. Wypełnij:
   - **Name**: `price-monitor-backend`
   - **Region**: Frankfurt
   - **Branch**: main
   - **Root Directory**: (puste, jeśli backend w głównym katalogu)
   - **Runtime**: Docker
   - **Instance Type**: Free
5. Kliknij **Advanced**

#### Environment Variables dla Backend:

Dodaj te zmienne środowiskowe:

```env
# Database (użyj Internal Database URL z kroku 2.2)
DATABASE_URL=postgresql://priceuser:PASSWORD@HOST/pricedb

# Redis (użyj Internal Redis URL z kroku 2.3)
REDIS_URL=redis://HOST:6379

# JWT Secret (wygeneruj losowy string)
SECRET_KEY=WYGENERUJ-LOSOWY-BEZPIECZNY-KLUCZ-128-ZNAKOW

# JWT Config
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_V1_STR=/api/v1
PROJECT_NAME=Price Monitor
DEBUG=False

# CORS - WAŻNE! Dodaj swój URL Netlify
BACKEND_CORS_ORIGINS=https://twoja-app.netlify.app,http://localhost:3000

# Scraping
SCRAPING_DELAY=2
SCRAPING_TIMEOUT=30
MAX_RETRIES=3
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Email (opcjonalne)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=twoj-email@gmail.com
SMTP_PASSWORD=haslo-aplikacji
SMTP_FROM=twoj-email@gmail.com
```

6. Kliknij **Create Web Service**
7. Poczekaj na deployment (~10 minut)
8. **Zapisz URL backendu** (np. `https://price-monitor-backend.onrender.com`)

### 2.5 Utwórz Worker (Celery Worker)

1. Kliknij **New +** → **Background Worker**
2. Wybierz to samo repo: `price-monitor-backend`
3. Wypełnij:
   - **Name**: `price-monitor-celery-worker`
   - **Region**: Frankfurt
   - **Runtime**: Docker
   - **Docker Command**: 
     ```
     celery -A app.tasks.celery_app worker --loglevel=info
     ```
   - **Instance Type**: Free

4. Dodaj **te same Environment Variables** co w kroku 2.4
5. Kliknij **Create Background Worker**

### 2.6 Utwórz Worker (Celery Beat - Scheduler)

1. Kliknij **New +** → **Background Worker**
2. Wybierz to samo repo: `price-monitor-backend`
3. Wypełnij:
   - **Name**: `price-monitor-celery-beat`
   - **Region**: Frankfurt
   - **Runtime**: Docker
   - **Docker Command**: 
     ```
     celery -A app.tasks.celery_app beat --loglevel=info
     ```
   - **Instance Type**: Free

4. Dodaj **te same Environment Variables** co w kroku 2.4
5. Kliknij **Create Background Worker**

---

## Krok 3: Konfiguracja Frontendu na Netlify

### 3.1 Zaktualizuj zmienne środowiskowe na Netlify

1. Idź do Dashboard Netlify
2. Wybierz swoją aplikację
3. **Site settings** → **Environment variables**
4. Dodaj:
   ```
   REACT_APP_API_URL=https://price-monitor-backend.onrender.com
   ```
5. **Save**

### 3.2 Redeploy frontendu

1. W Netlify: **Deploys** → **Trigger deploy** → **Deploy site**
2. Poczekaj ~2 minuty na rebuild

---

## Krok 4: Utworzenie pierwszego użytkownika

### 4.1 Przez Render Shell

1. W Render Dashboard → Wybierz **price-monitor-backend**
2. Kliknij **Shell** (w prawym górnym rogu)
3. Wykonaj:

```bash
python -c "
from app.models.database import SessionLocal
from app.models.models import User
from app.api.auth import get_password_hash

db = SessionLocal()
user = User(
    email='admin@example.com',
    hashed_password=get_password_hash('admin123'),
    full_name='Administrator',
    is_superuser=True
)
db.add(user)
db.commit()
print('✅ User created: admin@example.com / admin123')
"
```

### 4.2 Alternatywnie: przez API

```bash
curl -X POST https://price-monitor-backend.onrender.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123",
    "full_name": "Administrator"
  }'
```

---

## Krok 5: Testowanie

### 5.1 Sprawdź backend

```bash
# Health check
curl https://price-monitor-backend.onrender.com/health

# API docs
# Otwórz w przeglądarce:
https://price-monitor-backend.onrender.com/docs
```

### 5.2 Sprawdź frontend

1. Otwórz swoją aplikację Netlify: `https://twoja-app.netlify.app`
2. Zaloguj się:
   - Email: `admin@example.com`
   - Hasło: `admin123`

### 5.3 Sprawdź logi

W Render Dashboard:
- **price-monitor-backend** → **Logs** (sprawdź czy API działa)
- **price-monitor-celery-worker** → **Logs** (sprawdź workera)
- **price-monitor-celery-beat** → **Logs** (sprawdź schedulera)

---

## 🎉 Gotowe!

Twoja aplikacja działa na:
- **Frontend**: `https://twoja-app.netlify.app` (Netlify)
- **Backend API**: `https://price-monitor-backend.onrender.com` (Render)
- **Baza danych**: PostgreSQL na Render
- **Redis**: Redis na Render
- **Workers**: 2 Celery workers na Render

---

## 📊 Architektura wdrożenia

```
┌─────────────────────────────────────────────────┐
│  Netlify (Frontend)                             │
│  https://twoja-app.netlify.app                  │
│  ├── React App                                  │
│  └── Static Files                               │
└────────────────┬────────────────────────────────┘
                 │ API Calls
                 ▼
┌─────────────────────────────────────────────────┐
│  Render.com (Backend)                           │
│  https://price-monitor-backend.onrender.com     │
│                                                  │
│  ├── Web Service (FastAPI)                      │
│  │   └── REST API + Auth                        │
│  │                                               │
│  ├── PostgreSQL Database (Free)                 │
│  │   └── Products, Prices, Users                │
│  │                                               │
│  ├── Redis (Free)                               │
│  │   └── Celery Queue + Cache                   │
│  │                                               │
│  ├── Celery Worker                              │
│  │   └── Scraping Tasks                         │
│  │                                               │
│  └── Celery Beat                                │
│      └── Scheduler (Daily scraping)             │
└─────────────────────────────────────────────────┘
```

---

## ⚠️ Ważne uwagi o Free Tier

### Render.com Free Tier:
- ✅ 750 godzin/miesiąc na usługę
- ✅ PostgreSQL: 90 dni, potem wymaga karty
- ✅ Redis: 30 dni, potem wymaga karty
- ⚠️ **Aplikacja usypia po 15 min nieaktywności**
- ⚠️ Pierwszy request po uśpieniu: ~30-60 sekund

### Rozwiązania:
1. **Ping service** (utrzymuje aplikację aktywną):
   - Użyj https://uptimerobot.com (darmowy)
   - Pinguj co 10 minut: `https://price-monitor-backend.onrender.com/health`

2. **Upgrade do Paid** ($7/miesiąc):
   - Brak uśpienia
   - Więcej zasobów
   - Stała dostępność

---

## 🔧 Rozwiązywanie problemów

### Problem: Backend nie startuje

**Sprawdź logi:**
```
Render Dashboard → Backend → Logs
```

**Częste przyczyny:**
- Błędny DATABASE_URL
- Błędny REDIS_URL
- Brak zmiennych środowiskowych
- Błąd w kodzie

### Problem: CORS errors

**Sprawdź:**
1. Czy `BACKEND_CORS_ORIGINS` zawiera URL Netlify
2. Format: `https://twoja-app.netlify.app` (bez trailing slash)
3. Redeploy backend po zmianie

### Problem: Worker nie działa

**Sprawdź:**
- Logi workera w Render
- Czy DATABASE_URL i REDIS_URL są poprawne
- Czy Playwright zainstalował się poprawnie

### Problem: Baza danych pusta

**Uruchom migracje:**
```bash
# W Render Shell (Backend)
python -c "from app.models.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

---

## 📞 Potrzebujesz pomocy?

1. Sprawdź logi w Render Dashboard
2. Sprawdź browser console (F12) dla błędów CORS
3. Przetestuj API bezpośrednio: `/docs`
4. Zweryfikuj zmienne środowiskowe

---

## 🚀 Następne kroki

1. **Dodaj produkty** przez interfejs
2. **Skonfiguruj źródła** (Allegro, Amazon, etc.)
3. **Ustaw alerty** cenowe
4. **Przetestuj scraping** ręcznie
5. **Skonfiguruj email** (opcjonalnie)
6. **Dodaj UptimeRobot** ping (zalecane)

---

**Powodzenia z wdrożeniem! 🎉**

Jeśli napotkasz problemy, sprawdź logi w Render Dashboard i przeczytaj sekcję troubleshootingu powyżej.
