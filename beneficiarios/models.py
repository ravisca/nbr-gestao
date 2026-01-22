from django.db import models
from django.contrib import admin  # <--- IMPORTANTE: Adicionei esta linha
from datetime import date

class Turno(models.Model):
    nome = models.CharField(max_length=50, unique=True, verbose_name="Nome do Turno")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"

class Beneficiario(models.Model):
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo'),
        ('PENDENTE', 'Pendente'),
        ('DESLIGADO', 'Desligado'),
    ]

    # Dados Pessoais
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    data_nascimento = models.DateField(verbose_name="Data de Nascimento")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    telefone = models.CharField(max_length=20, verbose_name="Telefone para Contato")

    # Saúde e Acessibilidade
    tem_problema_saude = models.BooleanField(default=False, verbose_name="Possui Quadro de Saúde?")
    descricao_saude = models.CharField(max_length=255, blank=True, null=True, verbose_name="Qual o quadro de saúde?")
    necessita_acessibilidade = models.BooleanField(default=False, verbose_name="Necessita de Acessibilidade?")
    descricao_acessibilidade = models.CharField(max_length=255, blank=True, null=True, verbose_name="Qual acessibilidade?")

    # Dados do Projeto/ONG
    projeto = models.ForeignKey('atividades.Projeto', on_delete=models.PROTECT, verbose_name="Projeto")
    atividade = models.ForeignKey('atividades.TipoAtividade', on_delete=models.PROTECT, verbose_name="Atividade / Qtd. Atividades")
    turno = models.ForeignKey(Turno, on_delete=models.PROTECT, verbose_name="Turno")
    
    # Responsável
    responsavel = models.CharField(max_length=200, blank=True, null=True, verbose_name="Responsável")
    grau_parentesco = models.CharField(max_length=50, blank=True, null=True, verbose_name="Grau de Parentesco")

    # Controle Interno
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVO', verbose_name="Status")

    def __str__(self):
        return self.nome_completo

    # --- Campos Calculados ---

    @property
    def idade(self):
        """Calcula a idade (Anos) baseado na data de nascimento"""
        today = date.today()
        if self.data_nascimento:
            return today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return 0

    @property
    @admin.display(description="18+", boolean=True) # <--- CORREÇÃO AQUI
    def eh_maior_idade(self):
        """Retorna True se for 18+, usado para a coluna 18+"""
        return self.idade >= 18
    
    # REMOVI AS LINHAS QUE DAVAM ERRO AQUI EMBAIXO