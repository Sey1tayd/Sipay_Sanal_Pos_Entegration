from django.shortcuts import render
from .utils import generate_hash_key
import json
from uuid import uuid4
from django.views.decorators.http import require_http_methods
import requests
from .utils import generate_complete_payment_hash_key
from django.urls import reverse
from .models import Payment


def payment_form(request):
    # Sabit değerler (bunları ortam değişkeninden çekmen gerekir, ama hadi neyse)
    # TODO: Bu değerleri environment variables'dan al
    secret_key = "b46a67571aa1e7ef5641dc3fa6f1712a"
    merchant_key = "$2y$10$HmRgYosneqcwHj.UH7upGuyCZqpQ1ITgSMj9Vvxn.t6f.Vdf2SQFO"

    # Sahte sipariş verileri (normalde formdan gelir ya da DB’den çekilir)
    invoice_id = f"INV-{uuid4().hex[:10].upper()}"
    total = "1.00"
    currency_code = "TRY"
    installments_number = "1"
    name = "John"
    surname = "Doe"
    invoice_description = f"{invoice_id} nolu sipariş ödemesi"
    bill_email = "test@example.com"
    bill_phone = "5555555555"
    
    # Payment kaydı oluştur
    Payment.objects.create(
        invoice_id=invoice_id,
        total=total,
        currency_code=currency_code,
        status='pending'
    )
    
    items = json.dumps([
        {
            "name": "Test Product",
            "price": float(total),
            "quantity": 1,
            "description": "Some Description"
        }
    ])
    return_url = request.build_absolute_uri(reverse("payment_result"))
    cancel_url = request.build_absolute_uri(reverse("cancel_payment"))
    user_ip = request.META.get("REMOTE_ADDR", "127.0.0.1")

    # Hash key üretimi (mandatory)
    hash_key = generate_hash_key(
        total=total,
        installment=installments_number,
        currency_code=currency_code,
        merchant_key=merchant_key,
        invoice_id=invoice_id,
        app_secret=secret_key
    )

    # Context ile birlikte formu gönder
    context = {
        "merchant_key": merchant_key,
        "currency_code": currency_code,
        "installments_number": installments_number,
        "invoice_id": invoice_id,
        "invoice_description": invoice_description,
        "name": name,
        "surname": surname,
        "total": total,
        "items": items,
        "cancel_url": cancel_url,
        "return_url": return_url,
        "hash_key": hash_key,
        "bill_email": bill_email,
        "bill_phone": bill_phone,
        "user_ip": user_ip
    }

    return render(request, "payment_3d/payment_form.html", context)


