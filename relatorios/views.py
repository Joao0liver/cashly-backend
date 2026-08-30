from datetime import datetime
from calendar import monthrange

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,)

from vendas.models import Vendas

def relatorios(request):
    return render(request, 'relatorios.html')

def formatar_moeda(valor):
    return (
        f'R$ {valor:,.2f}'
        .replace(',', 'X')
        .replace('.', ',')
        .replace('X', '.')
    )

def relatorio_vendas_pdf(request):

    tipo = request.GET.get('tipo')

    data_inicio = None
    data_fim = None
    periodo = ''

    if tipo == 'dia':

        data = request.GET.get('data')

        if not data:
            return HttpResponse(
                'Nenhuma data foi informada.',
                status=400
            )

        try:
            data_inicio = datetime.strptime(
                data,
                '%Y-%m-%d'
            ).date()

        except ValueError:
            return HttpResponse(
                'Data inválida.',
                status=400
            )

        data_fim = data_inicio

        periodo = data_inicio.strftime('%d/%m/%Y')

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

        ano = data_mes.year
        numero_mes = data_mes.month

        data_inicio = data_mes.date().replace(
            day=1
        )

        ultimo_dia = monthrange(
            ano,
            numero_mes
        )[1]

        data_fim = data_mes.date().replace(
            day=ultimo_dia
        )

        periodo = (
            f'{data_inicio.strftime("%d/%m/%Y")} – '
            f'{data_fim.strftime("%d/%m/%Y")}'
        )

    else:

        return HttpResponse(
            'Tipo de relatório inválido.',
            status=400
        )

    fechamentos = Vendas.objects.filter(
        data__gte=data_inicio,
        data__lte=data_fim
    ).order_by('data')

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

    valor_movimentado = (
        fechamentos.aggregate(
            total=Sum('valor_total')
        )['total']
        or 0
    )

    valores_por_pagamento = (
        fechamentos
        .values('tipo_pagamento')
        .annotate(
            total=Sum('valor_total')
        )
        .order_by('tipo_pagamento')
    )

    valores_pagamento = {}

    for item in valores_por_pagamento:

        valores_pagamento[
            item['tipo_pagamento']
        ] = item['total'] or 0

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        'inline; '
        'filename="relatorio_vendas.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

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

    elementos = []

    elementos.append(
        Paragraph(
            'CASHLY',
            estilo_titulo
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

    tabela_resumo = Table(
        resumo,
        colWidths=[
            100 * mm,
            65 * mm
        ]
    )

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

    tipos_pagamento = [
        ('DINHEIRO', 'Dinheiro'),
        ('PIX', 'Pix'),
        ('DEBITO', 'Débito'),
        ('CREDITO', 'Crédito'),
    ]

    dados_pagamento = []

    for item in valores_por_pagamento:

        codigo = item['tipo_pagamento']
        valor = item['total'] or 0

        nome = dict(
            Vendas.TIPO_PAGAMENTO
        ).get(
            codigo,
            codigo
        )

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

    dados_fechamentos = [
        [
            Paragraph('<b>Data</b>', estilo_texto),
            Paragraph('<b>Pagamento</b>', estilo_texto),
            Paragraph('<b>Caixa</b>', estilo_texto),
            Paragraph('<b>Responsável</b>', estilo_texto),
            Paragraph('<b>Valor</b>', estilo_valor),
        ]
    ]

    for fechamento in fechamentos:

        dados_fechamentos.append([
            Paragraph(
                fechamento.data.strftime(
                    '%d/%m/%Y'
                ),
                estilo_texto
            ),
            Paragraph(
                fechamento.get_tipo_pagamento_display(),
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

    if not fechamentos.exists():

        dados_fechamentos.append([
            Paragraph(
                'Não foram encontrados fechamentos '
                'para o período selecionado.',
                estilo_texto
            ),
            '',
            '',
            '',
            '',
        ])

    tabela_fechamentos = Table(
        dados_fechamentos,
        colWidths=[
            28 * mm,
            35 * mm,
            20 * mm,
            45 * mm,
            30 * mm,
        ],
        repeatRows=1,
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

    elementos.append(
        tabela_fechamentos
    )

    elementos.append(
        Spacer(1, 10 * mm)
    )

    data_geracao = datetime.now().strftime(
        '%d/%m/%Y às %H:%M'
    )

    elementos.append(
        Paragraph(
            f'Gerado em: {data_geracao}',
            estilo_subtitulo
        )
    )

    doc.build(elementos)

    return response