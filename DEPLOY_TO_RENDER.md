# 🚀 Wdrożenie na Render.com - GOTOWE DO UŻYCIA

Ten folder jest **GOTOWY** do wdrożenia na Render.com + Netlify.  
Wszystkie pliki są już skonfigurowane - **nic nie musisz zamieniać!**

---

## ✅ Co zostało przygotowane:

- ✅ `backend/Dockerfile` - **już zamieniony** na wersję dla Render
- ✅ `netlify.toml` - konfiguracja dla Netlify (już dodana)
- ✅ Cały kod backend + frontend
- ✅ Docker Compose (dla lokalnych testów)
- ✅ Pełna dokumentacja

---

## 🎯 Twoje 3 proste kroki:

### Krok 1: Wyślij na GitHub (5 min)

```bash
cd price-monitor-app

# Inicjalizuj git
git init
git add .
git commit -m "Ready for Render deployment"

# Utwórz repo na GitHub (https://github.com/new)
# Nazwa: price-monitor-backend

# Wyślij kod
git remote add origin https://github.com/TWOJ-USERNAME/price-monitor-backend.git
git branch -M main
git push -u origin main
```

### Krok 2: Render.com - Utwórz serwisy (15 min)

Idź na https://render.com i utwórz:

#### 2.1 PostgreSQL Database
- New → PostgreSQL
- Name: `price-monitor-db`
- Database: `pricedb`
- User: `priceuser`
- Plan: **Free**
- **Zapisz Internal Database URL**

#### 2.2 Redis
- New → Redis
- Name: `price-monitor-redis`
- Plan: **Free**
- **Zapisz Internal Redis URL**

#### 2.3 Web Service (Backend API)
- New → Web Service
- Connect repo: `price-monitor-backend`
- Name: `price-monitor-backend`
- Runtime: **Docker**
- Region: Frankfurt
- Plan: **Free**

**Environment Variables** (dodaj wszystkie):
```env
DATABASE_URL=<Internal Database URL z kroku 2.1>
REDIS_URL=<Internal Redis URL z kroku 2.2>
SECRET_KEY=<wygeneruj losowy string 64+ znaków>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_STR=/api/v1
PROJECT_NAME=Price Monitor
DEBUG=False
BACKEND_CORS_ORIGINS=https://twoja-app.netlify.app
SCRAPING_DELAY=2
SCRAPING_TIMEOUT=30
MAX_RETRIES=3
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

**Zapisz Backend URL:** `https://price-monitor-backend.onrender.com`

#### 2.4 Celery Worker
- New → Background Worker
- Repo: `price-monitor-backend`
- Name: `price-monitor-celery-worker`
- Runtime: **Docker**
- Docker Command: `celery -A app.tasks.celery_app worker --loglevel=info`
- **Dodaj te same Environment Variables** co w kroku 2.3

#### 2.5 Celery Beat
- New → Background Worker
- Repo: `price-monitor-backend`
- Name: `price-monitor-celery-beat`
- Runtime: **Docker**
- Docker Command: `celery -A app.tasks.celery_app beat --loglevel=info`
- **Dodaj te same Environment Variables** co w kroku 2.3

### Krok 3: Netlify - Zaktualizuj (5 min)

1. Idź do Netlify Dashboard
2. Twoja aplikacja → **Site settings** → **Environment variables**
3. Dodaj nową zmienną:
   ```
   REACT_APP_API_URL = https://price-monitor-backend.onrender.com
   ```
   (Wstaw swój URL z Render)
4. **Deploys** → **Trigger deploy** → **Deploy site**
5. Poczekaj 2 minuty

### ✅ Gotowe!

Sprawdź:
- Backend: `https://price-monitor-backend.onrender.com/health`
- Frontend: `https://twoja-app.netlify.app`

Zaloguj się:
- Email: `admin@example.com` (utwórz przez Render Shell)
- Hasło: `admin123`

---

## 📋 Szybka checklist:

- [ ] Kod na GitHub ✅
- [ ] PostgreSQL na Render ✅
- [ ] Redis na Render ✅
- [ ] Backend (Web Service) na Render ✅
- [ ] Celery Worker na Render ✅
- [ ] Celery Beat na Render ✅
- [ ] Frontend na Netlify (już masz) ✅
- [ ] Environment Variables zaktualizowane ✅
- [ ] CORS skonfigurowany ✅
- [ ] Pierwszy użytkownik utworzony ✅

---

## 🆘 Potrzebujesz pomocy?

Szczegółowy przewodnik krok po kroku:
→ Otwórz **RENDER_DEPLOYMENT_GUIDE.md** (w folderze `docs/`)

Checklist z dokładnymi krokami:
→ Otwórz **QUICK_DEPLOY_CHECKLIST.md** (w folderze `docs/`)

---

## 🎉 To wszystko!

**Nic nie musisz zmieniać - wszystko jest gotowe!**

Po prostu:
1. Wyślij na GitHub
2. Połącz z Render
3. Zaktualizuj Netlify
4. **Działa!** 🚀

---

**Powodzenia!** 💪
