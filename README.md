# User Segmentation Service

Bu proje, şirketlerin kullanıcılarını davranışlarına veya niteliklerine göre gruplandırmasını (segmentasyon) sağlayan, Python ve Flask ile geliştirilmiş hafif bir HTTP servisidir. 

Sistem, bir kullanıcının verilerini ve bir dizi segment kuralını (SQL WHERE yüklemleri şeklinde) alır, ardından kullanıcının hangi segmentlere ait olduğunu dinamik olarak belirler.

## 🏗️ Mimari ve Mühendislik Kararları

- **İzolasyon ve Durumsuzluk (Statelessness):** Servis tamamen durumsuzdur. Her `/evaluate` isteği geldiğinde, `SQLite :memory:` özelliği kullanılarak RAM üzerinde anlık, o isteğe özel geçici bir veritabanı ve tablo oluşturulur. İstek tamamlandığında veriler yok edilir. Bu sayede eşzamanlı (concurrent) isteklerde veri çakışması (race condition) yaşanmaz.
- **Güvenli Tip Denetimi:** Gelen JSON verisi işlenmeden önce katı bir validasyon sürecinden geçer. İstenen veri tipleri (string, integer), null durumu, negatif tamsayı ve boş string kontrolleri manuel olarak yapılarak hatalı verilerin veritabanına ulaşması engellenir.
- **Özel SQL Fonksiyonu (`_now()`):** Anlık Unix zaman damgası gerektiren zaman bazlı segmentasyonlar için SQLite bağlantısına özel bir `_now()` fonksiyonu enjekte edilmiştir.

## 🚀 Kurulum ve Çalıştırma

Proje, her ortamda tutarlı çalışabilmesi için Dockerize edilmiştir. Sunucu portu `PORT` ortam değişkeni ile dinamik olarak ayarlanabilir.

### Docker Kullanarak (Önerilen)

Proje kök dizininde terminali açın ve aşağıdaki komutları çalıştırın:

```bash
# 1. Docker imajını derleyin
docker build -t solution .

# 2. Konteyneri başlatın (Örn: 3000 portunda)
docker run -e PORT=3000 -p 3000:3000 solution

```

### Yerel Ortamda Çalıştırma (Geliştirme İçin)

```bash
# Sanal ortam oluşturun ve aktif edin
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın (Varsayılan port 3000)
PORT=3000 python app.py

```

## 📖 API Dokümantasyonu

Servis iki adet uç nokta (endpoint) sunar.

### 1. Görsel Test Arayüzü

* **URL:** `GET /evaluate`
* **Açıklama:** Projeye entegre edilmiş statik bir test suitini (HTML) tarayıcı üzerinden sunar. Sistemin tüm edge-case'lerini görsel olarak test etmenizi sağlar.

### 2. Segmentasyon Değerlendirmesi

* **URL:** `POST /evaluate`
* **Content-Type:** `application/json`
* **Açıklama:** Gelen kullanıcı verisini, verilen SQL segment kurallarına göre değerlendirir.

#### Başarılı İstek Örneği (200 OK)

**İstek (Request):**

```json
{
  "user": {
    "id": "user-123",
    "level": 12,
    "country": "Turkey",
    "first_session": 1672531200,
    "last_session": 1735689600,
    "purchase_amount": 15000,
    "last_purchase_at": 1735600000
  },
  "segments": {
    "high_level": "level > 10",
    "turkish_spenders": "country = 'Turkey' and purchase_amount >= 10000",
    "recent_players": "last_session > _now() - 24*60*60"
  }
}

```

**Yanıt (Response):**

```json
{
  "results": {
    "high_level": true,
    "turkish_spenders": true,
    "recent_players": false
  }
}

```

#### Hata Yanıtı Örneği (400 Bad Request)

İstek geçersiz JSON, eksik alanlar, null değerler veya geçersiz SQL sözdizimi içeriyorsa açıklayıcı bir hata döner.

```json
{
  "error": "Field 'level' must be non-negative"
}

```

## 🧪 Test Süreci

Uygulama çalışır durumdayken sistemi test etmenin iki yolu vardır:

**1. Arayüz (UI) Üzerinden:** Tarayıcınızdan `http://localhost:3000/evaluate` adresine gidin ve **"Run Tests"** butonuna tıklayın.

**2. CLI (Curl) Üzerinden:** Terminalinizden aşağıdaki komutla temel büyük/küçük harf duyarlılığı testini gerçekleştirebilirsiniz:

```bash
curl -X POST http://localhost:3000/evaluate \
-H "Content-Type: application/json" \
-d '{"user": {"id": "u2", "level": 10, "country": "Turkey", "first_session": 1700000000, "last_session": 1700000000, "purchase_amount": 5000, "last_purchase_at": 1700000000}, "segments": {"turkish": "country = '\''Turkey'\''", "turkish_lowercase": "country = '\''turkey'\''"}}'

```

## 📂 Dosya Yapısı

```text
.
├── app.py               # Servis mantığı, validasyon ve SQLite işlemleri
├── Dockerfile           # Konteyner imajı derleme talimatları
├── requirements.txt     # Python bağımlılıkları (Flask)
└── static/
    └── test.html        # İstemci tarafı test arayüzü

```