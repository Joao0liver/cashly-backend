from django.urls import path
from . import views

urlpatterns = [
    path('', views.relatorios, name='relatorios'),
    path('pdf/', views.relatorio_vendas_pdf, name='relatorio_vendas_pdf'),
]