from django.urls import path

from .views import (CustomerView, Login, PaymentView,
                    TokenAuthenticationAPIView, UserView)

urlpatterns = [
    path('customers/', CustomerView.as_view(), name='customer-list'),
    path('payments/<int:customer_id>/', PaymentView.as_view(), name='payment-list'),  
    path('users/', UserView.as_view(), name='user-list'), 
    path('sign-in/', Login.as_view(),name='login'),
    path('token/authenticate/<str:token>/', TokenAuthenticationAPIView.as_view(), name='token-authentication'),
]