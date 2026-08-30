from django.shortcuts import render, redirect
from .models import Vendas

def listar_vendas(request):
    vendas = Vendas.objects.all()
    return render(request, 'vendas.html', {'vendas': vendas})

def criar_vendas(request):
    if request.method == 'POST':
        data = request.POST['data']
        tipo_pagamento = request.POST['tipo_pagamento']
        valor_total = request.POST['valor_total']
        bandeira_cartao = request.POST['bandeira_cartao']
        responsavel = request.POST['responsavel']
        num_caixa = request.POST['num_caixa']
        obs = request.POST['obs']
        conferido = request.POST['conferido']

        Vendas.objects.create(data=data, tipo_pagamento=tipo_pagamento, valor_total=valor_total, bandeira_cartao=bandeira_cartao, responsavel=responsavel, num_caixa=num_caixa, obs=obs, conferido=conferido)
        return redirect('listar_vendas')

    return render(request, 'form_vendas.html', {'titulo': 'Novo Fechamento'})

def editar_vendas(request, pk):
    return 0

def excluir_vendas(request, pk):
    return 0

