# Price Monitor - System Monitorowania Cen

Profesjonalny system do automatycznego monitorowania cen produktów na różnych platformach (Allegro, Amazon, Empik) oraz u dystrybutorów.

## 🚀 Funkcjonalności

- ✅ Automatyczne sprawdzanie cen z 20+ źródeł
- ✅ Monitoring ~10,000 produktów
- ✅ Sprawdzanie raz dziennie (konfigurowalne)
- ✅ System alertów email
- ✅ Historia cen z wykresami
- ✅ Dashboard z statystykami
- ✅ Export raportów (Excel, CSV, PDF)
- ✅ API REST z dokumentacją
- ✅ Responsywny interfejs webowy

## 📋 Wymagania

- Docker & Docker Compose
- 4GB RAM
- 10GB miejsca na dysku

## 🛠️ Instalacja

### 1. Sklonuj repozytorium

```bash
git clone <repository-url>
cd price-monitor-app
```

### 2. Konfiguracja środowiska

Skopiuj plik przykładowej konfiguracji:

```bash
cp backend/.env.example backend/.env
```

Edytuj `backend/.env` i uzupełnij:

```env
# Database
DATABASE_URL=postgresql://priceuser:pricepass@db:5432/pricedb

# JWT Secret (zmień na własny)
SECRET_KEY=your-super-secret-key-change-this-in-production

# Email (opcjonalne, dla alertów)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
```

### 3. Uruchomienie aplikacji

```bash
docker-compose up -d
```

Aplikacja będzie dostępna pod adresem:
- Frontend: http://localhost
- Backend API: http://localhost/api/v1
- API Docs: http://localhost/docs

### 4. Utworzenie pierwszego użytkownika

```bash
docker-compose exec backend python -c "
from app.models.database import SessionLocal
from app.models.models import User
from app.api.auth import get_password_hash

db = SessionLocal()
user = User(
    email='admin@example.com',
    hashed_password=get_password_hash('admin123'),
    full_name='Admin User',
    is_superuser=True
)
db.add(user)
db.commit()
print('User created: admin@example.com / admin123')
"
```

## 📖 Użytkowanie

### Logowanie

1. Otwórz http://localhost
2. Zaloguj się danymi: `admin@example.com` / `admin123`

### Dodawanie produktów

1. Przejdź do zakładki **Products**
2. Kliknij **+ Add Product**
3. Wypełnij formularz (nazwa, SKU, EAN, cena bazowa)
4. Zapisz produkt

### Konfiguracja źródeł

1. Przejdź do zakładki **Sources**
2. Kliknij **+ Add Source**
3. Skonfiguruj selektory CSS dla scrapingu:

```json
{
  "price_selector": ".price-value",
  "availability_selector": ".stock-status",
  "use_browser": true
}
```

**Przykładowe konfiguracje:**

**Allegro:**
```json
{
  "price_selector": "[data-box-name='Price'] span",
  "availability_selector": "button[data-role='buy-button']",
  "use_browser": true
}
```

**Amazon:**
```json
{
  "price_selector": ".a-price-whole",
  "availability_selector": "#availability",
  "use_browser": true
}
```

**Empik:**
```json
{
  "price_selector": "[data-ta='product-price']",
  "use_browser": true
}
```

### Mapowanie produktów do źródeł

Aby system sprawdzał ceny, musisz połączyć produkty ze źródłami.

**Przez API:**

```bash
curl -X POST http://localhost/api/v1/sources/product-sources/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "source_id": 1,
    "source_url": "https://allegro.pl/oferta/product-123",
    "is_active": true
  }'
```

### Uruchamianie scrapingu

**Ręcznie (wszystkie produkty):**

```bash
docker-compose exec celery_worker celery -A app.tasks.celery_app call app.tasks.scraping_tasks.scrape_all_products
```

**Ręcznie (jeden produkt):**

```bash
docker-compose exec celery_worker celery -A app.tasks.celery_app call app.tasks.scraping_tasks.scrape_product --args='[1, 1]'
```

**Automatycznie:**
System uruchamia scraping automatycznie raz dziennie o 2:00 (konfiguracja w `backend/app/tasks/celery_app.py`)

### Konfiguracja alertów

1. Przejdź do zakładki **Alerts**
2. Kliknij **+ Add Alert**
3. Wybierz produkt i typ alertu:
   - **Price Drop** - spadek ceny poniżej progu
   - **Price Increase** - wzrost ceny powyżej progu
   - **Availability** - zmiana dostępności
   - **Competitor** - cena konkurencji niższa niż Twoja

