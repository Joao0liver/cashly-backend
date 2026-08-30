from django.db import models

class Vendas(models.Model):

    data = models.DateField()

    TIPO_PAGAMENTO = [
        ('DINHEIRO', 'Dinheiro'),
        ('PIX', 'Pix'),
        ('DEBITO', 'Débito'),
        ('CREDITO', 'Crédito'),
    ]

    tipo_pagamento = models.CharField(max_length=10, choices=TIPO_PAGAMENTO)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)

    BANDEIRA_CARTAO = [
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('ELO', 'Elo'),
    ]

    bandeira_cartao = models.CharField(max_length=30, choices=BANDEIRA_CARTAO, blank=True)
    responsavel = models.CharField(max_length=100)
    num_caixa =  models.CharField(max_length=20)
    obs = models.TextField(blank=True)
    conferido = models.BooleanField(default=False)

    def __str__(self):
        pagamento = self.get_tipo_pagamento_display()
        return f"{self.data.strftime('%d/%m/%Y')} - R$ {self.valor_total:.2f} - {pagamento} - {self.responsavel}"