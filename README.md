# Sipay 3D Secure Payment Integration

Bu proje, Sipay ödeme sistemi ile 3D Secure entegrasyonu sağlayan Django uygulamasıdır.

## Özellikler

- 3D Secure ödeme formu
- Ödeme sonuç takibi
- Payment kayıtları veritabanında saklama
- Django Admin paneli entegrasyonu
- Responsive tasarım

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Veritabanı migrasyonlarını çalıştırın:
```bash
python manage.py migrate
```

3. Django Admin kullanıcısı oluşturun:
```bash
python manage.py createsuperuser
```

4. Sunucuyu başlatın:
```bash
python manage.py runserver
```

## Kullanım

1. Tarayıcınızda `http://localhost:8000` adresine gidin
2. Ödeme formu otomatik olarak yüklenecek
3. Test kartı bilgileri ile ödeme yapabilirsiniz:
   - Kart Numarası: 4508034508034509
   - Son Kullanma: 12/2026
   - CVV: 000

## Güvenlik Notları

⚠️ **ÖNEMLİ**: Bu proje test amaçlıdır. Production ortamında:

1. API anahtarlarını environment variables olarak saklayın
2. DEBUG modunu kapatın
3. ALLOWED_HOSTS ayarlarını yapılandırın
4. HTTPS kullanın

## API Anahtarları

Şu anda kodda hardcoded olan anahtarlar:
- `secret_key`: "b46a67571aa1e7ef5641dc3fa6f1712a"
- `merchant_key`: "$2y$10$HmRgYosneqcwHj.UH7upGuyCZqpQ1ITgSMj9Vvxn.t6f.Vdf2SQFO"

## Dosya Yapısı

```
complate_payment/
├── complate_payment/          # Ana Django projesi
│   ├── settings.py           # Proje ayarları
│   ├── urls.py               # Ana URL yapılandırması
│   └── ...
├── payment_3d/               # Ödeme uygulaması
│   ├── views.py              # View fonksiyonları
│   ├── models.py             # Veritabanı modelleri
│   ├── utils.py              # Yardımcı fonksiyonlar
│   └── urls.py               # URL yapılandırması
├── templates/                # HTML şablonları
│   └── payment_3d/
│       ├── payment_form.html
│       ├── payment_result.html
│       └── payment_cancel.html
└── manage.py
```

## Ödeme Akışı

1. Kullanıcı `/` adresine gider
2. Otomatik olarak `/payment/` adresine yönlendirilir
3. Ödeme formu gösterilir
4. Form Sipay'e gönderilir
5. 3D Secure doğrulaması yapılır
6. Sonuç `/payment/result/` adresine döner
7. Ödeme durumu kontrol edilir:
   - `sipay_status: 0` ve `status_code: 69` = Başarılı
   - Diğer durumlar = Başarısız
8. Gerekirse complete API çağrılır
9. Ödeme tamamlanır veya iptal edilir

## Hata Ayıklama

Ödeme işlemlerini takip etmek için:
1. Django Admin paneline gidin (`/admin/`)
2. "Payments" bölümünden ödeme kayıtlarını görüntüleyin
3. Console loglarını kontrol edin

## Lisans

Bu proje eğitim amaçlıdır.
