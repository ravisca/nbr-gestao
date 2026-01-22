# Requisitos de Servidor - NBR Gestão

Este documento detalha os requisitos mínimos e recomendados de hardware para hospedar o sistema **NBR Gestão** (Django), considerando diferentes volumes de usuários simultâneos.

> **Nota:** As estimativas consideram o uso do sistema para cadastro, navegação e geração eventual de relatórios em PDF (que consome mais CPU).

---

## 🏗️ Arquitetura Recomendada (Produção)
Para todos os cenários, recomenda-se a seguinte "stack" básica:
*   **SO:** Linux (Ubuntu 22.04 LTS ou Debian 11/12)
*   **Web Server:** Nginx (Proxy Reverso)
*   **App Server:** Gunicorn ou Uvicorn
*   **Banco de Dados:** PostgreSQL (Recomendado) ou SQLite (Apenas para < 10 usuários com baixo tráfego)

---

## 1. Pequeno Porte (Até 10 Usuários)
Ideal para fase inicial ou pequenas filiais. O banco de dados pode rodar no mesmo servidor da aplicação.

*   **CPU:** 1 vCPU (Core)
*   **RAM:** 2 GB
    *   *1 GB para o sistema/BD + 1 GB para aplicação (2 workers Gunicorn).*
*   **Armazenamento:** 20 GB SSD
*   **Banco de Dados:** SQLite (funciona bem) ou PostgreSQL local.
*   **Exemplo Cloud:** AWS t3.small / DigitalOcean Droplet Basic (2GB)

---

## 2. Médio Porte (Até 30 Usuários)
Cenário onde múltiplos usuários podem gerar relatórios ao mesmo tempo. É mandatório o uso de PostgreSQL para evitar travamentos de escrita (lock) do SQLite.

*   **CPU:** 2 vCPUs
    *   *Importante para garantir fluidez durante a geração de PDFs.*
*   **RAM:** 4 GB
*   **Armazenamento:** 40 GB SSD
*   **Banco de Dados:** PostgreSQL (Local ou serviço gerenciado simples).
*   **Exemplo Cloud:** AWS t3.medium / DigitalOcean Droplet (4GB / 2 vCPU)

---

## 3. Grande Porte (Até 100 Usuários)
Cenário com alta concorrência. Recomenda-se separar o servidor de Aplicação do servidor de Banco de Dados.

### Opção A: Servidor Único (Robusto)
*   **CPU:** 4 vCPUs
*   **RAM:** 8 GB
*   **Armazenamento:** 80 GB SSD NVMe
*   **Banco de Dados:** PostgreSQL otimizado localmente.

### Opção B: Arquitetura Separada (Recomendada)
*   **Servidor Web (App):** 2 vCPU / 4 GB RAM
*   **Servidor Banco de Dados:** 2 vCPU / 4 GB RAM (PostgreSQL)
*   **Armazenamento:** S3 ou similar para arquivos de mídia (Uploads) se houver muito volume.

---

## 📝 Resumo da Tabela

| Capacidade | CPU | RAM | Disco | Banco de Dados |
| :--- | :--- | :--- | :--- | :--- |
| **10 Usuários** | 1 Core | 2 GB | 20 GB | SQLite/Postgres |
| **30 Usuários** | 2 Cores | 4 GB | 40 GB | PostgreSQL |
| **100 Usuários**| 4 Cores | 8 GB | 80 GB+ | PostgreSQL (Ded.)|

## Considerações Especiais
1.  **Geração de PDF:** A biblioteca de PDF consome processamento. Se muitos usuários gerarem relatórios ("Lista de Chamada" de 100 páginas) simultaneamente, o consumo de CPU vai a 100%. Para 100 usuários, considere usar filas de tarefas (Celery + Redis) para processar relatórios em segundo plano.
2.  **Backups:** Independente do tamanho, configure backups diários do banco de dados (dump do Postgres ou cópia do arquivo .sqlite3) e da pasta `media/`.
