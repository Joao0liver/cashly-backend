from django.shortcuts import get_object_or_404, render, redirect
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
        conferido = request.POST.get('conferido') == 'on'

        Vendas.objects.create(data=data, tipo_pagamento=tipo_pagamento, valor_total=valor_total, bandeira_cartao=bandeira_cartao, responsavel=responsavel, num_caixa=num_caixa, obs=obs, conferido=conferido)
        return redirect('listar_vendas')

    venda = Vendas()

    return render(request, 'form_vendas.html', {'venda': venda, 'titulo': 'Novo Fechamento'})

def editar_vendas(request, pk):
    venda = get_object_or_404(Vendas, pk=pk)

    if request.method == 'POST':
        venda.data = request.POST['data']
        venda.tipo_pagamento = request.POST['tipo_pagamento']
        venda.valor_total = request.POST['valor_total']
        venda.bandeira_cartao = request.POST['bandeira_cartao']
        venda.responsavel = request.POST['responsavel']
        venda.num_caixa = request.POST['num_caixa']
        venda.obs = request.POST['obs']
        venda.conferido = request.POST.get('conferido') == 'on'

        venda.save()
        return redirect('listar_vendas')

    return render(request, 'form_vendas.html', {'venda': venda, 'titulo': 'Editar Fechamento'})

def excluir_vendas(request, pk):
    venda = venda = get_object_or_404(Vendas, pk=pk)

    if request.method == 'POST':
        venda.delete()
        return redirect('listar_vendas')

    return render(request, 'confirmar_exclusao.html', {'venda': venda})

