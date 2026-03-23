from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Item, Categoria, UnidadeMedida, Movimentacao, Emprestimo


class EstoqueBaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password', first_name='Test', last_name='User')
        self.client = Client()
        self.client.login(username='testuser', password='password')

        self.categoria = Categoria.objects.create(nome="Geral")
        self.unidade = UnidadeMedida.objects.create(sigla="UN", nome="Unidade")
        self.item1 = Item.objects.create(nome="Item 1", categoria=self.categoria, unidade=self.unidade, quantidade_atual=10)
        self.item2 = Item.objects.create(nome="Item 2", categoria=self.categoria, unidade=self.unidade, quantidade_atual=20)


class EmprestimoModelTests(EstoqueBaseTestCase):

    def test_emprestimo_externo_creation_reduces_stock(self):
        """Testa se criar empréstimo externo reduz estoque."""
        emp = Emprestimo.objects.create(
            item=self.item1,
            tipo='EXTERNO',
            nome_solicitante="João Silva",
            contato="11999999999",
            quantidade_emprestada=3,
            data_prevista=timezone.now().date() + timedelta(days=7),
        )
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, 7)  # 10 - 3
        self.assertFalse(emp.devolvido)

    def test_emprestimo_interno_creation_reduces_stock(self):
        """Testa se criar empréstimo interno reduz estoque."""
        emp = Emprestimo.objects.create(
            item=self.item1,
            tipo='INTERNO',
            nome_solicitante="Funcionário NBR",
            contato="11888888888",
            quantidade_emprestada=2,
            data_prevista=timezone.now().date() + timedelta(days=3),
        )
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, 8)  # 10 - 2
        self.assertEqual(emp.tipo, 'INTERNO')

    def test_emprestimo_devolucao_total(self):
        """Testa devolução total do empréstimo."""
        emp = Emprestimo.objects.create(
            item=self.item1,
            tipo='EXTERNO',
            nome_solicitante="João",
            contato="123",
            quantidade_emprestada=5,
            data_prevista=timezone.now().date() + timedelta(days=7),
        )
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, 5)  # 10 - 5

        emp.data_devolucao = timezone.now().date()
        emp.quantidade_devolvida = 5
        emp.save()

        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, 10)  # 5 + 5
        self.assertTrue(emp.devolvido)

    def test_emprestimo_devolucao_parcial_requires_motivo(self):
        """Testa que devolução parcial exige motivo_falta."""
        emp = Emprestimo.objects.create(
            item=self.item1,
            tipo='EXTERNO',
            nome_solicitante="João",
            contato="123",
            quantidade_emprestada=5,
            data_prevista=timezone.now().date() + timedelta(days=7),
        )
        emp.data_devolucao = timezone.now().date()
        emp.quantidade_devolvida = 3
        emp.motivo_falta = ''

        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            emp.clean()

    def test_emprestimo_status_display_pendente(self):
        """Testa status display 'Pendente'."""
        emp = Emprestimo.objects.create(
            item=self.item1,
            tipo='EXTERNO',
            nome_solicitante="João",
            contato="123",
            quantidade_emprestada=1,
            data_prevista=timezone.now().date() + timedelta(days=7),
        )
        self.assertEqual(emp.status_display, 'Pendente')

    def test_emprestimo_status_display_atrasado(self):
        """Testa status display 'Atrasado'."""
        emp = Emprestimo.objects.create(
            item=self.item1,
            tipo='EXTERNO',
            nome_solicitante="João",
            contato="123",
            quantidade_emprestada=1,
            data_prevista=timezone.now().date() - timedelta(days=1),  # ontem
        )
        self.assertEqual(emp.status_display, 'Atrasado')

    def test_emprestimo_estoque_insuficiente(self):
        """Testa validação de estoque insuficiente."""
        emp = Emprestimo(
            item=self.item1,
            tipo='EXTERNO',
            nome_solicitante="João",
            contato="123",
            quantidade_emprestada=100,  # mais do que 10
            data_prevista=timezone.now().date() + timedelta(days=7),
        )
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            emp.clean()


class MovimentacaoTests(EstoqueBaseTestCase):

    def test_entrada_increases_stock(self):
        """Testa se uma entrada aumenta o estoque."""
        Movimentacao.objects.create(
            item=self.item1,
            tipo='ENTRADA',
            quantidade=5,
            usuario=self.user,
            origem_destino='Doação Empresa X'
        )
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, 15)  # 10 + 5

    def test_saida_decreases_stock(self):
        """Testa se uma saída diminui o estoque."""
        Movimentacao.objects.create(
            item=self.item1,
            tipo='SAIDA',
            quantidade=3,
            usuario=self.user,
            origem_destino='Uso interno'
        )
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, 7)  # 10 - 3

    def test_saida_insuficiente_blocked(self):
        """Testa que saída maior que o estoque é bloqueada na validação."""
        mov = Movimentacao(
            item=self.item1,
            tipo='SAIDA',
            quantidade=100,
            usuario=self.user,
        )
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            mov.clean()


