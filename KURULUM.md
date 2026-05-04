# Kütük Sorgulama - Android APK Kurulum Kılavuzu

## ADIM 1 - PC'de Veritabanını Hazırla

### 1a. Kütük Sorgulama programını aç (MySQL başlasın)

### 1b. Dönüştürme scriptini çalıştır:
```
python convert_to_sqlite.py
```
→ `kutuk.db` dosyası oluşur (~14 GB)

### 1c. kutuk.db'yi tablete kopyala (USB):
```
Tablet yolu: /sdcard/KutukSorgulama/kutuk.db
```

---

## ADIM 2 - APK'yı Derle (Ubuntu/Linux bilgisayarda)

### 2a. Gerekli araçları kur:
```bash
pip install buildozer cython
sudo apt install -y \
    git zip unzip openjdk-17-jdk \
    python3-pip autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev
```

### 2b. Bu klasörde derle:
```bash
cd kutuk_android/
buildozer android debug
```
→ `bin/KutukSorgulama-1.0-debug.apk` oluşur (~50-80 MB)

---

## ADIM 3 - APK'yı Tablete Yükle

### 3a. Tablette "Bilinmeyen Kaynaklara" izin ver:
```
Ayarlar → Güvenlik → Bilinmeyen Kaynaklar → Aç
```

### 3b. APK'yı USB ile kopyala → tablete yükle

---

## Alternatif: Google Colab ile derle (Ücretsiz)

Yerel Linux yoksa Google Colab kullanabilirsiniz:
1. colab.research.google.com → Yeni not defteri
2. Dosyaları yükle
3. Aşağıdaki komutu çalıştır:
```python
!pip install buildozer cython
!apt install -y git zip unzip openjdk-17-jdk
!buildozer android debug
```

---

## Tablet Gereksinimleri

| Özellik | Minimum | Önerilen |
|---------|---------|---------|
| Android | 5.0 (API 21) | 10+ |
| RAM | 3 GB | 6 GB+ |
| Depolama | 20 GB boş | 50 GB+ boş |
| Ekran | 10 inç | 10-12 inç |

---

## Özellikler

- ✅ Tamamen offline — internet yok
- ✅ 100M+ kayıt destekler  
- ✅ TC ile anlık sorgu (<1 ms)
- ✅ Ad/Soyad ile hızlı arama
- ✅ Kayıt ekleme / düzenleme / silme
- ✅ Not ekleme
- ✅ USB ile veri güncelleme

---

## Veri Güncelleme (Yeni Veri Geldiğinde)

1. PC'de `convert_to_sqlite.py` yeniden çalıştır
2. Yeni `kutuk.db` dosyasını USB ile kopyala
3. Uygulama → Ayarlar → "Bağlantıyı Yenile"
