# Kod Dokümantasyonu

Bu doküman, `app.py` dosyasında yer alan Python Flask uygulamasının çalışma mantığını, kullanılan kütüphaneleri ve fonksiyonları satır satır detaylı bir şekilde açıklamaktadır. Açıklanan kodun örnek çalıştırılması da linki verilen videoda gösterilmiştir (https://youtu.be/YlNlWpgxpm4).

### 1. Kütüphane İçe Aktarımları ve SQLite

```python
import sqlite3
import time
import os
from flask import Flask, request, jsonify, send_from_directory

```

* **import sqlite3:** Python sqlite modülü SQLite veritabanını Python'a entegre etmek için kullanılır.
* **SQLite:** Hafif ve gömülü bir ilişkisel veritabanı motorudur. Yerel veri depolama için mükemmeldir çünkü MySQL veya PostgreSQL gibi alternatiflerinin yanında ayrı bir sunucu süreci gerektirmez. Bu da büyük ölçekli olmayan ve zaman kısıtlı projelerde işimize yarar.
* **Sunucusuzdur:** MySQL gibi veritabanlarının çalışması için ayrı bir sunucu gerekirken (TCP/IP protokolü kullanırlar) SQLite sunucu gerektirmez ("serverless"), arada bir sunucu katmanı olmadan doğrudan diskten okuma yazma yapar.
* **Avantajları:** Bu da bizi fazla bağımlılıklardan, kurulum ve yönetim karmaşıklığından kurtarır. (Örn: Big data alanına oldukça katkı sağlayan IoT cihazlarda hafif yapısı nedeniyle çokça tercih edilen bir veritabanıdır).
* **Tercih Sebebi:** Projenin kısıtlı zamanı, sqlite ile pythonun kusursuz uyumu nedeniyle tercih edilmiştir.

**SQLite ACID İlkeleri:**
SQLite tam ACID (Atomicity, Consistency, Isolation, Durability) işlemlerini destekler:

* **Atomicity (Atomiklik):** Bu ilkeye göre bir işlem ya tamamen gerçekleşir ya da hiç gerçekleşmez. İşlem adımlarından biri bile başarısız olursa, veritabanı işlemin en başına döner (Rollback).
* **Consistency (Tutarlılık):** Bir işlem başlamadan önce veritabanı hangi kurallara (kısıtlamalara) sahipse, işlem bittikten sonra da o kurallar korunmalıdır. Veri her zaman geçerli ve mantıklı kalır.
* **Isolation (İzolasyon):** Aynı anda gerçekleşen birden fazla işlem, birbirini etkilemez. Her işlem, sanki sistemde o an tek başına çalışıyormuş gibi davranır.
* **Durability (Dayanıklılık):** Bir işlem başarıyla tamamlandığında (Commit), sistem çökse veya elektrik kesilse bile bu veri kalıcı olarak saklanır. Veri artık fiziksel disk üzerindedir ve geri gelmez.

**Diğer Modüller:**

* **import time:** Bu modül zamanla ilgili çeşitli fonksiyonlar sağlar.
* **import os:** İşletim sistemi ile etkileşim kurmamızı sağlayan modül.
* **import Flask:** Flask uygulamasını başlatır, istekleri dinler ve yönetir.
* **import request:** Gelen istekleri tutar.
* **import jsonify:** Verileri json formatına çevirmek için kullanılır.
* **import send_from_directory:** Projemizdeki belirli bir dizinden dosya sunmak için kullanılır.

---

### 2. Uygulama Başlatma ve Konfigürasyon

```python
app = Flask(__name__)

```

* **Flask(__name__):** Flask sınıfından bir nesne oluşturur (app). `__name__` argümanı Python'da uygulamanın o an çalıştığı dosyanın konumunu tutar.
* **Avantajları:** Bu bize birtakım avantajlar sağlar. Örn: `static` klasörünü otomatik tanır, routing işlemlerini yapmamıza olanak sağlar.

```python
REQUIRED_FIELDS = {
    "id": str,
    "level": int,
    "country": str,
    "first_session": int,
    "last_session": int,
    "purchase_amount": int,
    "last_purchase_at": int
}

```

* **Sözlük Yapısı:** Bu kod RAM'de bir "dict" nesnesi oluşturur (sözlük). Python'da sözlük veri yapısı anahtar-değer formatındadır. Bir anahtara ulaşmak  zaman karmaşıklığındadır, yani hızlıdır.
* **Validasyon İhtiyacı:** Statik değildir, yani validasyonları Python yapmaz, bizim elle yapmamız gerekir.

---

### 3. Yardımcı Fonksiyonlar

```python
def get_now():
    return int(time.time())

```

* **Arka Plan:** Tek satırlık basit gibi görünen bu fonksiyon aslında arka planda birçok şey yapar. `time.time()` (time modülünden time() fonksiyonu) çağrıldığında arka planda bir sistem fonksiyonu çalışır. Yani program "user mode"dan "kernel mode"a geçer.
* **Unix Epoch:** Bu fonksiyon işletim sistemindeki bir sayaçtan Unix Epoch (1 Ocak 1970 00:00:00 UTC'den bu yana geçen saniye) değerini float veri tipinde olarak döndürür.
* **Type Casting:** `int(time.time())` ile ise type casting yaparak bu float değerinin virgülden sonraki kısmı atılarak veritabanına integer olarak kaydetmemize olanak sağlar.

---

### 4. Veri Doğrulama (Validation)

```python
def validate_user_data(user):
    if not user:
        return "User object is missing"

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in user:
            return f"Missing field: {field}"
        
        value = user[field]
        if value is None:
            return f"Field '{field}' cannot be null"
            
        if not isinstance(value, expected_type):
            return f"Field '{field}' must be of type {expected_type.__name__}"
            
        if expected_type == int and value < 0:
            return f"Field '{field}' must be non-negative"
            
        if expected_type == str and len(value.strip()) == 0:
            return f"Field '{field}' cannot be empty string"
            
    return None

```

* **Genel Amaç:** Bu fonksiyon ile Data Validasyon yapıyoruz. Gelen ham verinin iş mantığına uygun olup olmadığını bu fonksiyon ile doğruluyoruz denilebilir.
* **Tip Kontrolü:** Ayrıca yukarıda açıkladığım gibi sözlük veri yapısı statiktir dolayısıyla tip kontrolünü elle yapmamız gerekir. Bu kontrolü de bu fonksiyon ile yapıyoruz.
* **if not user:** User parametresi null mu diye kontrol eder. Öyle ise alt satırlara geçmez.
* **Döngü (for field...):** Sözlüğümüzdeki değerleri kontrol etmemizi sağlar. Keyleri `field`, değerleri de `expected_type` olarak isimlendirir (daha anlamlı, bakımı kolay, okunabilir bir yapı sağlar). User'ın her bir değeri için tip ve değer kontrollerini yapar (proje tanımında istendiği şekilde).
* **if field not in user:** Sözlükte var olmayan bir anahtara erişmek Python'da `KeyError` istisnası fırlatır. Burada bu istisnaya engel olunmuştur.
* **if value is None:** Python'da `None` geçerli bir tiptir ancak proje isterleri ve iş mantığı gereği bir fieldın boş olmaması gerekir, burada bu kontrol yapılır.
* **if not isinstance(...):** Bir value nesnesinin `expected_type` ile aynı sınıftan mı (veya üst sınıfından mı) olup olmadığını kontrol eder. Burada aslında basit bir tip kontrolü yapılır.
* **Diğer Kontroller:** Kalan satırlarda değer bir tamsayı ise sıfırdan küçük olamaz, dizge ise boş olamaz gibi kontroller yapılır.

---

### 5. GET Metodu (Arayüz)

```python
@app.route('/evaluate', methods=['GET'])
def get_evaluate():
    return send_from_directory('static', 'test.html')

```

* **Dekoratör:** `@app.route` dekoratörü Flask'ın yönlendirme mekanizmasını kullanmamızı sağlar. Dekoratörler Python'da eklendiği fonksiyona ek işlevsel özellikler kazandırır. Burada da görüldüğü gibi bu dekoratör `get_evaluate()` fonksiyonumuza Flask'ın yönlendirme mekanizmasını kazandırır.
* **İşlev:** `send_from_directory('static', 'test.html')` verilen dizinden statik bir dosya döner. Kısacası bu fonksiyon tarayıcıda `http://localhost:3000/evaluate` adresine gittiğimizde testlerimizin gerçekleştiği `test.html` dosyasını bize verir.

---

### 6. POST Metodu (Değerlendirme Mantığı)

#### 6.1 İstek ve Veri Ayrıştırma

```python
@app.route('/evaluate', methods=['POST'])
def evaluate_segments():
    if not request.is_json:
        return jsonify({"error": "Invalid JSON"}), 400

    data = request.get_json()
    user_data = data.get("user")
    segments = data.get("segments")

    if not user_data or segments is None:
        return jsonify({"error": "Missing 'user' or 'segments' field"}), 400
        
    validation_error = validate_user_data(user_data)
    if validation_error:
        return jsonify({"error": validation_error}), 400

```

* **if not request.is_json:** Burada HTTP isteğinin header bölümü kontrol edilir. `is_json` fonksiyonun kaynak kodlarındaki yorum satırında da belirtildiği gibi "mimetype: application/json" veya "mimetype: application/+json" yani isteğin header bölümü okunur ve JSON veri tipinde mi kontrolü yapılır.
* **request.get_json():** İstekteki ham json veriyi alır ve bu veriyi bir Python sözlüğüne dönüştürür (json -> dict).
* **Veri Atama:** Sözlükten `user` ve `segments` anahtarlarının değerlerini ayrı değişkenlere atayarak işlem yapma kolaylığı ve kod okunabilirliği sağlanır.
* **Eksik Veri Kontrolü:** User bilgileri veya segmentasyon bilgileri eksik mi kontrolü yapar.
* **Validasyon:** `validate_user_data(user_data)` ile yukarıda anlatılan fonksiyonu çağırır ve dönen değeri kaydeder.
* **Hata Dönüşü:** `if validation_error` ile None dışı bir değer dönerse, yani hata varsa hata mesajı döner.

#### 6.2 Veritabanı Bağlantısı ve Hazırlık

```python
    conn = sqlite3.connect(':memory:')
    conn.create_function("_now", 0, get_now)
    cursor = conn.cursor()

```

* **conn = sqlite3.connect(':memory:'):** Bu fonksiyon basitçe sqlite veritabanına bağlanmamızı sağlar ancak burada önemli bir detay mevcut: `':memory:'` parametresi. Bu parametre sayesinde veritabanımız disk üzerinde değil, doğrudan RAM üzerinde çalışır. Yani program durunca veritabanı da kesilir. Bu bize hız ve basitlik sağlar.
* **conn.create_function:** Python'da yazdığımız `get_now` fonksiyonunu SQL motoruna bir "plugin" gibi ekler. Verilen `0` parametresi ise bu fonksiyonun kaç parametre aldığını söyler. `get_now` fonksiyonumuz parametre almadığı için 0 verilir.
* **cursor:** Veritabanında işlem yapabilmek adına bir "imleç" oluşturur.

#### 6.3 Tablo Oluşturma ve Veri Ekleme

```python
    try:
        cursor.execute("""
            CREATE TABLE users (
                id TEXT,
                level INTEGER,
                country TEXT,
                first_session INTEGER,
                last_session INTEGER,
                purchase_amount INTEGER,
                last_purchase_at INTEGER
            )
        """)
        
        cursor.execute("""
            INSERT INTO users (id, level, country, first_session, 
                               last_session, purchase_amount, last_purchase_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_data['id'],
            user_data['level'],
            user_data['country'],
            user_data['first_session'],
            user_data['last_session'],
            user_data['purchase_amount'],
            user_data['last_purchase_at']
        ))

```

* **İşlev:** Gelen istekteki `user_data` sözlüğündeki verileri veritabanında `users` adındaki tabloya işler.

#### 6.4 Segment Sorgulama Mantığı

```python
        results = {}
        for segment_name, query in segments.items():
            sql_query = f"SELECT 1 FROM users WHERE {query}"
            try:
                cursor.execute(sql_query)
                match = cursor.fetchone()
                results[segment_name] = (match is not None)
            except sqlite3.Error as e:
                conn.close()
                return jsonify({"error": f"Invalid SQL syntax in segment '{segment_name}': {str(e)}"}), 400
                
        conn.close()
        return jsonify({"results": results}), 200

```

* **results = {}:** Sonuçları tutacağımız sözlük yapısı.
* **Döngü:** Gelen isteğin segment bölümündeki her bir anahtar ismi ve isme karşılık gelen (veri üzerinde işletilecek) SQL sorgu ifadesini tek tek döner.
* **sql_query:** `SELECT 1 FROM users WHERE {query}` sorgusu şunu yapar: Kullanıcı sorgudaki kurallara uyuyor mu? Cevap evet ise 1 döner, cevap hayır ise None döner.
* **cursor.execute:** Sorguyu alır, parse eder ve tablo üzerinde sorgular.
* **cursor.fetchone():** Sorgu çalıştığında SQLite bellekte bir sonuç kümesi oluşturur. `fetchone()` ise bu sonuç kümesinden ilk satırı çeker (zaten "SELECT 1" dediğimiz için sadece 1 rakamı olan bir satır döner).
* **Tuple Dönüşü:** Eğer kayıt bulunursa Python `match` değişkenine bir tuple döner `(1,)`, kayıt bulunamaz ise `None` döner. Tuple veri yapısı Immutable (değiştirilemez) ve sabittir.
* **Sonuç Kaydı:** `results[segment_name] = (match is not None)` basit bir if-else sorgusudur. Match `None` ise False, değilse True döner ve result sözlüğümüze değer kaydedilir.
* **SQL Hataları:** SQL sorgusunda hata varsa bunu yakalayıp kullanıcıya anlamlı bir mesaj dönüyoruz.
* **Kaynak İadesi:** `conn.close()` ile kaynak iadesi yapıyoruz ve sonuçların yer aldığı sözlük yapısını tekrar json'a çevirip bu sonucu döndürüyoruz.

#### 6.5 Genel Hata Yakalama

```python
    except Exception as e:
        conn.close()
        return jsonify({"error": f"Server error: {str(e)}"}), 500

```

* **İşlev:** SQL dışındaki sunucu hatalarını yakalar.

---

### 7. Sunucuyu Başlatma

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0',port=port, debug=False)

```

* **if __name__ == '__main__':** Bu kontrol Flask sunucusunun istem dışı ayağa kalkmasını engeller.
* **Port:** İşletim sistemindeki `PORT` isimli çevre değişkenine bakar, eğer sistemde `PORT` isimli bir değişken yoksa varsayılan olarak 3000 portunda sunucuyu ayağa kaldırır.
* **app.run:** Uygulamayı ayağa kaldırır. 