@require_http_methods(["GET", "POST"])  # Sadece GET ve POST isteklerini kabul et
def complete_payment(request):
    
    # Sipay'den gelen istekleri doğrula
    if request.method == 'POST':
        # Referer kontrolü (opsiyonel güvenlik)
        referer = request.META.get('HTTP_REFERER', '')
        if referer and 'sipay.com.tr' not in referer:
            print(f"⚠️ Şüpheli referer: {referer}")
    
    data = request.POST or request.GET

    print("🎯 Tam gelen veri (POST/GET karışık):")
    for key, val in data.items():
        print(f"  {key} → {val}")

    md_status = data.get("md_status")
    invoice_id = data.get("invoice_id")
    order_id = data.get("order_id")  # Bu Sipay'in döndürdüğü gerçek order ID
    sipay_status = data.get("sipay_status")
    status_code = data.get("status_code")
    status_description = data.get("status_description")

    print("🧪 MdStatus:", md_status)
    print("📦 invoice_id:", invoice_id)
    print("🧾 order_id:", order_id)
    print("🔍 Sipay Status:", sipay_status)
    print("📊 Status Code:", status_code)
    print("📝 Status Description:", status_description)

    # Payment kaydını güncelle
    payment = None
    try:
        payment = Payment.objects.get(invoice_id=invoice_id)
        payment.order_id = order_id
        payment.md_status = md_status
        payment.sipay_status = sipay_status
        payment.status_code = status_code
        payment.status_description = status_description
        payment.save()
    except Payment.DoesNotExist:
        print(f"⚠️ Payment kaydı bulunamadı: {invoice_id}")

    # Sipay'den gelen status bilgilerini kontrol et
    # sipay_status: 0 = başarılı, 1 = başarısız
    # status_code: 69 = Transaction Pending (başarılı)
    
    # 3D Secure durumlarını kontrol et
    if md_status == "0":  # 3D Secure başarısız
        if payment:
            payment.status = 'failed'
            payment.save()
            
        return render(request, "payment_3d/payment_result.html", {
            "result": {
                "error": "3D Secure doğrulaması başarısız (MdStatus = 0)",
                "md_status": md_status,
                "sipay_status": sipay_status,
                "status_code": status_code,
                "status_description": status_description
            }
        })
    
    elif md_status == "2":  # 3D Secure deneme sayısı aşıldı
        if payment:
            payment.status = 'failed'
            payment.save()
            
        return render(request, "payment_3d/payment_result.html", {
            "result": {
                "error": "3D Secure deneme sayısı aşıldı (MdStatus = 2)",
                "md_status": md_status,
                "sipay_status": sipay_status,
                "status_code": status_code,
                "status_description": status_description
            }
        })
    
    elif md_status == "3":  # 3D Secure sistem hatası
        if payment:
            payment.status = 'failed'
            payment.save()
            
        return render(request, "payment_3d/payment_result.html", {
            "result": {
                "error": "3D Secure sistem hatası (MdStatus = 3)",
                "md_status": md_status,
                "sipay_status": sipay_status,
                "status_code": status_code,
                "status_description": status_description
            }
        })
    
    elif md_status == "4":  # 3D Secure iptal edildi
        if payment:
            payment.status = 'cancelled'
            payment.save()
            
        return render(request, "payment_3d/payment_result.html", {
            "result": {
                "error": "3D Secure işlemi iptal edildi (MdStatus = 4)",
                "md_status": md_status,
                "sipay_status": sipay_status,
                "status_code": status_code,
                "status_description": status_description
            }
        })
    
    elif md_status != "1":  # Diğer 3D Secure hataları
        if payment:
            payment.status = 'failed'
            payment.save()
            
        return render(request, "payment_3d/payment_result.html", {
            "result": {
                "error": f"3D Secure doğrulaması başarısız (MdStatus = {md_status})",
                "md_status": md_status,
                "sipay_status": sipay_status,
                "status_code": status_code,
                "status_description": status_description
            }
        })
    
    # 3D Secure başarılı (md_status = 1), şimdi ödeme durumunu kontrol et
    if sipay_status == "0" and status_code == "69":  # Transaction Pending = başarılı
        # Ödeme başarılı, complete API'sine gerek yok
        if payment:
            payment.status = 'completed'
            payment.save()
            
        return render(request, "payment_3d/payment_result.html", {
            "result": {
                "status": "success",
                "message": "Ödeme başarıyla tamamlandı",
                "order_id": order_id,
                "invoice_id": invoice_id,
                "sipay_status": sipay_status,
                "status_code": status_code,
                "status_description": status_description
            }
        })

    # Eğer ödeme henüz tamamlanmamışsa, complete API'sini çağır
    # (Bu durumda sipay_status != "0" veya status_code != "69")
    if sipay_status != "0" or status_code != "69":
        # Hazırlıklar
        # TODO: Bu değerleri environment variables'dan al
        merchant_key = "$2y$10$HmRgYosneqcwHj.UH7upGuyCZqpQ1ITgSMj9Vvxn.t6f.Vdf2SQFO"
        secret_key = "b46a67571aa1e7ef5641dc3fa6f1712a"

        hash_key = generate_complete_payment_hash_key(
            invoice_id=invoice_id,
            order_id=order_id,
            merchant_key=merchant_key,
            app_secret=secret_key
        )

        payload = {
            "merchant_key": merchant_key,
            "invoice_id": invoice_id,
            "order_id": order_id,
            "hash_key": hash_key
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        try:
            # Sipay'in doğru endpoint'ini kullan - 3D Secure sonrası ödeme tamamlama
            response = requests.post(
                "https://provisioning.sipay.com.tr/ccpayment/api/sale/complete3D",
                headers=headers,
                json=payload
            )

            print("🌐 completePayment API yanıtı (raw text):")
            print(response.text)

            # Response'un JSON olup olmadığını kontrol et
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
            else:
                # HTML yanıt gelirse, ödeme durumunu kontrol et
                if response.status_code == 200:
                    result = {
                        "status": "success",
                        "message": "Ödeme başarıyla tamamlandı",
                        "order_id": order_id,
                        "invoice_id": invoice_id,
                        "sipay_status": sipay_status,
                        "status_code": status_code,
                        "status_description": status_description
                    }
                else:
                    result = {
                        "status": "error",
                        "message": f"API yanıt kodu: {response.status_code}",
                        "raw_response": response.text[:500]  # İlk 500 karakter
                    }
            
            # Payment durumunu güncelle
            if payment:
                if result.get('status') == 'success':
                    payment.status = 'completed'
                else:
                    payment.status = 'failed'
                payment.save()
                
        except Exception as e:
            result = {"error": "completePayment API başarısız", "detail": str(e)}
            
            # Payment durumunu güncelle
            if payment:
                payment.status = 'failed'
                payment.save()

        return render(request, "payment_3d/payment_result.html", {
            "result": result
        })
    
    # Ödeme zaten başarılı, sadece sonucu göster
    return render(request, "payment_3d/payment_result.html", {
        "result": {
            "status": "success",
            "message": "Ödeme başarıyla tamamlandı",
            "order_id": order_id,
            "invoice_id": invoice_id,
            "sipay_status": sipay_status,
            "status_code": status_code,
            "status_description": status_description
        }
    })


def cancel_payment(request):
    return render(request, "payment_3d/payment_cancel.html")
