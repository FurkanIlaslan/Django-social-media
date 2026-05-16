# 🚀 Deployment Kılavuzu (Demo/Eğitim)

Bu proje **eğitim amaçlıdır** ve hızlı demo için optimize edilmiştir.

## ✅ Hazır Durumda Olanlar

- ✅ Güçlü SECRET_KEY oluşturuldu
- ✅ Dosya upload limitleri eklendi (5MB)
- ✅ CSRF koruması aktif
- ✅ Admin paneli özelleştirildi
- ✅ Çoklu dil desteği (TR/EN)
- ✅ Dark mode
- ✅ Responsive tasarım

## 🎯 Hızlı Deployment Seçenekleri

### 1️⃣ Heroku (En Kolay - Ücretsiz Tier)

```bash
# Heroku CLI yükleyin
brew install heroku/brew/heroku  # macOS
# veya https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Proje klasöründe
cd "Yapay Zeka Uygulaması"
git init
git add .
git commit -m "Initial commit"

# Heroku app oluştur
heroku create your-app-name

# PostgreSQL ekle (ücretsiz)
heroku addons:create heroku-postgresql:hobby-dev

# Environment variables
heroku config:set DJANGO_SECRET_KEY="your-secret-key"
heroku config:set DJANGO_DEBUG="False"

# Deploy
git push heroku main
heroku run python socialsite/manage.py migrate
heroku run python socialsite/manage.py createsuperuser

# Açın
heroku open
```

**Gerekli Dosyalar:**
- `Procfile` (web: gunicorn socialsite.wsgi)
- `runtime.txt` (python-3.11.0)
- `requirements.txt`'e `gunicorn` ekle

### 2️⃣ PythonAnywhere (Kolay - Ücretsiz)

1. https://www.pythonanywhere.com/ hesap açın
2. "Web" sekmesinden "Add a new web app"
3. "Manual Configuration" → Python 3.10
4. Bash console'dan projeyi yükleyin:
```bash
git clone your-repo-url
cd Yapay-Zeka-Uygulamasi
mkvirtualenv --python=/usr/bin/python3.10 myenv
pip install -r requirements.txt
cd socialsite
python manage.py migrate
python manage.py createsuperuser
```
5. Web tab'dan WSGI configuration düzenleyin
6. Static files ayarlarını yapın
7. Reload

### 3️⃣ Railway.app (Modern - Ücretsiz Trial)

1. https://railway.app/ hesap açın
2. "New Project" → "Deploy from GitHub"
3. Repository'nizi seçin
4. Otomatik detect edilir
5. Environment variables ekleyin:
   - `DJANGO_SECRET_KEY`
   - `DJANGO_DEBUG=False`
6. Deploy!

### 4️⃣ Render.com (İyi Seçenek)

1. https://render.com/ hesap açın
2. "New Web Service"
3. Repository bağlayın
4. Settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd socialsite && gunicorn socialsite.wsgi:application`
5. Environment variables ekleyin
6. Deploy

## ⚙️ Production İçin Ek Ayarlar (İsteğe Bağlı)

### A) requirements.txt'e ekleyin:
```txt
gunicorn==21.2.0
psycopg2-binary==2.9.9  # PostgreSQL için
whitenoise==6.6.0  # Static files için
dj-database-url==2.1.0  # Database URL parse için
```

### B) settings.py'de production ayarları:

```python
import dj_database_url

# Database - Production'da PostgreSQL
if not DEBUG:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )

# Static files - WhiteNoise ile serve et
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Security - Production'da
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
```

### C) Procfile oluşturun:
```
web: cd socialsite && gunicorn socialsite.wsgi
release: cd socialsite && python manage.py migrate
```

### D) runtime.txt oluşturun:
```
python-3.11.0
```

## 🎓 Eğitim/Demo İçin ÖNERİLER

### ✅ Şu Anki Haliyle Yapabilirsiniz:
- Localhost'ta demo gösterimi
- Heroku/Railway gibi platformlara deploy
- Küçük grup eğitimleri (10-50 kullanıcı)
- Portfolio projesi olarak kullanma
- GitHub'da paylaşma

### ⚠️ Gerçek Kullanıcılar İçin GEREKLİ:
- PostgreSQL veritabanı (SQLite yerine)
- Cloud storage (AWS S3/Cloudinary) - medya dosyaları için
- Redis (caching)
- Email servisi (SendGrid/Mailgun)
- Rate limiting (django-ratelimit)
- Monitoring (Sentry)
- CDN (Cloudflare)
- Regular backups

## 🌍 Domain Bağlama

Deploy ettikten sonra kendi domain'inizi bağlamak için:

1. DNS ayarlarında CNAME record ekleyin:
   - Heroku: `your-app.herokuapp.com`
   - Render: `your-app.onrender.com`
   
2. `settings.py`'de:
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

3. Platform'da custom domain ekleyin

## 📊 Performans İpuçları

Demo için optimize edilmiş, ancak isterseniz:

```python
# Cache ekleyin
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Database optimizasyonu
CONN_MAX_AGE = 600

# Gzip compression
MIDDLEWARE.append('django.middleware.gzip.GZipMiddleware')
```

## 🐛 Debug İpuçları

Deployment sonrası sorun yaşarsanız:

```bash
# Logları kontrol edin
heroku logs --tail  # Heroku
railway logs  # Railway

# Database bağlantısını test edin
python manage.py check --database default

# Static files sorunları
python manage.py collectstatic --noinput

# Migration sorunları
python manage.py showmigrations
python manage.py migrate --fake-initial
```

## 📝 Checklist

Deployment öncesi kontrol edin:

- [ ] SECRET_KEY güçlü ve güvenli
- [ ] DEBUG=False (production'da)
- [ ] ALLOWED_HOSTS doğru domain ile
- [ ] Database ayarları doğru
- [ ] Static files toplandı
- [ ] Migrations yapıldı
- [ ] Superuser oluşturuldu
- [ ] Media klasörü yazılabilir
- [ ] HTTPS sertifikası (platformlar otomatik sağlar)

## 🎉 Sonuç

**Demo/Eğitim için:** Heroku veya Railway en kolay seçeneklerdir. 5-10 dakikada deploy edebilirsiniz!

**Gerçek kullanıcılar için:** Yukarıdaki production ayarlarını uygulayın.

---

**Başarılar! 🚀**

*Son Güncelleme: 16 Mayıs 2026*
