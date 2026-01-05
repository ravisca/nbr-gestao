from django.db import models

class Beneficiario(models.Model):
    # Opções para campos de seleção
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]

    ESTADO_CIVIL_CHOICES = [
        ('SOL', 'Solteiro(a)'),
        ('CAS', 'Casado(a)'),
        ('DIV', 'Divorciado(a)'),
        ('VIU', 'Viúvo(a)'),
    ]

    # Dados Pessoais Básicos
    nome_completo = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    data_nascimento = models.DateField()
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    nome_mae = models.CharField(max_length=200, verbose_name="Nome da Mãe")

    # Contato e Endereço
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.TextField(verbose_name="Endereço Completo")
    referencia = models.CharField(max_length=200, blank=True, null=True)

    # Dados Sociais
    nis = models.CharField(max_length=20, blank=True, null=True, verbose_name="NIS/PIS")
    renda_familiar = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    qtd_membros_familia = models.IntegerField(verbose_name="Qtd. Pessoas na Casa", default=1) 
    observacoes = models.TextField(blank=True, null=True)

    # Auditoria (Saber quando foi criado)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome_completo} ({self.cpf})"