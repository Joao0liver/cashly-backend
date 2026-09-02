from datetime import datetime
from calendar import monthrange # Informa quantos dias existem em um determinado mês

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render

# Biblioteca utilizada para criar o arquivo .pdf
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT # Alinhamento
from reportlab.lib.pagesizes import A4 # Tamanho da página
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # Estilos
from reportlab.lib.units import mm # Medida utilizada (milímetros)
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,)

# Importa o model do app vendas
from vendas.models import Vendas

# Renderiza o template
def relatorios(request):
    return render(request, 'relatorios.html')

# Função que formata o valor na moeda brasileira (reais)
def formatar_moeda(valor):
    # Transforma em string e substitui o ponto por vírgula e vice-versa
    return (
        f'R$ {valor:,.2f}'
        .replace(',', 'X')
        .replace('.', ',')
        .replace('X', '.')
    )

# Função que gera o arquivo .pdf
def relatorio_vendas_pdf(request):

    # Resgata o parâmetro "tipo" da URL (dia ou mês)
    tipo = request.GET.get('tipo')

    # Inicializa as variáveis de data
    data_inicio = None
    data_fim = None
    periodo = ''

    if tipo == 'dia':

        # Resgata o parâmetro "data" da URL
        data = request.GET.get('data')

        if not data:
            return HttpResponse(
                'Nenhuma data foi informada.',
                status=400
            )

        try:
            # Converte a string em objeto date
            data_inicio = datetime.strptime(
                data,
                '%Y-%m-%d'
            ).date()
        except ValueError:
            # Caso a data resgatada esteja em um formato errado
            return HttpResponse(
                'Data inválida.',
                status=400
            )

        data_fim = data_inicio # Relatório de dia único
        periodo = data_inicio.strftime('%d/%m/%Y') # Formata a data

    elif tipo == 'mes':

        mes = request.GET.get('mes')

        if not mes:
            return HttpResponse(
                'Nenhum mês foi informado.',
                status=400
            )

        try:
            data_mes = datetime.strptime(
                mes,
                '%Y-%m'
            )
        except ValueError:
            return HttpResponse(
                'Mês inválido.',
                status=400
            )

        ano = data_mes.year # Pega apenas o ano da data
        numero_mes = data_mes.month # Pega apenas o mês da data

        # Define o dia da data inicial como 1 do mês-ano escolhido
        data_inicio = data_mes.date().replace(
            day=1
        )

        # Função retorno o último dia daquele mês-ano
        ultimo_dia = monthrange(
            ano,
            numero_mes
        )[1]

        # Define o dia da data final como o último dia do mês-ano escolhido
        data_fim = data_mes.date().replace(
            day=ultimo_dia
        )

        # String range do período que será usada no .pdf
        periodo = (
            f'{data_inicio.strftime("%d/%m/%Y")} – '
            f'{data_fim.strftime("%d/%m/%Y")}'
        )

    # Caso seja outro tipo de relatório fora dia único ou mês
    else:

        return HttpResponse(
            'Tipo de relatório inválido.',
            status=400
        )

    # Busca no banco todos os registros entre as datas X e Y, ordenando-os por data
    fechamentos = Vendas.objects.filter(
        data__gte=data_inicio, # gte - maior ou igual a data início
        data__lte=data_fim # lte - menor ou igual a data fim
    ).order_by('data')

    # Se não existirem registros
    if not fechamentos.exists():
        return render(
            request,
            'relatorios.html',
            {
                'erro': (
                    'Não existem fechamentos registrados '
                    'para o período selecionado.'
                )
            }
        )

    # Soma os valores dos registros retornados - Cálcula o fechamento total
    valor_movimentado = (
        fechamentos.aggregate(
            total=Sum('valor_total')
        )['total'] # Retorna um dicionário contendo a relação de somas
        or 0 # Caso a soma seja None, retorna 0
    )

    # Soma os valores agrupando por tipo de pagamento
    valores_por_pagamento = (
        fechamentos
        .values('tipo_pagamento')
        .annotate(
            total=Sum('valor_total')
        )
        .order_by('tipo_pagamento')
    )

    valores_pagamento = {}

    # Armazena as somas por tipo em um dicionário
    for item in valores_por_pagamento:

        valores_pagamento[
            item['tipo_pagamento']
        ] = item['total'] or 0

    # Indica ao navegador que se trata de uma resposta HTTP em .pdf
    response = HttpResponse(
        content_type='application/pdf'
    )

    # Indica que a disposição do conteúdo será "abertura na mesma janela" (inline)
    response['Content-Disposition'] = (
        'inline; '
        'filename="relatorio_vendas.pdf"'
    )

    # Criação do arquivo .pdf - indica instruções para a base da formatação
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    # Resgata estilos prontos fornecidos pela biblioteca
    styles = getSampleStyleSheet()

    # Define estilos personalizados para certos atributos /
    estilo_titulo = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#123524'),
        spaceAfter=4,
    )

    estilo_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#555555'),
        spaceAfter=15,
    )

    estilo_secao = ParagraphStyle(
        'Secao',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor('#123524'),
        spaceBefore=8,
        spaceAfter=8,
    )

    estilo_texto = ParagraphStyle(
        'Texto',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#333333'),
    )

    estilo_valor = ParagraphStyle(
        'Valor',
        parent=estilo_texto,
        alignment=TA_RIGHT,
    )
    # /

    # Corpo do .pdf
    elementos = []

    # Adiciona o título ao corpo (parágrafo)
    elementos.append(
        Paragraph(
            'CASHLY', # O texto que será escrito
            estilo_titulo # O estilo aplicado
        )
    )

    elementos.append(
        Paragraph(
            'Sistema de Controle de Vendas',
            estilo_subtitulo
        )
    )

    elementos.append(
        Paragraph(
            'RELATÓRIO DE VENDAS',
            estilo_secao
        )
    )

    elementos.append(
        Paragraph(
            f'Período: {periodo}',
            estilo_texto
        )
    )

    elementos.append(
        Spacer(1, 8 * mm)
    )

    elementos.append(
        Paragraph(
            'RESUMO',
            estilo_secao
        )
    )

    # Tabela resumo do valor total em reais do respectivo período
    resumo = [
        [
            Paragraph(
                '<b>Valor movimentado:</b>',
                estilo_texto
            ),
            Paragraph(
                f'<b>{formatar_moeda(valor_movimentado)}</b>',
                estilo_valor
            ),
        ]
    ]

    # Define a coluna da tabela resumo
    tabela_resumo = Table(
        resumo,
        colWidths=[
            100 * mm,
            65 * mm
        ]
    )

    # Define o estilo da tabela resumo
    tabela_resumo.setStyle(
        TableStyle([
            (
                'BACKGROUND',
                (0, 0),
                (-1, -1),
                colors.HexColor('#E8F5EC')
            ),
            (
                'BOX',
                (0, 0),
                (-1, -1),
                0.7,
                colors.HexColor('#176B3A')
            ), # BOX - borda
            (
                'LEFTPADDING',
                (0, 0),
                (-1, -1),
                8
            ),
            (
                'RIGHTPADDING',
                (0, 0),
                (-1, -1),
                8
            ),
            (
                'TOPPADDING',
                (0, 0),
                (-1, -1),
                8
            ),
            (
                'BOTTOMPADDING',
                (0, 0),
                (-1, -1),
                8
            ),
        ])
    )

    # Adiciona a tabela ao corpo
    elementos.append(
        tabela_resumo
    )

    elementos.append(
        Spacer(1, 8 * mm)
    )

    elementos.append(
        Paragraph(
            'POR TIPO DE PAGAMENTO',
            estilo_secao
        )
    )

    # Relação do model para os tipos de pagamento
    tipos_pagamento = [
        ('DINHEIRO', 'Dinheiro'),
        ('PIX', 'Pix'),
        ('DEBITO', 'Débito'),
        ('CREDITO', 'Crédito'),
    ]

    dados_pagamento = []

    # Percorre os valores armazenados anteriormente - da soma por tipo de pagamento
    for item in valores_por_pagamento:

        codigo = item['tipo_pagamento']
        valor = item['total'] or 0

        # Resgata o nome amigável definido no model de vendas
        nome = dict(
            Vendas.TIPO_PAGAMENTO
        ).get(
            codigo,
            codigo
        )

        # Armazena os valores na lista para formatação da tabela
        dados_pagamento.append([
            Paragraph(
                nome,
                estilo_texto
            ),
            Paragraph(
                formatar_moeda(valor),
                estilo_valor
            )
        ])

    # Define quais dados usados e formatação das colunas
    tabela_pagamento = Table(
        dados_pagamento,
        colWidths=[
            100 * mm,
            65 * mm
        ]
    )

    tabela_pagamento.setStyle(
        TableStyle([
            (
                'GRID',
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor('#CCCCCC')
            ),
            (
                'ROWBACKGROUNDS',
                (0, 0),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor('#F5F5F5')
                ]
            ),
            (
                'LEFTPADDING',
                (0, 0),
                (-1, -1),
                8
            ),
            (
                'RIGHTPADDING',
                (0, 0),
                (-1, -1),
                8
            ),
            (
                'TOPPADDING',
                (0, 0),
                (-1, -1),
                6
            ),
            (
                'BOTTOMPADDING',
                (0, 0),
                (-1, -1),
                6
            ),
        ])
    )

    # Adiciona ao corpo
    elementos.append(
        tabela_pagamento
    )

    elementos.append(
        Spacer(1, 8 * mm)
    )

    elementos.append(
        Paragraph(
            'FECHAMENTOS',
            estilo_secao
        )
    )

    # Define o cabeçalho da tabela que mostra todos os fechamentos do período
    dados_fechamentos = [
        [
            Paragraph('<b>Data</b>', estilo_texto),
            Paragraph('<b>Pagamento</b>', estilo_texto),
            Paragraph('<b>Caixa</b>', estilo_texto),
            Paragraph('<b>Responsável</b>', estilo_texto),
            Paragraph('<b>Valor</b>', estilo_valor),
        ]
    ]

    # Adiciona os registros de fechamento à tabela
    for fechamento in fechamentos:

        dados_fechamentos.append([
            Paragraph(
                fechamento.data.strftime(
                    '%d/%m/%Y'
                ),
                estilo_texto
            ),
            Paragraph(
                fechamento.get_tipo_pagamento_display(), # Resgata nome amigável
                estilo_texto
            ),
            Paragraph(
                str(fechamento.num_caixa),
                estilo_texto
            ),
            Paragraph(
                fechamento.responsavel,
                estilo_texto
            ),
            Paragraph(
                formatar_moeda(
                    fechamento.valor_total
                ),
                estilo_valor
            ),
        ])

    # Define a tabela no documento e formata suas colunas
    tabela_fechamentos = Table(
        dados_fechamentos,
        colWidths=[
            28 * mm,
            35 * mm,
            20 * mm,
            45 * mm,
            30 * mm,
        ],
        repeatRows=1, # Repete o cabeçalho caso a tabela seja grande e passe de uma página
    )

    tabela_fechamentos.setStyle(
        TableStyle([
            (
                'BACKGROUND',
                (0, 0),
                (-1, 0),
                colors.HexColor('#176B3A')
            ),
            (
                'TEXTCOLOR',
                (0, 0),
                (-1, 0),
                colors.white
            ),
            (
                'GRID',
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor('#CCCCCC')
            ),
            (
                'ROWBACKGROUNDS',
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor('#F5F5F5')
                ]
            ),
            (
                'VALIGN',
                (0, 0),
                (-1, -1),
                'MIDDLE'
            ),
            (
                'LEFTPADDING',
                (0, 0),
                (-1, -1),
                5
            ),
            (
                'RIGHTPADDING',
                (0, 0),
                (-1, -1),
                5
            ),
            (
                'TOPPADDING',
                (0, 0),
                (-1, -1),
                6
            ),
            (
                'BOTTOMPADDING',
                (0, 0),
                (-1, -1),
                6
            ),
        ])
    )

     # Adiciona ao corpo
    elementos.append(
        tabela_fechamentos
    )

    elementos.append(
        Spacer(1, 10 * mm)
    )

    # Define a data e hora da geração do relatório
    data_geracao = datetime.now().strftime(
        '%d/%m/%Y às %H:%M'
    )

    # Adiciona ao corpo
    elementos.append(
        Paragraph(
            f'Gerado em: {data_geracao}',
            estilo_subtitulo
        )
    )

    # Constrói o arquivo .pdf
    doc.build(elementos)

    # Devolve ao navegador como resposta HTTP
    return response