### Generowanie raportów

1. Przejdź do zakładki **Reports**
2. Wybierz typ raportu i format
3. Kliknij **Generate Report**
4. Raport zostanie pobrany automatycznie

## 🔧 Architektura

```
price-monitor-app/
├── backend/                 # Backend Python/FastAPI
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   ├── scrapers/       # Web scraping
│   │   └── tasks/          # Celery tasks
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Frontend React/TypeScript
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── Dockerfile
├── docker/                 # Docker configs
│   └── nginx.conf
└── docker-compose.yml
```

## 🗄️ Baza danych

### Główne tabele

- **products** - produkty
- **sources** - źródła cen
- **product_sources** - mapowanie produktów do źródeł
- **price_history** - historia cen
- **alerts** - alerty cenowe
- **users** - użytkownicy
- **scrape_jobs** - zadania scrapingu

### Migracje

```bash
# Instalacja Alembic (jeśli potrzebne)
docker-compose exec backend pip install alembic

# Inicjalizacja migracji
docker-compose exec backend alembic init migrations

# Utworzenie migracji
docker-compose exec backend alembic revision --autogenerate -m "Initial migration"

# Zastosowanie migracji
docker-compose exec backend alembic upgrade head
```

## 🔍 API Documentation

API documentation jest dostępna pod adresem: http://localhost/docs

### Główne endpointy

**Autentykacja:**
- POST `/api/v1/auth/register` - rejestracja
- POST `/api/v1/auth/login` - logowanie
- GET `/api/v1/auth/me` - dane użytkownika

**Produkty:**
- GET `/api/v1/products/` - lista produktów
- POST `/api/v1/products/` - dodaj produkt
- GET `/api/v1/products/{id}` - szczegóły produktu
- PUT `/api/v1/products/{id}` - aktualizuj produkt
- DELETE `/api/v1/products/{id}` - usuń produkt

**Źródła:**
- GET `/api/v1/sources/` - lista źródeł
- POST `/api/v1/sources/` - dodaj źródło
- GET `/api/v1/sources/product-sources/` - mapowania

**Alerty:**
- GET `/api/v1/alerts/` - lista alertów
- POST `/api/v1/alerts/` - dodaj alert

**Raporty:**
- POST `/api/v1/reports/generate` - generuj raport

## 📊 Monitoring

### Logi

```bash
# Backend logs
docker-compose logs -f backend

# Celery worker logs
docker-compose logs -f celery_worker

# Celery beat logs (scheduler)
docker-compose logs -f celery_beat

# Wszystkie logi
docker-compose logs -f
```

### Status Celery

```bash
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect active
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect stats
```

## 🚀 Wdrożenie produkcyjne

### 1. Zmień secrety w `.env`

```env
SECRET_KEY=<wygeneruj-długi-losowy-klucz>
DATABASE_PASSWORD=<silne-hasło>
```

### 2. Konfiguracja domenowa

Edytuj `docker/nginx.conf` i zmień `server_name` na swoją domenę.

### 3. SSL/TLS (Let's Encrypt)

```bash
# Zainstaluj Certbot
apt-get install certbot python3-certbot-nginx

# Uzyskaj certyfikat
certbot --nginx -d your-domain.com
```

### 4. Backup bazy danych

```bash
# Backup
docker-compose exec db pg_dump -U priceuser pricedb > backup.sql

# Restore
docker-compose exec -T db psql -U priceuser pricedb < backup.sql
```

## 🐛 Troubleshooting

### Problem z Playwright

```bash
docker-compose exec backend playwright install chromium
docker-compose restart backend celery_worker
```

### Problem z bazą danych

```bash
# Reset bazy
docker-compose down -v
docker-compose up -d
```

### Problem z uprawnieniami

```bash
chmod -R 755 backend/
chmod -R 755 frontend/
```

## 📝 Licencja

MIT License

## 🤝 Wsparcie

W razie problemów:
1. Sprawdź logi: `docker-compose logs`
2. Sprawdź status kontenerów: `docker-compose ps`
3. Zrestartuj system: `docker-compose restart`

## 🔄 Aktualizacje

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

---

**Autor:** Price Monitor Team  
**Wersja:** 1.0.0  
**Data:** 2024
