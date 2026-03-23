from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nome
    class Meta: verbose_name_plural = "Categorias"

class UnidadeMedida(models.Model):
    sigla = models.CharField(max_length=10, unique=True, verbose_name="Sigla")
    nome = models.CharField(max_length=50, verbose_name="Nome Completo")

    def __str__(self):
        return f"{self.nome} ({self.sigla})"
    
    class Meta:
        verbose_name = "Unidade de Medida"
        verbose_name_plural = "Unidades de Medida"

class Item(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    nome = models.CharField(max_length=200, verbose_name="Nome do Item")
    unidade = models.ForeignKey(UnidadeMedida, on_delete=models.PROTECT, verbose_name="Unidade")
    quantidade_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Saldo em Estoque")
    estoque_minimo = models.DecimalField(max_digits=10, decimal_places=2, default=5, verbose_name="Estoque Mínimo")

    def __str__(self): return f"{self.nome} ({self.quantidade_atual} {self.unidade})"
    class Meta: verbose_name_plural = "Itens em Estoque"; ordering = ['nome']

class Movimentacao(models.Model):
    TIPO_CHOICES = [('ENTRADA', 'Entrada (Doação/Compra)'), ('SAIDA', 'Saída (Uso/Consumo)')]
    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='movimentacoes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Responsável")
    origem_destino = models.CharField(max_length=200, blank=True, null=True, verbose_name="Origem / Destino")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observações")
    grupo_lote = models.CharField(max_length=50, blank=True, null=True, db_index=True, verbose_name="Código do Lote")

    def __str__(self): return f"{self.get_tipo_display()} - {self.item.nome}"
    class Meta: verbose_name = "Movimentação"; verbose_name_plural = "Movimentações"; ordering = ['-data', '-id']

    def clean(self):
        if self.tipo == 'SAIDA' and not self.pk:
            if self.item.quantidade_atual < self.quantidade:
                raise ValidationError(f"Estoque insuficiente! Saldo atual: {self.item.quantidade_atual}.")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            if self.tipo == 'ENTRADA': self.item.quantidade_atual += self.quantidade
            else: self.item.quantidade_atual -= self.quantidade
            self.item.save()


class Emprestimo(models.Model):
    TIPO_CHOICES = [
        ('EXTERNO', 'Externo'),
        ('INTERNO', 'Interno / Operação'),
    ]

    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="Item Emprestado")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='EXTERNO', verbose_name="Tipo")

    # Dados do Solicitante (Externo)
    nome_solicitante = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf_solicitante = models.CharField(max_length=14, verbose_name="CPF/Documento", blank=True, null=True)
    contato = models.CharField(max_length=100, verbose_name="Telefone/WhatsApp")
    email_solicitante = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    endereco = models.CharField(max_length=255, verbose_name="Endereço", blank=True, null=True)
    responsavel_casa = models.CharField(max_length=200, blank=True, null=True, verbose_name="Responsável da Casa (quem entregou)")

    # Dados Internos (Projeto/Operação)
    projeto = models.ForeignKey('atividades.Projeto', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Projeto")
    nucleo = models.ForeignKey('atividades.Nucleo', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Núcleo")
    logistica = models.TextField(blank=True, null=True, verbose_name="Detalhes de Logística")

    # Controle de Quantidade
    quantidade_emprestada = models.PositiveIntegerField(default=1, verbose_name="Qtd. Levada")

    # Datas
    data_saida = models.DateField(default=timezone.now, verbose_name="Data de Saída (Prevista)")
    data_saida_real = models.DateField(blank=True, null=True, verbose_name="Data de Saída (Real)")
    data_prevista = models.DateField(verbose_name="Previsão de Devolução")

    # Devolução
    data_devolucao = models.DateField(blank=True, null=True, verbose_name="Data da Devolução Real")
    quantidade_devolvida = models.PositiveIntegerField(blank=True, null=True, verbose_name="Qtd. Devolvida")
    motivo_falta = models.TextField(blank=True, null=True, verbose_name="Motivo da Diferença (Perda/Quebra)")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações Gerais")
    grupo_lote = models.CharField(max_length=50, blank=True, null=True, db_index=True, verbose_name="Código do Lote")

    devolvido = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return f"{self.quantidade_emprestada}x {self.item.nome} - {self.nome_solicitante}"

    class Meta:
        verbose_name = "Empréstimo"
        verbose_name_plural = "Controle de Empréstimos"
        ordering = ['-data_saida', '-id']

    @property
    def status_display(self):
        if self.devolvido:
            return 'Devolvido'
        if self.data_prevista and self.data_prevista < timezone.now().date():
            return 'Atrasado'
        return 'Pendente'

    def clean(self):
        if not self.pk and not self.devolvido:
            if hasattr(self, 'item') and self.item:
                if self.item.quantidade_atual < self.quantidade_emprestada:
                    raise ValidationError(f"Estoque insuficiente! Você quer {self.quantidade_emprestada}, mas só tem {self.item.quantidade_atual}.")

        if self.quantidade_devolvida is not None:
            if self.quantidade_devolvida > self.quantidade_emprestada:
                raise ValidationError({'quantidade_devolvida': "Você não pode devolver mais do que emprestou!"})
            if self.quantidade_devolvida < self.quantidade_emprestada and not self.motivo_falta:
                raise ValidationError({'motivo_falta': "Como a quantidade devolvida é menor que a emprestada, descreva o motivo da falta."})

    def save(self, *args, **kwargs):
        from django.db import transaction

        is_new = self.pk is None

        with transaction.atomic():
            super().save(*args, **kwargs)

            if is_new:
                self.item.quantidade_atual -= self.quantidade_emprestada
                self.item.save()
            elif self.data_devolucao and self.quantidade_devolvida is not None and not self.devolvido:
                self.item.quantidade_atual += self.quantidade_devolvida
                self.item.save()
                self.devolvido = True
                super().save(update_fields=['devolvido'])