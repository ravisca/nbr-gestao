from django.db import models


class ConfiguracaoSite(models.Model):
    """Configuração global do sistema (singleton — apenas 1 registro permitido)."""
    nome_sistema = models.CharField(max_length=100, default='SIGEP', verbose_name="Nome do Sistema")
    logo_site = models.ImageField(upload_to='config/', blank=True, null=True, verbose_name="Logo do Site (Sidebar)",
                                  help_text="Imagem para o painel web. Recomendado: PNG com fundo transparente.")
    logo_relatorio = models.ImageField(upload_to='config/', blank=True, null=True, verbose_name="Logo para Relatórios (PDF)",
                                       help_text="Imagem para o cabeçalho dos PDFs. Recomendado: PNG de alta qualidade.")
    favicon = models.ImageField(upload_to='config/', blank=True, null=True, verbose_name="Favicon (Ícone do Navegador)",
                                help_text="Ícone exibido na aba do navegador. Recomendado: PNG quadrado 32x32 ou 64x64.")

    class Meta:
        verbose_name = "Configuração do Site"
        verbose_name_plural = "Configuração do Site"

    def __str__(self):
        return self.nome_sistema

    def save(self, *args, **kwargs):
        # Garante singleton: só permite pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Retorna a instância singleton ou cria uma padrão."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
