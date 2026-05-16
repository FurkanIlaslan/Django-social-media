# 🚀 Django Social Media Platform

Modern, tam özellikli sosyal medya platformu - **Eğitim ve Demo Amaçlı**

Instagram benzeri bir web uygulaması

Backend: Django + Django REST Framework
Frontend: Plain HTML/CSS/JS with Tailwind CSS

## ✨ Özellikler

### 📱 Temel Sosyal Medya Özellikleri
- ✅ Kullanıcı kayıt ve giriş sistemi
- ✅ Profil sayfaları ve özelleştirme
- ✅ Gönderi oluşturma, düzenleme, silme (CRUD)
- ✅ Fotoğraf yükleme ve paylaşma
- ✅ Beğeni (Like) sistemi
- ✅ Yorum sistemi
- ✅ Takip/Takipçi sistemi
- ✅ Kullanıcı arama

### 💬 İletişim
- ✅ Gerçek zamanlı mesajlaşma
- ✅ Anlık bildirimler
- ✅ Online/offline durum gösterimi

### 🎨 Kullanıcı Deneyimi
- ✅ **Çoklu Dil Desteği** (Türkçe/İngilizce)
- ✅ **Dark Mode** (Karanlık tema)
- ✅ Responsive tasarım (Mobil uyumlu)
- ✅ Infinite scroll (Sonsuz kaydırma)
- ✅ Modern ve zarif UI/UX

### 🛡️ Moderasyon ve Güvenlik
- ✅ İçerik raporlama sistemi
- ✅ Admin moderasyon paneli
- ✅ CSRF koruması
- ✅ Dosya upload güvenliği (5MB limit)

### 📊 Admin Paneli
- ✅ Renkli ve özelleştirilmiş admin interface
- ✅ Rapor yönetimi (status badges ile)
- ✅ Kullanıcı ve içerik yönetimi

## 🛠️ Teknolojiler

**Backend:** Django 4.2.3, Django REST Framework, SQLite, Pillow
**Frontend:** Tailwind CSS, Alpine.js, Chart.js, Vanilla JavaScript
**İlave:** Django i18n (çoklu dil), CORS Headers

## 📦 Kurulum

### 1. Projeyi İndirin
```bash
cd "Yapay Zeka Uygulaması"
```

### 2. Sanal Ortam Oluşturun (Önerilen)
```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Veritabanını Hazırlayın
```bash
cd socialsite
python3 manage.py migrate
```

### 5. Süper Kullanıcı Oluşturun
```bash
python3 manage.py createsuperuser
```

### 6. Sunucuyu Başlatın
```bash
python3 manage.py runserver 8001
```

### 7. Tarayıcıda Açın
- **Ana Sayfa:** http://127.0.0.1:8001/tr/
- **Feed:** http://127.0.0.1:8001/tr/feed/
- **Admin:** http://127.0.0.1:8001/tr/admin/
- **İngilizce:** http://127.0.0.1:8001/en/

## 🌍 Çoklu Dil Kullanımı

Proje Türkçe ve İngilizce dillerini destekler. Navbar'daki 🌐 simgesine tıklayarak dil değiştirebilirsiniz.

## 🎯 Demo Özellikleri

Bu proje **eğitim ve demo** amaçlıdır:
- ✅ Tüm özellikler çalışır durumda
- ✅ SQLite veritabanı kullanır (kolay setup)
- ✅ DEBUG mode aktif (hata mesajları görünür)
- ⚠️ Production kullanımı için ek güvenlik ayarları gereklidir

## 📂 Proje Yapısı

```
socialsite/
├── accounts/          # Kullanıcı yönetimi
├── posts/            # Gönderi, yorum, beğeni, raporlama
├── messaging/        # Mesajlaşma sistemi
├── chat/             # Chat desteği
├── notifs/           # Bildirimler
├── media/            # Yüklenen dosyalar
├── locale/           # Çeviri dosyaları (TR/EN)
└── templates/        # HTML şablonları
```

## 📝 Not

Bu proje eğitim amaçlıdır. Öğrenmek ve geliştirmek için özgürce kullanabilirsiniz.

**⭐ Son Güncelleme: 16 Mayıs 2026**