class EmprestimoLoteViewTests(EstoqueBaseTestCase):

    def test_emprestimo_externo_lote_post(self):
        """Testa criação de empréstimo externo em lote via POST."""
        url = '/estoque/emprestimos/externo/novo/'
        data = {
            'nome_solicitante': 'Maria Santos',
            'contato': '11999999999',
            'data_saida': timezone.now().date().isoformat(),
            'data_prevista': (timezone.now().date() + timedelta(days=7)).isoformat(),
            'itens-TOTAL_FORMS': '2',
            'itens-INITIAL_FORMS': '0',
            'itens-MIN_NUM_FORMS': '0',
            'itens-MAX_NUM_FORMS': '1000',
            'itens-0-item': self.item1.id,
            'itens-0-quantidade': 2,
            'itens-1-item': self.item2.id,
            'itens-1-quantidade': 5,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # renders success page

        # Verify 2 empréstimos created with same grupo_lote
        emps = Emprestimo.objects.all()
        self.assertEqual(emps.count(), 2)

        lotes = set(emps.values_list('grupo_lote', flat=True))
        self.assertEqual(len(lotes), 1)  # same batch

        # Verify stock
        self.item1.refresh_from_db()
        self.item2.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, 8)   # 10 - 2
        self.assertEqual(self.item2.quantidade_atual, 15)  # 20 - 5

    def test_emprestimo_interno_lote_post(self):
        """Testa criação de empréstimo interno em lote via POST."""
        url = '/estoque/emprestimos/interno/novo/'
        data = {
            'nome_solicitante': 'Carlos Operação',
            'contato': '11777777777',
            'data_saida': timezone.now().date().isoformat(),
            'data_prevista': (timezone.now().date() + timedelta(days=3)).isoformat(),
            'itens-TOTAL_FORMS': '1',
            'itens-INITIAL_FORMS': '0',
            'itens-MIN_NUM_FORMS': '0',
            'itens-MAX_NUM_FORMS': '1000',
            'itens-0-item': self.item1.id,
            'itens-0-quantidade': 1,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # renders success page

        emp = Emprestimo.objects.last()
        self.assertEqual(emp.tipo, 'INTERNO')
        self.assertEqual(emp.quantidade_emprestada, 1)

        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, 9)

    def test_emprestimo_estoque_insuficiente_lote(self):
        """Testa que lote com estoque insuficiente re-renderiza o form."""
        url = '/estoque/emprestimos/externo/novo/'
        data = {
            'nome_solicitante': 'Teste',
            'contato': '123',
            'data_saida': timezone.now().date().isoformat(),
            'data_prevista': (timezone.now().date() + timedelta(days=7)).isoformat(),
            'itens-TOTAL_FORMS': '1',
            'itens-INITIAL_FORMS': '0',
            'itens-MIN_NUM_FORMS': '0',
            'itens-MAX_NUM_FORMS': '1000',
            'itens-0-item': self.item1.id,
            'itens-0-quantidade': 999,  # mais do que 10
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Estoque insuficiente')

        # Stock should be unchanged
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, 10)


class ReciboViewTests(EstoqueBaseTestCase):

    def test_recibo_emprestimo_by_grupo_lote(self):
        """Testa recibo de empréstimo acessado por grupo_lote."""
        emp = Emprestimo.objects.create(
            item=self.item1,
            tipo='EXTERNO',
            nome_solicitante="João",
            contato="123",
            quantidade_emprestada=1,
            data_prevista=timezone.now().date() + timedelta(days=7),
            grupo_lote='ABC123'
        )
        response = self.client.get('/estoque/recibo/emprestimo/ABC123/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_recibo_emprestimo_by_pk_fallback(self):
        """Testa recibo de empréstimo acessado por PK (fallback sem grupo_lote)."""
        emp = Emprestimo.objects.create(
            item=self.item1,
            tipo='EXTERNO',
            nome_solicitante="João",
            contato="123",
            quantidade_emprestada=1,
            data_prevista=timezone.now().date() + timedelta(days=7),
            # grupo_lote is None
        )
        response = self.client.get(f'/estoque/recibo/emprestimo/{emp.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_recibo_emprestimo_invalid_lote(self):
        """Testa recibo com lote inválido retorna mensagem de erro."""
        response = self.client.get('/estoque/recibo/emprestimo/INVALID_LOTE/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'não encontrado')

    def test_recibo_movimentacao(self):
        """Testa recibo de movimentação por grupo_lote."""
        Movimentacao.objects.create(
            item=self.item1,
            tipo='ENTRADA',
            quantidade=5,
            usuario=self.user,
            grupo_lote='MOV456'
        )
        response = self.client.get('/estoque/recibo/movimentacao/MOV456/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


class DevolucaoViewTests(EstoqueBaseTestCase):

    def test_devolucao_view_get(self):
        """Testa acesso à tela de devolução."""
        emp = Emprestimo.objects.create(
            item=self.item1,
            tipo='EXTERNO',
            nome_solicitante="João",
            contato="123",
            quantidade_emprestada=3,
            data_prevista=timezone.now().date() + timedelta(days=7),
        )
        response = self.client.get(f'/estoque/emprestimos/devolucao/{emp.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Registrar Devolução')

    def test_devolucao_view_post(self):
        """Testa submit de devolução total."""
        emp = Emprestimo.objects.create(
            item=self.item1,
            tipo='EXTERNO',
            nome_solicitante="João",
            contato="123",
            quantidade_emprestada=3,
            data_prevista=timezone.now().date() + timedelta(days=7),
        )
        self.item1.refresh_from_db()
        estoque_apos_emprestimo = self.item1.quantidade_atual  # 7

        response = self.client.post(f'/estoque/emprestimos/devolucao/{emp.pk}/', {
            'quantidade_devolvida': 3,
            'data_devolucao': timezone.now().date().isoformat(),
        })
        self.assertEqual(response.status_code, 302)  # redirect on success

        emp.refresh_from_db()
        self.assertTrue(emp.devolvido)

        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, estoque_apos_emprestimo + 3)  # stock restored
