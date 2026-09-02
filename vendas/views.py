from django.shortcuts import get_object_or_404, render, redirect
from .models import Vendas

# Função que lista os fechamentos registrados
def listar_vendas(request):
    vendas = Vendas.objects.all() # É um SELECT executado pelo Django ORM que retornar todos os registros
    return render(request, 'vendas.html', {'vendas': vendas}) # Renderiza o template HTTP
    # Parâmetros: request é utilazado para construir corretamente a resposta - template utilizado para montar - nome que o template usa:variável com os dados

# Função que resgata as informações de um registro em específico
def detalhe_venda(request, pk):
    # Retorna um objeto ou erro 404
    venda = get_object_or_404(Vendas, pk=pk)

    return render(request, 'detalhe_vendas.html', {'venda': venda})

# Função que criar um registro de fechamento
def criar_vendas(request):
    # Ao formulário ser enviado, cai em POST - executando a criação do objeto no banco
    if request.method == 'POST':
        data = request.POST['data']
        tipo_pagamento = request.POST['tipo_pagamento']
        valor_total = request.POST['valor_total']
        bandeira_cartao = request.POST['bandeira_cartao']
        responsavel = request.POST['responsavel']
        num_caixa = request.POST['num_caixa']
        obs = request.POST['obs']
        # Se o checkbox for marcado / retorna "on" e compara / a comparação retorna True
        conferido = request.POST.get('conferido') == 'on'

        # Cria um objeto do tipo venda
        Vendas.objects.create(data=data, tipo_pagamento=tipo_pagamento, valor_total=valor_total, bandeira_cartao=bandeira_cartao, responsavel=responsavel, num_caixa=num_caixa, obs=obs, conferido=conferido)
        return redirect('listar_vendas')

    venda = Vendas() # Cria um objeto Vendas vazio (puxando os valores default para pré-preencher o formulário)

    return render(request, 'form_vendas.html', {'venda': venda, 'titulo': 'Novo Fechamento'})

# Função para editar o registro de um fechamento (mesmo princípio da criaçáo)
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

        venda.save() # Salva a instância atual, reescrevendo os dados anteriores
        return redirect('listar_vendas')

    return render(request, 'form_vendas.html', {'venda': venda, 'titulo': 'Editar Fechamento'})

# Função para excluir o registro de um fechamento
def excluir_vendas(request, pk):
    venda = get_object_or_404(Vendas, pk=pk)

    # Ao confirmar a exclusão, cai em POST - executando a exclusão do objeto no banco
    if request.method == 'POST':
        venda.delete()
        return redirect('listar_vendas')

    return render(request, 'confirmar_exclusao.html', {'venda': venda})
