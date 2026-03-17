from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from atividades.models import Projeto
from .models import Conta

@receiver(pre_save, sender=Projeto)
def pre_save_projeto_valor(sender, instance, **kwargs):
    """
    Antes de salvar o projeto, guarda o valor inicial antigo para
    poder calcular a diferença de reajuste financeiro depois do save.
    """
    if instance.pk:
        try:
            old_instance = Projeto.objects.get(pk=instance.pk)
            instance._old_valor_inicial = old_instance.valor_inicial
        except Projeto.DoesNotExist:
            instance._old_valor_inicial = 0
    else:
        instance._old_valor_inicial = 0

@receiver(post_save, sender=Projeto)
def create_conta_por_projeto(sender, instance, created, **kwargs):
    """
    Cria a conta automática ao criar um Projeto.
    Sincroniza a diferença do valor_inicial nas edições.
    """
    if created:
        if not hasattr(instance, 'conta'):
            Conta.objects.create(
                projeto=instance,
                nome=f"CONTA PROJETO - {instance.nome}",
                saldo_inicial=instance.valor_inicial,
                saldo_atual=instance.valor_inicial
            )
    else:
        if hasattr(instance, 'conta'):
            conta = instance.conta
            old_valor = getattr(instance, '_old_valor_inicial', 0)
            novo_valor = instance.valor_inicial
            
            diferenca = novo_valor - old_valor
            if diferenca != 0:
                # O saldo inicial formal da conta sobe ou desce
                conta.saldo_inicial += diferenca
                # O saldo atual, que flutua com as despesas, sobe ou desce na mesma exata quantia
                conta.saldo_atual += diferenca
                conta.save()
