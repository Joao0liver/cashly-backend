from django.urls import path
from . import views

# Registro dos caminhos que o app vendas possui
# Rota - view usada - nome (geram um padrão de URL)
urlpatterns = [
    path('', views.listar_vendas, name='listar_vendas'),
    path('<int:pk>/detalhe/', views.detalhe_venda, name='detalhe_vendas'), # Necessita de <int:pk> para indicar de qual registro se trata a operação
    path('novo/', views.criar_vendas, name='criar_vendas'),
    path('<int:pk>/editar/', views.editar_vendas, name='editar_vendas'),
    path('<int:pk>/excluir/', views.excluir_vendas, name='excluir_vendas'),
]