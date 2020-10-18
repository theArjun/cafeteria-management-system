from django.urls import path

from .views import get_stock

urlpatterns = [
    path('get_stock/<int:id>', get_stock, name='get_stock')
]
