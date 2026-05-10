# 1. Python'un hafif bir sürümünü temel imaj olarak alıyoruz
FROM python:3.9-slim

# 2. Konteyner içinde çalışma dizinini /app olarak ayarlıyoruz
WORKDIR /app

# 3. Önce gereksinim dosyasını kopyalıyoruz (Cache optimizasyonu için)
COPY requirements.txt .

# 4. Bağımlılıkları yüklüyoruz
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kalan tüm proje dosyalarını (app.py, static/ vb.) kopyalıyoruz
COPY . .

# 6. Uygulamayı başlatıyoruz.
# app.py içindeki kod PORT değişkenini okuyup ona göre başlayacak.
CMD ["python", "app.py"]