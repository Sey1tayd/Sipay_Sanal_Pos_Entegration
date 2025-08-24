from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os
import base64
import hmac
import hashlib


def generate_hash_key(total, installment, currency_code, merchant_key, invoice_id, app_secret):
    data = f"{total}|{installment}|{currency_code}|{merchant_key}|{invoice_id}"

    iv = hashlib.sha1(os.urandom(16)).hexdigest()[:16]
    salt = hashlib.sha1(os.urandom(16)).hexdigest()[:4]

    password = hashlib.sha1(app_secret.encode()).hexdigest()
    salt_with_password = hashlib.sha256((password + salt).encode()).hexdigest()

    cipher = AES.new(salt_with_password.encode()[:32], AES.MODE_CBC, iv.encode())
    encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))

    msg_encrypted_bundle = f"{iv}:{salt}:{base64.b64encode(encrypted).decode()}"
    msg_encrypted_bundle = msg_encrypted_bundle.replace('/', '__')

    print("HASH KEY:", msg_encrypted_bundle)

    return msg_encrypted_bundle


def generate_complete_payment_hash_key(invoice_id, order_id, merchant_key, app_secret):
    # Sipay'in beklediği format: invoice_id|order_id|merchant_key
    data = f"{invoice_id}|{order_id}|{merchant_key}"
    
    # HMAC-SHA256 ile imzalama
    signature = hmac.new(
        app_secret.encode('utf-8'), 
        data.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    return signature
