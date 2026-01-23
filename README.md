# NBR Gestão - Sistema de Gestão para ONG

## 📋 Sobre o Projeto

O **NBR Gestão** é um sistema integrado desenvolvido em Django para auxiliar na administração da ONG NBR. O sistema centraliza o controle de beneficiários, atividades diárias, estoque de materiais e gestão financeira, oferecendo uma plataforma robusta para a prestação de contas e organização interna.

## 🚀 Funcionalidades Principais (Módulos)

O sistema é dividido em módulos especializados:

### 1. 👥 Beneficiários (`beneficiarios`)
Gestão completa dos atendidos pela ONG.
*   **Cadastro Detalhado:** Dados pessoais, CPF, contato e responsável legal.
*   **Saúde e Inclusão:** Registro de quadros de saúde e necessidades de acessibilidade.
*   **Vínculos:** Associação com Projetos, Atividades e Turnos.
*   **Controle Automático:** Cálculo de idade e identificação de maioridade penal (18+).

### 2. ⚽ Atividades e Projetos (`atividades`)
Acompanhamento do dia a dia da ONG.
*   **Estrutura:** Projetos (ex: "Jovem Aprendiz") contêm múltiplos Tipos de Atividade (ex: "Futebol", "Dança").
*   **Diário de Classe (Digital):** Monitores registram as atividades diárias com:
    *   Descrição detalhada.
    *   Upload obrigatório de fotos e vídeos para comprovação.
    *   Validação de extensões de mídia.
*   **Controle de Acesso:** Permissões diferenciadas para Monitores, Professores e Admin.

### 3. 📦 Estoque e Patrimônio (`estoque`)
Controle rigoroso de materiais e empréstimos.
*   **Gestão de Saldo:** Entradas (Doações/Compras) e Saídas (Consumo) com validação de saldo negativo.
*   **Categorização:** Organização por Categorias e Unidades de Medida (KG, UN, LT).
*   **Controle de Empréstimos:**
    *   Registro de quem retirou (Nome, CPF, Endereço).
    *   Data de previsão de devolução.
    *   Baixa parcial ou total com justificativa de perdas/danos.

### 4. 💰 Financeiro (`financeiro`)
Gestão financeira focada em transparência e prestação de contas.
*   **Contas Bancárias:** Controle de saldo de múltiplas contas.
*   **Receitas:** Lançamento de entradas categorizadas.
*   **Despesas (Prestação de Contas):**
    *   Vínculo obrigatório com nota fiscal (Razão Social, CNPJ, Número, Série).
    *   Classificação por Rúbricas (ex: "Material de Consumo", "RH").
    *   Upload de comprovantes/notas fiscais.
    *   Bloqueio automático de despesas sem saldo em conta.

---

## 🛠️ Tecnologias Utilizadas

*   **Backend:** Python 3 + Django 6.0
*   **Banco de Dados:** SQLite (Desenvolvimento) / PostgreSQL (Recomendado Produção)
*   **Frontend:** Bootstrap 5 (Crispy Forms)
*   **Servidor:** Ver detalhes em `requisitos_servidor.md`

---

## ⚙️ Instalação e Configuração

### Pré-requisitos
*   Python 3.10+
*   Git

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/nbr-gestao.git
    cd nbr-gestao
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute as migrações do banco de dados:**
    ```bash
    python manage.py migrate
    ```

5.  **Crie um superusuário (Administrador):**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```

7.  Acesse o sistema em: `http://127.0.0.1:8000`

---

## 🔒 Perfis de Acesso

O sistema possui hierarquia de permissões gerenciadas via Django Groups:
*   **Administrador:** Acesso total a todos os módulos e configurações.
*   **Professor/Monitor:** Acesso restrito ao registro de atividades e visualização de turmas.

---

## 📄 Requisitos de Servidor

Para implantação em produção, consulte o documento detalhado: [requisitos_servidor.md](requisitos_servidor.md)
