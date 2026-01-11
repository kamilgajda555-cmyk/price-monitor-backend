# ✅ Szybka Lista Kontrolna Wdrożenia

Użyj tej listy, aby upewnić się, że wszystko jest skonfigurowane poprawnie.

---

## 📋 Przed rozpoczęciem

- [ ] Mam konto GitHub
- [ ] Mam konto Render.com
- [ ] Mam konto Netlify.com
- [ ] Mam rozpakowaną aplikację `price-monitor-app`

---

## 🗄️ Render.com (Backend)

### 1. Repozytorium GitHub
- [ ] Utworzyłem repo `price-monitor-backend` na GitHub
- [ ] Wysłałem kod do GitHub (`git push`)

### 2. PostgreSQL Database
- [ ] Utworzyłem PostgreSQL database na Render
- [ ] Zapisałem **Internal Database URL**
- [ ] Plan: Free ✅

### 3. Redis
- [ ] Utworzyłem Redis na Render
- [ ] Zapisałem **Internal Redis URL**
- [ ] Plan: Free ✅

### 4. Backend API (Web Service)
- [ ] Utworzyłem Web Service z Docker
- [ ] Dodałem wszystkie Environment Variables:
  - [ ] `DATABASE_URL`
  - [ ] `REDIS_URL`
  - [ ] `SECRET_KEY` (losowy, bezpieczny)
  - [ ] `BACKEND_CORS_ORIGINS` (z URL Netlify)
  - [ ] Pozostałe zmienne (patrz przewodnik)
- [ ] Deployment zakończony sukcesem ✅
- [ ] Zapisałem **Backend URL** (np. `https://price-monitor-backend.onrender.com`)

### 5. Celery Worker
- [ ] Utworzyłem Background Worker
- [ ] Docker Command: `celery -A app.tasks.celery_app worker --loglevel=info`
- [ ] Dodałem te same Environment Variables co Backend
- [ ] Worker działa ✅

### 6. Celery Beat (Scheduler)
- [ ] Utworzyłem Background Worker
- [ ] Docker Command: `celery -A app.tasks.celery_app beat --loglevel=info`
- [ ] Dodałem te same Environment Variables co Backend
- [ ] Beat działa ✅

### 7. Testy Backend
- [ ] Health check działa: `curl https://BACKEND-URL/health`
- [ ] API docs dostępne: `https://BACKEND-URL/docs`
- [ ] Logi bez błędów

---

## 🌐 Netlify (Frontend)

### 1. Repozytorium (opcjonalnie)
- [ ] Utworzyłem repo `price-monitor-frontend` na GitHub (jeśli używam Git)
- [ ] Wysłałem kod do GitHub

### 2. Deploy na Netlify
- [ ] Zdeployowałem przez Git lub Drag & Drop
- [ ] Dodałem Environment Variable:
  - [ ] `REACT_APP_API_URL` = URL backendu z Render
- [ ] Deployment zakończony ✅
- [ ] Zapisałem **Frontend URL** (np. `https://price-monitor-app.netlify.app`)

### 3. Aktualizacja CORS na Render
- [ ] Wróciłem do Render → Backend → Environment
- [ ] Zaktualizowałem `BACKEND_CORS_ORIGINS` o URL Netlify
- [ ] Backend zrestartował się automatycznie ✅

### 4. Testy Frontend
- [ ] Aplikacja otwiera się w przeglądarce
- [ ] Strona logowania widoczna
- [ ] Brak błędów w Console (F12)

---

## 👤 Pierwszy użytkownik

- [ ] Utworzyłem pierwszego użytkownika:
  - [ ] Przez Render Shell (opcja 1)
  - [ ] Przez API endpoint (opcja 2)
- [ ] Mogę się zalogować:
  - Email: `admin@example.com`
  - Hasło: `admin123`

---

## 🧪 Pełne testy E2E

### Frontend → Backend
- [ ] Logowanie działa ✅
- [ ] Dashboard ładuje się ✅
- [ ] Mogę dodać produkt ✅
- [ ] Mogę dodać źródło ✅

### Backend → Database
- [ ] Dane zapisują się do PostgreSQL ✅
- [ ] Historia cen działa ✅

### Workers
- [ ] Celery Worker działa (logi OK) ✅
- [ ] Celery Beat działa (logi OK) ✅

### API
- [ ] Wszystkie endpointy działają:
  - [ ] `/api/v1/products/`
  - [ ] `/api/v1/sources/`
  - [ ] `/api/v1/alerts/`
  - [ ] `/api/v1/reports/generate`
  - [ ] `/api/v1/dashboard/stats`

---

## 🎯 Dodatkowe (opcjonalne)

- [ ] Skonfigurowałem własną domenę na Netlify
- [ ] Dodałem UptimeRobot ping (utrzymuje backend aktywny)
- [ ] Skonfigurowałem email alerts (SMTP)
- [ ] Dodałem pierwsze produkty i źródła
- [ ] Przetestowałem scraping ręcznie
- [ ] Uruchomiłem pierwszy automatyczny scraping job

---

## 📊 URLs do zapisania

Zapisz te URLs w bezpiecznym miejscu:

```
Frontend (Netlify):
https://_____________________.netlify.app

Backend API (Render):
https://_____________________.onrender.com

API Docs:
https://_____________________.onrender.com/docs

GitHub Backend Repo:
https://github.com/___________/price-monitor-backend

GitHub Frontend Repo:
https://github.com/___________/price-monitor-frontend

PostgreSQL (Render):
Internal URL: ___________________________________

Redis (Render):
Internal URL: ___________________________________
```

---

## 🚨 Jeśli coś nie działa

### Sprawdź logi:
1. **Render Backend**: Dashboard → Backend → Logs
2. **Render Workers**: Dashboard → Worker → Logs
3. **Netlify**: Dashboard → Deploys → Deploy log
4. **Browser**: DevTools (F12) → Console + Network

### Typowe problemy:

**Problem:** Backend nie startuje
- ✅ Sprawdź Environment Variables na Render
- ✅ Sprawdź logi: czy DATABASE_URL i REDIS_URL są poprawne

**Problem:** CORS errors w przeglądarce
- ✅ Sprawdź `BACKEND_CORS_ORIGINS` na Render
- ✅ Upewnij się że zawiera URL Netlify (bez `/` na końcu)

**Problem:** Frontend biała strona
- ✅ Sprawdź Deploy log na Netlify
- ✅ Sprawdź `REACT_APP_API_URL` w Environment Variables

**Problem:** 404 na refresh
- ✅ Dodaj `netlify.toml` z redirects

**Problem:** Worker nie działa
- ✅ Sprawdź Docker Command
- ✅ Sprawdź Environment Variables (te same co Backend)

---

## ✅ Wszystko działa?

Jeśli zaznaczyłeś wszystkie checkboxy powyżej:

🎉 **GRATULACJE!** 🎉

Twoja aplikacja działa w pełni:
- ✅ Frontend na Netlify
- ✅ Backend API na Render
- ✅ Database i Redis na Render
- ✅ Workers działają w tle
- ✅ System gotowy do monitorowania cen!

---

## 🚀 Następne kroki

1. **Dodaj swoje produkty**
2. **Skonfiguruj źródła** (Allegro, Amazon, Empik)
3. **Połącz produkty ze źródłami** (mapowanie)
4. **Ustaw alerty** cenowe
5. **Przetestuj scraping** ręcznie
6. **Sprawdź automatyczny scraping** (raz dziennie o 2:00)
7. **Generuj raporty**
8. **(Opcjonalnie)** Dodaj UptimeRobot ping

---

**Miłego monitorowania cen! 📊💰**
