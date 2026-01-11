# 🌐 Konfiguracja Frontendu na Netlify

## Metoda 1: Deploy przez Git (ZALECANE)

### Krok 1: Przygotuj repozytorium frontend

```bash
# W folderze aplikacji
cd price-monitor-app

# Utwórz osobne repo dla frontendu
mkdir -p ../price-monitor-frontend
cp -r frontend/* ../price-monitor-frontend/
cp netlify.toml ../price-monitor-frontend/

cd ../price-monitor-frontend

# Inicjalizuj git
git init
git add .
git commit -m "Initial commit - Price Monitor Frontend"

# Utwórz repo na GitHub i wyślij
git remote add origin https://github.com/TWOJ-USERNAME/price-monitor-frontend.git
git branch -M main
git push -u origin main
```

### Krok 2: Połącz z Netlify

1. Idź na https://app.netlify.com
2. Kliknij **Add new site** → **Import an existing project**
3. Wybierz **GitHub**
4. Wybierz repo: `price-monitor-frontend`
5. Konfiguracja build:
   ```
   Build command: npm run build
   Publish directory: build
   Base directory: (puste)
   ```
6. **Environment variables**:
   ```
   REACT_APP_API_URL = https://price-monitor-backend.onrender.com
   ```
   (Zamień na swój URL z Render po wdrożeniu backendu)

7. Kliknij **Deploy site**

### Krok 3: Konfiguracja domeny (opcjonalnie)

1. W Netlify Dashboard → **Domain settings**
2. Zmień nazwę: **Options** → **Change site name**
   - Np. `price-monitor-app` → URL będzie `price-monitor-app.netlify.app`
3. Lub dodaj własną domenę: **Add custom domain**

---

## Metoda 2: Deploy przez Drag & Drop (Szybsza, ale mniej automatyczna)

### Krok 1: Zbuduj frontend lokalnie

```bash
cd price-monitor-app/frontend

# Ustaw URL backendu (zamień na swój)
echo "REACT_APP_API_URL=https://price-monitor-backend.onrender.com" > .env.production

# Zainstaluj zależności i zbuduj
npm install
npm run build
```

### Krok 2: Deploy na Netlify

1. Idź na https://app.netlify.com
2. Przeciągnij folder `build/` na stronę ("Drop" area)
3. Poczekaj na upload (~1 minuta)
4. Gotowe! Otrzymasz URL typu `random-name-123456.netlify.app`

### Krok 3: Aktualizacja (gdy zmienisz kod)

Po każdej zmianie kodu:
```bash
npm run build
# Przeciągnij nowy folder build/ na Netlify
```

---

## ⚠️ WAŻNE: Aktualizacja CORS na Render

Po wdrożeniu frontendu na Netlify, musisz zaktualizować backend:

### W Render Dashboard:

1. Idź do **price-monitor-backend**
2. **Environment** → Edytuj `BACKEND_CORS_ORIGINS`
3. Zamień na:
   ```
   https://twoja-app.netlify.app,http://localhost:3000
   ```
   (Zamień `twoja-app` na swoją nazwę Netlify)
4. **Save Changes**
5. Backend automatycznie zrestartuje się

---

## 🧪 Testowanie

### Sprawdź połączenie frontend-backend:

1. Otwórz aplikację: `https://twoja-app.netlify.app`
2. Otwórz DevTools (F12) → **Console**
3. Spróbuj się zalogować
4. Jeśli widzisz błędy CORS:
   - Sprawdź `BACKEND_CORS_ORIGINS` na Render
   - Upewnij się że URL jest dokładny (bez `/` na końcu)
   - Poczekaj 1-2 minuty na restart backendu

### Testuj API bezpośrednio:

```bash
# Test health check
curl https://price-monitor-backend.onrender.com/health

# Test CORS
curl -H "Origin: https://twoja-app.netlify.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://price-monitor-backend.onrender.com/api/v1/auth/login \
     -v
```

---

## 📱 Dodatkowe opcje Netlify

### Włącz HTTPS (automatyczne)

✅ Netlify automatycznie zapewnia HTTPS

### Własna domena

1. **Domain settings** → **Add custom domain**
2. Wpisz swoją domenę (np. `priceapp.com`)
3. Skonfiguruj DNS u swojego rejestratora:
   ```
   CNAME: www → twoja-app.netlify.app
   A: @ → 75.2.60.5
   ```
4. Poczekaj na propagację DNS (~24h)

### Formularze kontaktowe (opcjonalnie)

Netlify obsługuje formularze bez backend - przydatne do "Contact Us"

### Analytics (opcjonalnie)

Netlify Analytics - $9/miesiąc (opcjonalne)

---

## 🔄 Automatyczny Redeploy

Jeśli używasz Metody 1 (Git):

**Każdy push do `main` branch automatycznie wdraża nową wersję!**

```bash
# Zmień coś w kodzie
git add .
git commit -m "Update feature"
git push

# Netlify automatycznie buduje i wdraża
```

---

## 🚀 Optymalizacja

### Build optimization

Dodaj do `package.json`:
```json
{
  "scripts": {
    "build": "react-scripts build && echo '/* /index.html 200' > build/_redirects"
  }
}
```

### Environment-specific builds

`.env.production`:
```env
REACT_APP_API_URL=https://price-monitor-backend.onrender.com
REACT_APP_ENV=production
```

`.env.development`:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

---

## 📊 Monitoring

### Sprawdź logi deploymentu:

1. Netlify Dashboard → Twoja aplikacja
2. **Deploys** → Kliknij na latest deploy
3. Zobacz **Deploy log**

### Sprawdź metryki:

1. **Analytics** (jeśli włączone)
2. **Functions** (jeśli używasz)
3. **Bandwidth** (100GB/miesiąc free)

---

## ❓ Troubleshooting

### Problem: Biała strona po wdrożeniu

**Przyczyna:** Błąd w build
**Rozwiązanie:** 
- Sprawdź **Deploy log** w Netlify
- Uruchom `npm run build` lokalnie i napraw błędy

### Problem: API calls nie działają

**Przyczyna:** CORS lub błędny URL
**Rozwiązanie:**
1. Sprawdź `REACT_APP_API_URL` w Netlify Environment Variables
2. Sprawdź `BACKEND_CORS_ORIGINS` na Render
3. Otwórz DevTools → **Network** → zobacz błędy

### Problem: 404 na refresh strony

**Przyczyna:** Brak redirects
**Rozwiązanie:**
- Dodaj `netlify.toml` z redirects (już w pakiecie)
- Lub utwórz `public/_redirects`:
  ```
  /*    /index.html   200
  ```

### Problem: Wolne ładowanie

**Przyczyna:** Duże bundle size
**Rozwiązanie:**
```bash
# Analiza bundle
npm install --save-dev webpack-bundle-analyzer
npm run build -- --stats

# Optymalizacja w package.json
"build": "GENERATE_SOURCEMAP=false react-scripts build"
```

---

## 🎉 Gotowe!

Twój frontend działa na Netlify i łączy się z backendem na Render!

**URLs:**
- Frontend: `https://twoja-app.netlify.app`
- Backend API: `https://price-monitor-backend.onrender.com`
- API Docs: `https://price-monitor-backend.onrender.com/docs`

**Następne kroki:**
1. Zaloguj się do aplikacji
2. Dodaj pierwszy produkt
3. Skonfiguruj źródło (np. Allegro)
4. Przetestuj scraping

---

**Powodzenia! 🚀**
