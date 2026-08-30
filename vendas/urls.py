from django.urls import path
from . import views

urlpatterns = [
    path('', views.vendas, name='listar_vendas'),
]