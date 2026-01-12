from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Conta(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome da Conta (Ex: Banco Brasil, Caixa)")
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    saldo_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    
    def __str__(self):
        return f"{self.nome} - R$ {self.saldo_atual}"

# --- TABELA 1: ENTRADAS (Simples) ---
class CategoriaReceita(models.Model):
    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome da Categoria")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Categoria de Receita"
        verbose_name_plural = "Categorias de Receita"

class Rubrica(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Rúbrica")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Rúbrica"
        verbose_name_plural = "Rúbricas"

# --- TABELA 1: ENTRADAS (Simples) ---
class Receita(models.Model):
    conta = models.ForeignKey(Conta, on_delete=models.PROTECT, verbose_name="Conta de Entrada")
    categoria = models.ForeignKey(CategoriaReceita, on_delete=models.PROTECT, verbose_name="Categoria")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor (R$)")
    data = models.DateField(default=timezone.now, verbose_name="Data do Recebimento")
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    
    responsavel = models.ForeignKey(User, on_delete=models.PROTECT, editable=False)
    data_lancamento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ENTRADA: R$ {self.valor} - {self.descricao}"

    class Meta:
        verbose_name = "Receita (Entrada)"
        verbose_name_plural = "Receitas"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.conta.saldo_atual += self.valor
            self.conta.save()
        super().save(*args, **kwargs)

# --- TABELA 2: SAÍDAS (Detalhada - Prestação de Contas) ---
class Despesa(models.Model):
    MES_CHOICES = [
        ('01', 'Janeiro'), ('02', 'Fevereiro'), ('03', 'Março'), ('04', 'Abril'),
        ('05', 'Maio'), ('06', 'Junho'), ('07', 'Julho'), ('08', 'Agosto'),
        ('09', 'Setembro'), ('10', 'Outubro'), ('11', 'Novembro'), ('12', 'Dezembro'),
    ]

    # Vínculos
    conta = models.ForeignKey(Conta, on_delete=models.PROTECT, verbose_name="Saiu de qual conta?")
    projeto = models.ForeignKey('atividades.Projeto', on_delete=models.PROTECT, verbose_name="Projeto Relacionado")
    
    # Dados Fiscais Obrigatórios
    razao_social = models.CharField(max_length=200, verbose_name="Razão Social (Fornecedor)")
    cnpj = models.CharField(max_length=20, verbose_name="CNPJ")
    nota_fiscal = models.CharField(max_length=50, verbose_name="Doc. Fiscal / Nº Nota")
    serie = models.CharField(max_length=10, verbose_name="Série", blank=True, null=True)
    data_emissao = models.DateField(verbose_name="Dt. Emissão")
    
    # Classificação
    rubrica = models.ForeignKey(Rubrica, on_delete=models.PROTECT, verbose_name="Rúbrica (Ex: Material Consumo, RH)")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor (R$)")
    
    # Competência
    mes_referencia = models.CharField(max_length=2, choices=MES_CHOICES, verbose_name="Mês Ref.")
    ano_referencia = models.IntegerField(default=timezone.now().year, verbose_name="Ano Ref.")
    
    # Detalhes
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    comprovante = models.FileField(upload_to='financeiro/notas/%Y/', verbose_name="NOTA (Arquivo)")
    
    responsavel = models.ForeignKey(User, on_delete=models.PROTECT, editable=False)
    data_lancamento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SAÍDA: R$ {self.valor} - {self.razao_social}"

    class Meta:
        verbose_name = "Despesa (Prestação de Contas)"
        verbose_name_plural = "Despesas"

    def clean(self):
        # Validação: Não pode gastar o que não tem
        if not self.pk:
            if self.conta.saldo_atual < self.valor:
                raise ValidationError(f"Saldo Insuficiente na conta '{self.conta.nome}'! Disponível: R$ {self.conta.saldo_atual}")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.conta.saldo_atual -= self.valor
            self.conta.save()
        super().save(*args, **kwargs)