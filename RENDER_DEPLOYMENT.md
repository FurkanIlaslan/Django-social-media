# 🚀 Render.com Deployment Kılavuzu

Bu dosya, projenizi Render.com'a deploy etmek için adım adım talimatları içerir.

## ✅ Ön Hazırlık (Tamamlandı)

- [x] `requirements.txt` güncellendi (gunicorn, psycopg2, whitenoise eklendi)
- [x] `build.sh` oluşturuldu (Render build scripti)
- [x] `settings.py` production için yapılandırıldı
- [x] `.gitignore` hazırlandı

## 📝 Adım 1: GitHub'a Yükleyin

### Terminal'de:

```bash
cd "/Users/furkan/Desktop/Ahmet Tekrarlar/Yapay Zeka Uygulaması"

# Git başlat (eğer başlatmadıysanız)
git init

# Tüm dosyaları ekle
git add .

# Commit yap
git commit -m "Production ready - Render.com deployment"

# GitHub'da yeni repo oluşturun (https://github.com/new)
# Sonra bağlayın:
git remote add origin https://github.com/KULLANICI_ADINIZ/REPO_ADINIZ.git
git branch -M main
git push -u origin main
```

## 🌐 Adım 2: Render.com'a Kaydolun

1. https://render.com adresine gidin
2. **"Get Started for Free"** tıklayın
3. GitHub ile giriş yapın (önerilir)
4. Hesabınızı doğrulayın (email)

## 🗄️ Adım 3: PostgreSQL Database Oluşturun

1. Render Dashboard'da **"New +"** → **"PostgreSQL"** seçin
2. Ayarlar:
   - **Name:** `socialsite-db` (veya istediğiniz isim)
   - **Database:** `socialsite` (otomatik)
   - **User:** `socialsite` (otomatik)
   - **Region:** `Frankfurt (EU Central)` (size yakın olanı seçin)
   - **PostgreSQL Version:** `16` (son sürüm)
   - **Plan:** **Free** ($0/month)
3. **"Create Database"** tıklayın
4. ⏳ 2-3 dakika bekleyin (hazır olana kadar)
5. ✅ Database hazır olunca **"Internal Database URL"** kopyalayın (ileride lazım olacak)

## 🌍 Adım 4: Web Service Oluşturun

1. Render Dashboard'da **"New +"** → **"Web Service"** seçin
2. **"Build and deploy from a Git repository"** → **"Next"**
3. GitHub repository'nizi seçin (yetki verin gerekirse)
4. Ayarlar:

### Temel Ayarlar:
- **Name:** `socialsite-app` (veya istediğiniz isim)
- **Region:** `Frankfurt (EU Central)` (database ile aynı olsun)
- **Branch:** `main`
- **Root Directory:** (boş bırakın)
- **Runtime:** `Python 3`
- **Build Command:** `./build.sh`
- **Start Command:** `cd socialsite && gunicorn socialsite.wsgi:application`

### İleri Ayarlar (Advanced):
**Plan:** **Free** ($0/month - 750 saat/ay)

## 🔐 Adım 5: Environment Variables Ekleyin

Aynı sayfada **"Environment Variables"** bölümüne aşağıdaki değişkenleri ekleyin:

### Zorunlu:

```
DATABASE_URL
Değer: (Adım 3'te kopyaladığınız Internal Database URL'yi yapıştırın)

DJANGO_SECRET_KEY
Değer: 2+eyz*m=lr4ds$z4kyshz!te4@3aw)*!61$_ql9434d0x^!0(v

DJANGO_DEBUG
Değer: False

PYTHON_VERSION
Değer: 3.11.0
```

### Cloudinary (Fotoğraflar için - ÖNEMLİ! 📸):

**Cloudinary hesabı oluşturun:** https://cloudinary.com/users/register/free

Dashboard'dan şu bilgileri alıp ekleyin:

```
CLOUDINARY_CLOUD_NAME
Değer: (Dashboard'dan Cloud Name)

CLOUDINARY_API_KEY
Değer: (Dashboard'dan API Key)

CLOUDINARY_API_SECRET
Değer: (Dashboard'dan API Secret)
```

