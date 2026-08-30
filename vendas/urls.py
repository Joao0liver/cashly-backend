from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_vendas, name='listar_vendas'),
    path('<int:pk>/detalhe/', views.detalhe_venda, name='detalhe_vendas'),
    path('novo/', views.criar_vendas, name='criar_vendas'),
    path('<int:pk>/editar/', views.editar_vendas, name='editar_vendas'),
    path('<int:pk>/excluir/', views.excluir_vendas, name='excluir_vendas'),
]