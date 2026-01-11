# 🚀 Szybki Start - Price Monitor

Ten przewodnik pomoże Ci uruchomić aplikację w 10 minut.

## Krok 1: Wymagania

Upewnij się, że masz zainstalowane:
- **Docker** (wersja 20.10+)
- **Docker Compose** (wersja 2.0+)

Sprawdź wersje:
```bash
docker --version
docker-compose --version
```

## Krok 2: Rozpakowanie

```bash
tar -xzf price-monitor-app.tar.gz
cd price-monitor-app
```

## Krok 3: Konfiguracja

Skopiuj przykładowy plik konfiguracyjny:
```bash
cp backend/.env.example backend/.env
```

**Minimalna konfiguracja (działa od razu):**
Plik `backend/.env` jest już skonfigurowany z domyślnymi wartościami.

**Opcjonalna konfiguracja email** (jeśli chcesz alerty):
Edytuj `backend/.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=twoj-email@gmail.com
SMTP_PASSWORD=haslo-aplikacji
SMTP_FROM=twoj-email@gmail.com
```

## Krok 4: Uruchomienie

### Sposób 1: Użyj Makefile (zalecane)

```bash
make install
```

To polecenie:
- Zbuduje wszystkie kontenery
- Uruchomi wszystkie serwisy
- Utworzy użytkownika admin
- Pokaże dane logowania

### Sposób 2: Manualnie

```bash
# Zbuduj i uruchom
docker-compose up -d

# Poczekaj 30 sekund na uruchomienie bazy danych

# Utwórz użytkownika admin
docker-compose exec backend python -c "
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
print('✅ Użytkownik utworzony: admin@example.com / admin123')
"
```

## Krok 5: Weryfikacja

Sprawdź czy wszystko działa:
```bash
docker-compose ps
```

Powinieneś zobaczyć 7 kontenerów w statusie "running":
- `price_monitor_db` (PostgreSQL)
- `price_monitor_redis` (Redis)
- `price_monitor_backend` (FastAPI)
- `price_monitor_celery_worker` (Celery Worker)
- `price_monitor_celery_beat` (Celery Scheduler)
- `price_monitor_frontend` (React)
- `price_monitor_nginx` (Nginx)

## Krok 6: Pierwsze logowanie

1. Otwórz przeglądarkę: **http://localhost**
2. Zaloguj się:
   - Email: `admin@example.com`
   - Hasło: `admin123`

## Krok 7: Dodaj pierwszy produkt

1. Kliknij **Products** w menu
2. Kliknij **+ Add Product**
3. Wypełnij formularz:
   ```
   Name: iPhone 15 Pro
   SKU: IPHONE-15-PRO-256
   EAN: 0195949038488
   Category: Electronics
   Brand: Apple
   Base Price: 5999
   ```
4. Kliknij **Add Product**

## Krok 8: Dodaj źródło (np. Allegro)

1. Kliknij **Sources** w menu
2. Kliknij **+ Add Source**
3. Wypełnij formularz:
   ```
   Name: Allegro
   Type: marketplace
   Base URL: https://allegro.pl
   Scraper Config:
   {
     "price_selector": "[data-box-name='Price'] span",
     "availability_selector": "button[data-role='buy-button']",
     "use_browser": true
   }
   ```
4. Kliknij **Add Source**

## Krok 9: Połącz produkt ze źródłem

Użyj API lub dodaj przez konsole:
```bash
docker-compose exec backend python -c "
from app.models.database import SessionLocal
from app.models.models import ProductSource

db = SessionLocal()
ps = ProductSource(
    product_id=1,
    source_id=1,
    source_url='https://allegro.pl/oferta/iphone-15-pro-256gb-1234567890',
    is_active=True
)
db.add(ps)
db.commit()
print('✅ Produkt połączony ze źródłem')
"
```

## Krok 10: Uruchom pierwszy scraping

```bash
# Ręcznie uruchom sprawdzanie cen
docker-compose exec celery_worker celery -A app.tasks.celery_app call app.tasks.scraping_tasks.scrape_product --args='[1, 1]'
```

Sprawdź wyniki w zakładce **Products** → kliknij na produkt → zobacz historię cen.

## 🎉 Gratulacje!

Twoja aplikacja działa! Teraz możesz:

### Dodać więcej produktów
Użyj funkcji **Bulk Import** lub API do importu z CSV.

### Skonfigurować alerty
Idź do **Alerts** → ustaw alerty cenowe.

### Automatyczny scraping
System automatycznie sprawdza ceny raz dziennie o 2:00.
Zmień harmonogram w `backend/app/tasks/celery_app.py`:
```python
celery_app.conf.beat_schedule = {
    'scrape-all-products-daily': {
        'task': 'app.tasks.scraping_tasks.scrape_all_products',
        'schedule': crontab(hour=2, minute=0),  # Zmień tutaj
    },
}
```

### Generować raporty
Idź do **Reports** → wybierz typ i format → pobierz.

## 📊 Monitorowanie

### Zobacz logi
```bash
# Wszystkie logi
docker-compose logs -f

# Tylko backend
docker-compose logs -f backend

# Tylko celery worker
docker-compose logs -f celery_worker
```

### Status zadań Celery
```bash
docker-compose exec celery_worker celery -A app.tasks.celery_app inspect active
```

## ⚠️ Rozwiązywanie problemów

### Problem: Kontener nie startuje
```bash
docker-compose down
docker-compose up -d
docker-compose logs -f
```

### Problem: Baza danych nie działa
```bash
docker-compose down -v  # UWAGA: usuwa wszystkie dane!
docker-compose up -d
```

### Problem: Playwright nie działa
```bash
docker-compose exec backend playwright install chromium
docker-compose restart celery_worker
```

### Problem: Frontend nie łączy się z backend
Sprawdź `frontend/package.json`:
```json
{
  "proxy": "http://backend:8000"
}
```

## 🔧 Użyteczne komendy

```bash
# Status wszystkich kontenerów
docker-compose ps

# Restart całej aplikacji
make restart
# lub
docker-compose restart

# Zatrzymaj aplikację
make down
# lub
docker-compose down

# Zobacz logi
make logs
# lub
docker-compose logs -f

# Backup bazy danych
make backup

# Wyczyszczenie wszystkiego
make clean  # UWAGA: usuwa wszystkie dane!
```

## 📚 Więcej informacji

- **README.md** - Pełna dokumentacja
- **docs/API.md** - Dokumentacja API
- **docs/SCRAPING_GUIDE.md** - Przewodnik po scrapingu
- **http://localhost/docs** - Interaktywna dokumentacja API

## 🆘 Pomoc

Jeśli napotkasz problemy:
1. Sprawdź logi: `docker-compose logs`
2. Sprawdź dokumentację w README.md
3. Upewnij się, że wszystkie kontenery działają: `docker-compose ps`

---

**Powodzenia! 🚀**
