from django.shortcuts import render
from .models import Vendas

def vendas(request):
    vendas = Vendas.objects.all()
    return render(request, 'vendas.html', {'vendas': vendas})
