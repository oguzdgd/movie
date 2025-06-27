# 🎬 MovieApp XML API: Kapsamlı Bir XML ve Web Servisleri Projesi

**MovieApp XML API**, modern web teknolojileriyle XML tabanlı veri alışverişinin nasıl entegre edilebileceğini gösteren, zengin özellikli bir RESTful API projesidir. Bu proje, **155-8056 XML ve Web Servisleri** dersi final projesi olarak, derste işlenen tüm teorik konuların pratik bir uygulaması olarak geliştirilmiştir.

Uygulama, kullanıcıların bir film kataloğunu keşfetmelerine, kendi izleme listelerini yönetmelerine ve filmler hakkında yorumlar yaparak sosyal bir etkileşimde bulunmalarına olanak tanır. Projenin temel felsefesi, istemci ve sunucu arasındaki tüm veri iletişimini **XML formatı** üzerinden gerçekleştirmek ve bu süreçte XSD, XPath, XSLT gibi temel XML teknolojilerini etkin bir şekilde kullanmaktır.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-3.14-A30000?style=for-the-badge)](https://www.django-rest-framework.org/)
[![XML](https://img.shields.io/badge/XML-W3C-orange?style=for-the-badge&logo=xml)](https://www.w3.org/XML/)
[![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman)](https://www.postman.com/)

---

## ✨ Projenin Öne Çıkan Özellikleri

-   **Katmanlı Mimari:** Django çatısı altında, veri (models), iş mantığı (views/serializers) ve sunum (XSLT) katmanları birbirinden net bir şekilde ayrılmıştır.
-   **XML Odaklı API:** Tüm veri alışverişi, `Content-Type: application/xml` başlığı ile XML formatında gerçekleştirilir.
-   **Güçlü Veri Doğrulama:** Backend'e gelen tüm XML verileri, önceden tanımlanmış **XSD şemaları** kullanılarak doğrulanır.
-   **Sunucu Taraflı XML Dönüşümü:** XML verileri, **XSLT** kullanılarak sunucu tarafında doğrudan tarayıcıda görüntülenebilir **HTML sayfalarına** dönüştürülür.
-   **Gelişmiş Veri Bağlama (Data Binding):** Django REST Framework'ün `Serializer` sınıfları kullanılarak, veritabanı nesneleri ile XML gösterimleri arasında güçlü ve esnek bir bağ kurulmuştur.
-   **Güvenlik Mekanizmaları:** Token tabanlı kimlik doğrulama ve rol tabanlı (Admin/Normal Kullanıcı) yetkilendirme.
-   **API Sürümleme:** `/api/v1/` gibi URL tabanlı sürümleme stratejisi ile API'nin geleceğe dönük olması.
-   **Harici Servis Entegrasyonu:** The Movie Database (TMDB) API'sinden film verilerini çekip sisteme aktarma özelliği.
-   **Otomatik API Dokümantasyonu:** **Swagger UI** ve **ReDoc** ile tüm endpoint'lerin otomatik olarak belgelenmesi.
-   **Kapsamlı Otomatik Testler:** Django'nun test altyapısı ile API'nin tüm kritik işlevlerini doğrulayan bir test suiti.
-   **Performans Analizi:** Büyük XML dosyaları için DOM ve Olay-tabanlı (iterparse) ayrıştırma yöntemlerinin performansını karşılaştıran bir analiz aracı.

---

## 🛠️ Kullanılan Teknolojiler

| Kategori              | Teknoloji / Kütüphane       | Amaç                                                                    |
| --------------------- | --------------------------- | ----------------------------------------------------------------------- |
| **Backend**           | Python, Django              | Projenin ana çatısı, ORM, veritabanı yönetimi ve URL yönlendirme.        |
| **API Geliştirme**    | Django REST Framework (DRF) | Güçlü REST API'leri oluşturma, serileştirme, kimlik doğrulama.   |
| **XML İşleme**        | `lxml`                      | Yüksek performanslı XML/HTML ayrıştırma, XSD, XPath ve XSLT işlemleri.    |
| **API XML Desteği**   | `djangorestframework-xml`   | DRF'nin XML formatında istekleri işlemesini ve yanıtlar üretmesini sağlar.  |
| **Veritabanı**        | SQLite                      | Geliştirme ortamı için hafif ve kurulum gerektirmeyen veritabanı.       |
| **API Dokümantasyonu**| `drf-yasg`                  | Swagger/OpenAPI şemaları üreterek interaktif dokümantasyon sağlar.    |
| **Harici İstekler**   | `requests`                  | Harici API'lere (TMDB) HTTP istekleri göndermek için.                     |
| **Ortam Yönetimi**    | `python-dotenv`, `venv`     | Sanal ortam yönetimi ve hassas bilgilerin (`.env`) güvenli saklanması. |

---

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları izleyin.

### 1. Ön Gereksinimler
- Python (3.8+)
- Git

### 2. Kurulum
```bash
# 1. Projeyi klonlayın
git clone https://github.com/kullanici-adiniz/proje-adiniz.git
cd proje-adiniz

# 2. Sanal ortam oluşturun ve aktive edin
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 3. Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt
```

### 3. Yapılandırma
1.  Proje kök dizininde `.env` adında bir dosya oluşturun.
2.  `settings.py` dosyasındaki `SECRET_KEY` değerini kopyalayıp `.env` dosyasına `SECRET_KEY='sizin-anahtarınız'` şeklinde yapıştırın.
3.  The Movie Database (TMDB) sitesinden aldığınız API anahtarını `.env` dosyasına `TMDB_API_KEY='sizin-tmdb-anahtarınız'` şeklinde ekleyin.
4.  Geliştirme için `.env` dosyasına `DEBUG=True` satırını ekleyin.

### 4. Veritabanı ve Başlangıç Verileri
```bash
# 1. Veritabanı tablolarını oluşturun
python manage.py migrate

# 2. Admin paneli için bir süper kullanıcı oluşturun
python manage.py createsuperuser

# 3. Örnek film verilerini XML dosyalarından veritabanına yükleyin
python manage.py load_movies_from_xml
```

### 5. Sunucuyu Başlatma
```bash
python manage.py runserver
```
Uygulama artık `http://127.0.0.1:8000/` adresinde çalışıyor olacaktır.

---

## 🗺️ Proje Haritası ve Önemli URL'ler

-   **Admin Paneli:** `http://127.0.0.1:8000/admin/`
    -   *Not: `createsuperuser` komutu ile oluşturduğunuz admin bilgileriyle giriş yapabilirsiniz.*
-   **Swagger API Dokümantasyonu:** `http://127.0.0.1:8000/swagger/`
-   **ReDoc API Dokümantasyonu:** `http://127.0.0.1:8000/redoc/`

### API Endpoint'leri (v1)
Tüm API endpoint'leri `/api/v1/` ön eki ile başlar. Detaylı bilgi ve test için Swagger arayüzünü kullanın.

### HTML Arayüzü (XSLT ile)
-   **Film Listesi:** `http://127.0.0.1:8000/api/v1/html/movies/`
-   **Film Detayı:** `http://127.0.0.1:8000/api/v1/html/movies/{movie_id}/`

---

## 📁 Proje Mimarisi ve Dosya Yapısı

Proje, Django'nun standart "uygulama" tabanlı mimarisini takip eder.

-   `movieproject/`: Ana proje yapılandırma dosyalarını içerir (`settings.py`, `urls.py`).
-   `api/`: Projenin tüm ana iş mantığını, modellerini, view'larını ve serializer'larını içeren ana uygulama.
    -   `models.py`: Veritabanı şemasını tanımlayan Django modelleri (Movie, Comment, vb.).
    -   `views.py`: API endpoint'lerinin mantığını içeren fonksiyonlar.
    -   `serializers.py`: Modeller ve XML arasında veri bağlamayı (data binding) sağlayan DRF Serializer sınıfları.
    -   `urls.py`: `api` uygulamasına özel URL yönlendirmeleri.
    -   `tests.py`: Uygulamanın otomatik testleri.
    -   `management/commands/`: Özel `manage.py` komutlarını (örn: `load_movies_from_xml`) barındırır.
-   `data/`: Veritabanına yüklenecek olan örnek XML dosyalarını içerir.
-   `schemas/`: Veri doğruluğunu sağlamak için kullanılan XSD ve DTD şema dosyaları.
-   `xslt/`: XML verisini HTML'e dönüştürmek için kullanılan XSLT stylesheet dosyaları.

---

## ✅ Ders Gereksinimlerinin Karşılanması

Bu proje, dersin 15 maddelik gereksinim listesini aşağıdaki şekilde karşılamaktadır:

| Madde No | Konu                               | Projedeki Uygulama                                                                                                     |
| :------- | :--------------------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| 1        | XML Fundamentals                   | Farklı veri türleri (filmler, kullanıcılar, yorumlar) için yapısal XML dökümanları oluşturuldu. CDATA kullanıldı.           |
| 2        | XML Validation                     | Gelen veriler sunucu tarafında **XSD** şemalarıyla, hata mesajları ise **DTD** konseptiyle doğrulandı.                       |
| 3        | XML Transformation                 | **XPath** ile XML içinde veri arandı, **XSLT** ile XML verileri sunucu tarafında HTML'e dönüştürüldü.                      |
| 4        | XML Parsing Techniques             | DOM-benzeri (`lxml.etree`) ve olay-tabanlı (`iterparse`) ayrıştırma yöntemleri incelendi ve performansları karşılaştırıldı. |
| 5        | Web Services Fundamentals          | Proje, **REST** mimarisi prensiplerine uygun olarak hizmet odaklı bir yapıda geliştirildi.                                  |
| 6        | RESTful Web Services with XML      | Django REST Framework kullanılarak, tüm veri alışverişini XML ile yapan bir RESTful API tasarlandı.                         |
| 7        | Consuming External Web Services    | TMDB API'sinden (JSON) veri çekilip, işlenip, projenin iç XML yapısına uygun olarak veritabanına aktarıldı.             |
| 8        | API Documentation and Testing      | **Swagger/ReDoc** ile otomatik API dokümantasyonu oluşturuldu. API endpoint'leri **Postman** ile test edildi.                |
| 9        | Web Service Security               | **Token** tabanlı kimlik doğrulama ve rol bazlı (admin/kullanıcı) **yetkilendirme** mekanizmaları entegre edildi.         |
| 10       | Data Binding                       | DRF **Serializer** sınıfları kullanılarak veritabanı nesneleri ile XML gösterimleri arasında serileştirme/deserileştirme yapıldı. |
| 11       | Version Control                    | Proje geliştirme süreci boyunca **Git** ve anlamlı commit mesajları kullanıldı. Hassas dosyalar `.gitignore` ile korundu.     |
| 12       | Real-World Applications            | Sosyal etkileşim özellikleri olan bir film kataloğu uygulaması, gerçek dünya senaryosunu simüle eder.                        |
| 13       | API Versioning                     | URL tabanlı sürümleme (`/api/v1/`) stratejisi benimsenerek API'nin gelecekteki değişikliklere hazır olması sağlandı.        |
| 14       | Web Service Testing and Debugging  | Django'nun test çatısı kullanılarak API'nin temel işlevleri için **otomatik testler** yazıldı.                          |
| 15       | Language Flexibility               | Proje, dersin önerdiği C#/.NET yerine **Python/Django** kullanılarak geliştirildi.                                         |

---

## 🤝 Katkıda Bulunma (Contributing)

Bu proje şu an için kişisel bir ders projesi olsa da, her türlü fikir, öneri ve katkıya açıktır. Eğer bir hata bulursanız veya yeni bir özellik önermek isterseniz, lütfen bir "Issue" açmaktan çekinmeyin.
"Pull Request" göndermek isterseniz, harika olur! Katkıda bulunmak için lütfen aşağıdaki adımları izleyin:

1.  Bu depoyu "Fork" edin.
2.  Yeni özelliğiniz veya hata düzeltmeniz için yeni bir "branch" oluşturun (`git checkout -b ozellik/yeni-film-listeleme`).
3.  Değişikliklerinizi yapın ve "commit" edin (`git commit -m 'Yeni özellik: Film listeleme eklendi'`).
4.  Oluşturduğunuz "branch"i kendi deponuza "push" edin (`git push origin ozellik/yeni-film-listeleme`).
5.  Son olarak, bu depoya bir "Pull Request" açın.

Eğer bir hata bulduysanız veya bir fikriniz varsa, bir "Issue" açarak da tartışmaya başlayabilirsiniz.

---
