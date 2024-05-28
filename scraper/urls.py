from django.urls import path
from . import views

urlpatterns = [
    path('detectPrice/', views.detect_price_pattern, name='detect_price_pattern'),
]
