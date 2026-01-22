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

# --- MODELO ATUALIZADO (SEM VÍNCULO COM BENEFICIÁRIO) ---
class Emprestimo(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name="Item Emprestado")
    
    # Dados do Solicitante
    nome_solicitante = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf_solicitante = models.CharField(max_length=14, verbose_name="CPF/Documento", blank=True, null=True)
    contato = models.CharField(max_length=100, verbose_name="Telefone/WhatsApp")
    endereco = models.CharField(max_length=255, verbose_name="Endereço", blank=True, null=True)

    # Controle de Quantidade (NOVO)
    quantidade_emprestada = models.PositiveIntegerField(default=1, verbose_name="Qtd. Levada")
    
    # Datas
    data_saida = models.DateField(default=timezone.now, verbose_name="Data de Retirada")
    data_prevista = models.DateField(verbose_name="Previsão de Devolução")
    
    # Devolução
    data_devolucao = models.DateField(blank=True, null=True, verbose_name="Data da Devolução Real")
    quantidade_devolvida = models.PositiveIntegerField(blank=True, null=True, verbose_name="Qtd. Devolvida")
    
    # Motivo aparece se Qtd Devolvida < Qtd Emprestada
    motivo_falta = models.TextField(blank=True, null=True, verbose_name="Motivo da Diferença (Perda/Quebra)")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações Gerais")
    
    devolvido = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return f"{self.quantidade_emprestada}x {self.item.nome} - {self.nome_solicitante}"

    class Meta:
        verbose_name = "Empréstimo Avulso"
        verbose_name_plural = "Controle de Empréstimos"

    def clean(self):
        # 1. Validação na Saída (Criação)
        if not self.pk and not self.devolvido:
            if self.item.quantidade_atual < self.quantidade_emprestada:
                raise ValidationError(f"Estoque insuficiente! Você quer {self.quantidade_emprestada}, mas só tem {self.item.quantidade_atual}.")

        # 2. Validação na Devolução
        if self.quantidade_devolvida is not None:
            # Não pode devolver mais do que levou
            if self.quantidade_devolvida > self.quantidade_emprestada:
                 raise ValidationError({'quantidade_devolvida': "Você não pode devolver mais do que emprestou!"})
            
            # Se devolver MENOS, o motivo é obrigatório
            if self.quantidade_devolvida < self.quantidade_emprestada and not self.motivo_falta:
                raise ValidationError({'motivo_falta': "Como a quantidade devolvida é menor que a emprestada, descreva o motivo da falta."})

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        
        if is_new:
            # SAÍDA: Subtrai a quantidade que está levando
            self.item.quantidade_atual -= self.quantidade_emprestada
            self.item.save()
        
        else:
            # RETORNO: Se preencheu a data E a quantidade devolvida, e ainda não processou
            if self.data_devolucao and self.quantidade_devolvida is not None and not self.devolvido:
                # O Estoque recebe de volta APENAS o que foi devolvido fisicamente
                # O restante é considerado perda/consumo
                self.item.quantidade_atual += self.quantidade_devolvida
                self.item.save()
                self.devolvido = True
                
        super().save(*args, **kwargs)