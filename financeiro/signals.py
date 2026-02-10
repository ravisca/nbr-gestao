from django.db.models.signals import post_save
from django.dispatch import receiver
from atividades.models import Projeto
from .models import Conta

@receiver(post_save, sender=Projeto)
def create_conta_por_projeto(sender, instance, created, **kwargs):
    """
    Sempre que um Projeto é criado, cria automaticamente uma Conta
    financeira vinculada a ele.
    """
    if created:
        # Verifica se já não existe conta (por segurança)
        if not hasattr(instance, 'conta'):
            Conta.objects.create(
                projeto=instance,
                nome=f"CONTA PROJETO - {instance.nome}",
                saldo_inicial=0,
                saldo_atual=0
            )
