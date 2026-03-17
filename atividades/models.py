from django.db import models
from django.contrib.auth.models import User


class Projeto(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome do Projeto")
    descricao = models.TextField(verbose_name="Descrição", blank=True, null=True)
    cor = models.CharField(max_length=7, default="#FFFFFF", verbose_name="Cor de Identificação", help_text="Cor em Hexadecimal (ex: #FF0000)")
    valor_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Valor Inicial do Projeto")
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

# Núcleo: agrupador intermediário dentro de um projeto
class Nucleo(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name="nucleos")
    nome = models.CharField(max_length=100, verbose_name="Nome do Núcleo (Ex: Núcleo Centro)")

    def __str__(self):
        return f"{self.projeto.nome} | {self.nome}"

    class Meta:
        verbose_name = "Núcleo"
        verbose_name_plural = "Núcleos"
        ordering = ['nome']

# Define o que pode ser feito nesse projeto
class TipoAtividade(models.Model):
    projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE, related_name="tipos_atividade")
    nucleo = models.ForeignKey(Nucleo, on_delete=models.SET_NULL, null=True, blank=True, related_name="atividades", verbose_name="Núcleo")
    nome = models.CharField(max_length=100, verbose_name="Nome da Atividade (Ex: Treino, Aula)")
    turnos = models.ManyToManyField('beneficiarios.Turno', verbose_name="Turnos Disponíveis", blank=True)
    
    def __str__(self):
        return f"{self.projeto.nome} | {self.nome}"

class RegistroAtividade(models.Model):
    # Seleção Hierárquica
    projeto = models.ForeignKey(Projeto, on_delete=models.PROTECT, verbose_name="Projeto")
    
    # Agora selecionamos de uma lista, não digitamos mais
    tipo_atividade = models.ForeignKey(TipoAtividade, on_delete=models.PROTECT, verbose_name="Atividade Realizada")
    
    monitor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Monitor", blank=True, null=True)
    data = models.DateField(verbose_name="Data da Atividade")
    descricao = models.TextField(verbose_name="Descrição Detalhada do Dia")

    # --- MÍDIA (4 fotos obrigatórias) ---
    foto_1 = models.ImageField(upload_to='atividades/fotos/%Y/%m/', verbose_name="Foto 1")
    foto_2 = models.ImageField(upload_to='atividades/fotos/%Y/%m/', verbose_name="Foto 2")
    foto_3 = models.ImageField(upload_to='atividades/fotos/%Y/%m/', verbose_name="Foto 3")
    foto_4 = models.ImageField(upload_to='atividades/fotos/%Y/%m/', verbose_name="Foto 4")

    # --- OBSERVAÇÕES ---
    observacoes = models.TextField(verbose_name="Observações", blank=True)

    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.data} - {self.tipo_atividade}"

    class Meta:
        verbose_name = "Diário de Atividade"
        verbose_name_plural = "Diários de Atividades"