### Otomatik (Render ekler):
```
RENDER_EXTERNAL_HOSTNAME
(Otomatik - kendi domain'inizi verir)
```

### Opsiyonel (Email için - şimdilik atlayın):
```
EMAIL_HOST_USER
Değer: (Gmail adresiniz - ileride ekleyebilirsiniz)

EMAIL_HOST_PASSWORD
Değer: (Gmail app password - ileride ekleyebilirsiniz)
```

## 🚀 Adım 6: Deploy Başlat

1. Tüm ayarları kontrol edin
2. **"Create Web Service"** tıklayın
3. ⏳ **10-15 dakika bekleyin** (ilk deploy uzun sürer)
4. Build süreci:
   - 📦 Dependencies yükleniyor...
   - 🔨 Build script çalışıyor...
   - 📊 Static files toplanıyor...
   - 🗄️ Database migrate ediliyor...
   - ✅ Deploy tamamlandı!

## 🎯 Adım 7: İlk Kullanıcıyı Oluşturun

Deploy tamamlandıktan sonra:

1. Render Dashboard'da servisinize gidin
2. Üstte **"Shell"** sekmesine tıklayın
3. Terminal açılacak, şu komutları girin:

```bash
cd socialsite
python manage.py createsuperuser
```

4. Username, email, password girin
5. ✅ Admin kullanıcısı oluşturuldu!

## 🌐 Adım 8: Siteyi Ziyaret Edin

1. Render Dashboard'da servisinizin URL'sini görün (üstte)
2. Örnek: `https://socialsite-app.onrender.com`
3. Tarayıcıda açın:
   - Ana Sayfa: `https://your-app.onrender.com/tr/`
   - Admin: `https://your-app.onrender.com/tr/admin/`
   - Feed: `https://your-app.onrender.com/tr/feed/`

## ⚠️ Önemli Notlar

### İlk Yüklenme Yavaş Olabilir:
- Free tier'da 15 dakika inaktif kalırsa uykuya geçer
- İlk istek 30-60 saniye sürebilir (cold start)
- Sonraki istekler normal hızda

### Medya Dosyaları:
- User uploads (profil fotoğrafları, post resimleri) geçici olarak saklanır
- Free tier'da disk temizlenir, kalıcı olmaz
- Production için AWS S3 veya Cloudinary kullanın

### Database Limitleri:
- Free PostgreSQL: 1GB storage
- Demo için yeterli
- Yedek almayı unutmayın (Render Dashboard → Database → Backups)

## 🐛 Sorun Giderme

### Build Hatası:
```bash
# Render Dashboard → Logs sekmesinden hataları kontrol edin
# Genelde eksik package veya syntax hatası olur
```

### Database Bağlantı Hatası:
```bash
# Environment variables kontrol edin
# DATABASE_URL doğru mu?
```

### Static Files Görünmüyor:
```bash
# Shell'de:
cd socialsite
python manage.py collectstatic --no-input
```

### 500 Error:
```bash
# DEBUG=False olduğu için hata detayları gizli
# Logs sekmesinden gerçek hatayı görün
```

## 🔄 Güncelleme (Yeni Kod Deploy Etme)

Kod değişikliği yaptıktan sonra:

```bash
git add .
git commit -m "Güncelleme mesajı"
git push origin main
```

Render otomatik olarak yeni deploy başlatır! ✅

## 📊 Monitoring

- Render Dashboard → **"Metrics"** sekmesinden:
  - CPU kullanımı
  - Memory kullanımı
  - Request sayısı
  - Response time
  
- **"Logs"** sekmesinden:
  - Gerçek zamanlı loglar
  - Error mesajları
  - Django output

## 💰 Ücretsiz Limitler

**Free Tier (0$/month):**
- 750 saat/ay web service (1 ay = 720 saat, yeterli!)
- 1 GB PostgreSQL storage
- 100 GB bandwidth/ay
- Otomatik HTTPS (Let's Encrypt)
- Custom domain desteği
- Cold start var (15 dk inaktif sonrası)

## 🎉 Tebrikler!

Projeniz artık canlıda! 🚀

**Paylaşabileceğiniz link:** `https://your-app.onrender.com/tr/`

---

**Hazırlayan:** AI Assistant
**Tarih:** 16 Mayıs 2026
