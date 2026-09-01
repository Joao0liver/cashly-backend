from django.db import models
from django.utils import timezone

class Vendas(models.Model):

    # Recebe por padrão a data atual
    data = models.DateField(default=timezone.localdate)

    # Cria uma lista com os tipos de pagamento para usar em choices
    TIPO_PAGAMENTO = [
        ('DINHEIRO', 'Dinheiro'),
        ('PIX', 'Pix'),
        ('DEBITO', 'Débito'),
        ('CREDITO', 'Crédito'),
    ]

    tipo_pagamento = models.CharField(max_length=10, choices=TIPO_PAGAMENTO)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)

    # Cria uma lista com as bandeiras dos cartões para usar em choices
    BANDEIRA_CARTAO = [
        ('VISA', 'Visa'),
        ('MASTERCARD', 'Mastercard'),
        ('ELO', 'Elo'),
    ]

    bandeira_cartao = models.CharField(max_length=30, choices=BANDEIRA_CARTAO, blank=True) # Opcional (pois nem sempre o tipo é cartão)
    responsavel = models.CharField(max_length=100)
    num_caixa =  models.CharField(max_length=20, blank=True) # Opcional (pois há lugares que possuem somente um caixa)
    obs = models.TextField(blank=True) # Opcional
    conferido = models.BooleanField(default=False) # Não vem conferido por padrão

    def __str__(self):
        pagamento = self.get_tipo_pagamento_display() # Display pega o valor "amigável" da lista
        return f"{self.data.strftime('%d/%m/%Y')} - R$ {self.valor_total:.2f} - {pagamento} - {self.responsavel}"