from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Item, Categoria, UnidadeMedida, Movimentacao, Emprestimo

class EstoqueTests(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

        # Create base data
        self.categoria = Categoria.objects.create(nome="Geral")
        self.unidade = UnidadeMedida.objects.create(sigla="UN", nome="Unidade")
        self.item1 = Item.objects.create(nome="Item 1", categoria=self.categoria, unidade=self.unidade, quantidade_atual=10)
        self.item2 = Item.objects.create(nome="Item 2", categoria=self.categoria, unidade=self.unidade, quantidade_atual=20)

    def test_emprestimo_interno_flag(self):
        """Testa se o flag 'interno' do modelo Emprestimo funciona corretamente"""
        emprestimo = Emprestimo.objects.create(
            item=self.item1,
            nome_solicitante="Staff",
            contato="123",
            quantidade_emprestada=1,
            data_prevista="2024-01-01",
            interno=True
        )
        self.assertTrue(emprestimo.interno)
        
        # Verify it affects stock (logic in save method)
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, 9)

    def test_bulk_withdrawal_view(self):
        """Testa a view de saída em lote"""
        url = '/estoque/movimentacao/saida/lote/'
        
        # Prepare formset data
        data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            
            'form-0-item': self.item1.id,
            'form-0-quantidade': 5,
            
            'form-1-item': self.item2.id,
            'form-1-quantidade': 10,
        }
        
        response = self.client.post(url, data)
        
        # Should redirect on success
        if response.status_code != 302:
            import sys
            sys.stderr.write(f"\nFormset Errors: {response.context['formset'].errors}\n")
            
        self.assertEqual(response.status_code, 302)

    def test_bulk_withdrawal_decimal_input(self):
        """Testa se o form rejeita números decimais"""
        url = '/estoque/movimentacao/saida/lote/'
        
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            
            'form-0-item': self.item1.id,
            'form-0-quantidade': 5.5, # Decimal
        }
        
        response = self.client.post(url, data)
        
        # Should NOT redirect
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['formset'].is_valid())
        
        # Verify Items stock reduced
        self.item1.refresh_from_db()
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, 10) # Should be unchanged
        self.assertEqual(self.item2.quantidade_atual, 20) # Should be unchanged (entire formset validation fails)
        
        # Verify Movimentacao records NOT created
        self.assertEqual(Movimentacao.objects.filter(tipo='SAIDA').count(), 0)

    def test_bulk_withdrawal_insufficient_stock(self):
        """Testa validação de estoque insuficiente no lote"""
        url = '/estoque/movimentacao/saida/lote/'
        
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            
            'form-0-item': self.item1.id,
            'form-0-quantidade': 100, # More than 10
        }
        
        response = self.client.post(url, data)
        
        # Should NOT redirect (render form with errors)
        if response.status_code != 200:
            print(f"Status Code: {response.status_code}")
        
        try:
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Estoque insuficiente")
        except AssertionError:
            import sys
            sys.stderr.write(f"\nResponse Content: {response.content.decode()}\n")
            if 'formset' in response.context:
                 sys.stderr.write(f"Formset Errors: {response.context['formset'].errors}\n")
            raise

    def test_bulk_output_creating_loan(self):
        """Testa se a saída em lote cria Empréstimos quando marcado como interno"""
        url = '/estoque/movimentacao/saida/lote/'
        
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            
            'form-0-item': self.item1.id,
            'form-0-quantidade': 2,
            
            # Campos do formulário de opções
            'is_emprestimo': 'on',
            'nome_solicitante': 'Teste User',
            'contato': '9999-9999',
            'data_prevista': '2024-12-31'
        }
        
        response = self.client.post(url, data)
        
        if response.status_code != 302:
             import sys
             sys.stderr.write(f"\nResponse Content: {response.content.decode()}\n")
             if 'formset' in response.context:
                 sys.stderr.write(f"Formset Errors: {response.context['formset'].errors}\n")
             if 'options_form' in response.context:
                 sys.stderr.write(f"Options Errors: {response.context['options_form'].errors}\n")
        
        self.assertEqual(response.status_code, 302)
        
        # Debug: Check if Movimentacao was created instead
        if Movimentacao.objects.filter(tipo='SAIDA').count() > 0:
            print("DEBUG: Movimentacao created instead of Emprestimo. is_emprestimo flag failed?")
            
        # Verify Emprestimo created
        self.assertEqual(Emprestimo.objects.count(), 1) # Only 1 new (none in setup)
        emp = Emprestimo.objects.last()
        self.assertTrue(emp.interno)
        self.assertEqual(emp.nome_solicitante, 'Teste User')
        self.assertEqual(emp.item, self.item1)
        
        # Verify Stock reduced
        self.item1.refresh_from_db()
        self.assertEqual(self.item1.quantidade_atual, 8) # 10 - 2

    def test_bulk_output_loan_validation(self):
        """Testa validação dos campos de empréstimo"""
        url = '/estoque/movimentacao/saida/lote/'
        
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',
            
            'form-0-item': self.item1.id,
            'form-0-quantidade': 2,
            
            'is_emprestimo': 'on',
            # Falta nome e data
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        form_errors = response.context['options_form'].errors
        self.assertIn('nome_solicitante', form_errors)
        self.assertEqual(form_errors['nome_solicitante'], ["Nome do solicitante é obrigatório para empréstimos."])
