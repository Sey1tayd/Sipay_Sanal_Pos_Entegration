from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_form, name='payment_form'),
    path('payment/', views.payment_form, name='payment_form'),
    path("payment/result/", views.complete_payment, name="payment_result"),
    path("payment/cancel/", views.cancel_payment, name="cancel_payment"),
]
