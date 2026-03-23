#!/bin/bash
# ============================================================
# NBR Gestão - Script Mestre de Deploy
# VPS Hostinger Ubuntu 24.04 LTS
#
# Uso: bash deploy.sh [--skip-postgres] [--skip-ssl]
#   --skip-postgres   Pula a migração para PostgreSQL (mantém SQLite)
#   --skip-ssl        Pula a configuração do certificado SSL
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

SKIP_POSTGRES=false
SKIP_SSL=false

for arg in "$@"; do
    case $arg in
        --skip-postgres) SKIP_POSTGRES=true ;;
        --skip-ssl)      SKIP_SSL=true ;;
    esac
done

PROJECT_DIR=$(pwd)
REPO_URL=""  # Preenchido automaticamente se clonado via git

step() { echo -e "\n${BLUE}========================================${NC}"; echo -e "${BLUE}  $1${NC}"; echo -e "${BLUE}========================================${NC}"; }
ok()   { echo -e "${GREEN}[OK] $1${NC}"; }
warn() { echo -e "${YELLOW}[AVISO] $1${NC}"; }
fail() { echo -e "${RED}[ERRO] $1${NC}"; exit 1; }

# ============================================================
# PASSO 1 - Verificações Iniciais
# ============================================================
step "PASSO 1 - Verificações Iniciais"

if [ ! -f "${PROJECT_DIR}/manage.py" ]; then
    fail "manage.py não encontrado. Execute este script a partir da raiz do projeto."
fi

if [ ! -f "${PROJECT_DIR}/.env" ]; then
    fail ".env não encontrado!\nCopie o template: cp .env.example .env\nPreencha os valores e execute novamente."
fi

# Verifica SECRET_KEY
if grep -q "sua-chave-secreta-aqui" "${PROJECT_DIR}/.env"; then
    fail "SECRET_KEY ainda é o valor padrão no .env!\nGere uma chave segura:\n  python3 -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
fi

ok "Verificações iniciais concluídas."

# ============================================================
# PASSO 2 - Atualizar Sistema e Instalar Dependências
# ============================================================
step "PASSO 2 - Atualizar Sistema e Instalar Dependências"

sudo apt-get update -qq && sudo apt-get upgrade -y -qq
sudo apt-get install -y -qq \
    python3-pip \
    python3-venv \
    nginx \
    libpq-dev \
    git \
    curl

ok "Dependências do sistema instaladas."

# ============================================================
# PASSO 3 - Ambiente Virtual e Dependências Python
# ============================================================
step "PASSO 3 - Ambiente Virtual Python"

if [ ! -d "${PROJECT_DIR}/venv" ]; then
    python3 -m venv "${PROJECT_DIR}/venv"
    ok "Ambiente virtual criado."
else
    ok "Ambiente virtual já existe."
fi

"${PROJECT_DIR}/venv/bin/pip" install --quiet --upgrade pip
"${PROJECT_DIR}/venv/bin/pip" install --quiet -r "${PROJECT_DIR}/requirements.txt"
ok "Dependências Python instaladas."

# ============================================================
# PASSO 4 - Configurar Serviço (Gunicorn + Nginx)
# ============================================================
step "PASSO 4 - Configurando Serviço Gunicorn e Nginx"

chmod +x "${PROJECT_DIR}/setup_service.sh"
bash "${PROJECT_DIR}/setup_service.sh"
ok "Serviço e Nginx configurados."

# ============================================================
# PASSO 5 - Migração para PostgreSQL (opcional)
# ============================================================
if [ "$SKIP_POSTGRES" = false ]; then
    step "PASSO 5 - Migração SQLite → PostgreSQL"

    if [ -f "${PROJECT_DIR}/db.sqlite3" ]; then
        chmod +x "${PROJECT_DIR}/migrate_to_postgres.sh"
        bash "${PROJECT_DIR}/migrate_to_postgres.sh"
        ok "Migração para PostgreSQL concluída."
    else
        warn "db.sqlite3 não encontrado. Pulando migração de dados."
        warn "Rodando apenas as migrations no PostgreSQL..."
        chmod +x "${PROJECT_DIR}/setup_postgres.sh"
        bash "${PROJECT_DIR}/setup_postgres.sh"
        set -a; source "${PROJECT_DIR}/.env"; set +a
        "${PROJECT_DIR}/venv/bin/python" manage.py migrate
    fi
else
    step "PASSO 5 - Migração PostgreSQL [PULADO]"
    warn "Mantendo SQLite como banco de dados."
    set -a; source "${PROJECT_DIR}/.env"; set +a
    "${PROJECT_DIR}/venv/bin/python" manage.py migrate
fi

# ============================================================
# PASSO 6 - SSL com Certbot (opcional)
# ============================================================
if [ "$SKIP_SSL" = false ]; then
    step "PASSO 6 - Configuração SSL com Certbot"

    # Detectar domínio do .env
    DOMAIN=$(grep "ALLOWED_HOSTS" "${PROJECT_DIR}/.env" | cut -d'=' -f2 | tr ',' '\n' | grep -v '^[0-9]' | head -1)

    if [ -z "$DOMAIN" ]; then
        warn "Nenhum domínio encontrado em ALLOWED_HOSTS. Pulando SSL."
        warn "Para configurar SSL manualmente:\n  sudo apt install certbot python3-certbot-nginx -y\n  sudo certbot --nginx -d seu-dominio.com"
    else
        echo "Domínio detectado: $DOMAIN"
        sudo apt-get install -y -qq certbot python3-certbot-nginx
        sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "admin@${DOMAIN}" || \
            warn "Certbot falhou. Verifique se o domínio aponta para este servidor e tente:\n  sudo certbot --nginx -d ${DOMAIN}"
    fi
else
    step "PASSO 6 - SSL [PULADO]"
    warn "Para configurar SSL depois:\n  sudo apt install certbot python3-certbot-nginx -y\n  sudo certbot --nginx -d seu-dominio.com"
fi

# ============================================================
# PASSO 7 - Status Final
# ============================================================
step "PASSO 7 - Status dos Serviços"

echo ""
sudo systemctl status nbr-gestao --no-pager || true
echo ""
sudo systemctl status nginx --no-pager || true

SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Deploy concluído com sucesso!${NC}"
echo -e "${GREEN}  Acesse: http://${SERVER_IP}${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Comandos úteis:"
echo "  sudo journalctl -u nbr-gestao -f        # Logs em tempo real"
echo "  sudo systemctl restart nbr-gestao       # Reiniciar serviço"
echo "  sudo systemctl restart nginx            # Reiniciar Nginx"
echo "  ${PROJECT_DIR}/venv/bin/python manage.py createsuperuser  # Criar admin"
