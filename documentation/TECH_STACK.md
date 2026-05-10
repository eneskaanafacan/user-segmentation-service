# Tech Stack

Bu dökümantasyon istenen projeyi gerçekleştirirken kullandığım teknolojileri ve neden bu teknolojileri tercih ettiğimi sade bir dille anlatmaktadır.

## Web Framework Olarak Flask

Flask Web geliştirme alanında kullanılan hafif bir framework’tür. Öyle ki bazı kaynaklarda “micro-framework” olarak bile tanımlanmıştır (bkz. O’Reilly Flask Web Development by Miguel Grinberg).

Flask temel hizmetleri sunan sade bir yapıda size gelir. Siz isteğiniz doğrultusunda eklentiler ekleyerek yapıyı dilediğiniz kadar komplike yapabilirsiniz. Programlama dili olarak Python kullanması, geniş dökümantasyon ve öğrenme kaynağı desteği ile de öğrenmesi ve kullanması alternatiflerine göre nispeten kolay bir framework olarak karşımıza çıkmaktadır.

### Peki Ben Bu Proje İçin Neden Flask Seçtim?

Temel seviyede Flask ve Python hakkında bilgi sahibi olmam ve öğrenmeye ilgimin olması, kısıtlı sürede hızlı ve kolay geliştirme yapma isteğim, gereğinden fazla güçlü bir framework kullanmaya gerek duymamam (Spring Boot gibi), basit mimari yapı, az dosya, hızlı üretim. Flask seçmemin başlıca sebepleri bunlardır.

## Veritabanı Motoru Olarak SQLite

CODE_WALKTHROUGH.md dosyasında da detaylı şekilde anlattığım gibi gelen istekleri geçici bir veritabanına kaydedip oradan gerekli segmentasyon işlemlerini yaptım. Bu kurguladığım mimaride ayrı bir SQL sunucu ile uğraşmak bu aşamada verimsiz geldi. Bu sebeple SQLite’ın serverless yapısı ve yönetim kolaylığı seçmemdeki ana sebep oldu. Ancak staj sürecim devam etsin veya etmesin proje büyürse Flask’ın sağladığı esneklik ile gerekirse daha farklı veritabanı çözümlerine hızlıca geçilebilir. Hatta Dokku gibi PaaS çözümleri kullanılarak birden fazla veritabanına veya uygulamaya kolayca bağlanılıp tümüyle bir HTTP sunucu servisi olarak proje geliştirilmeye devam edilebilir.

## LLM Olarak Gemini 3 PRO

Projeyi yaparken LLM olaram Gemini 3 PRO kullandım. 3-4 Prompt kullandım ve hepsini dışa aktarıp /transricpt dizinin altına tüm detayıyla ekledim.