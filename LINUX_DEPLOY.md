# Guia de Implantação Linux

Este guia explica como implantar a aplicação **nbr-gestao** como um serviço systemd no Linux usando Gunicorn.

## Pré-requisitos

- Servidor Linux (Ubuntu/Debian recomendado)
- Python 3.10+ instalado
- Ambiente virtual criado e ativo
- Arquivos do projeto clonados no servidor

## Passos para Configuração

### 1. Configurações de Ambiente

Crie um arquivo `.env` na raiz do projeto (`nbr-gestao/`) com seus segredos de produção:

```bash
# .env
SECRET_KEY='django-insecure'
DEBUG=False
ALLOWED_HOSTS=*,127.0.0.1
```

> **Dica:** Para gerar uma `SECRET_KEY` segura, rode este comando no terminal:
> ```bash
> python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
> ```

### 2. Instalar Dependências

Certifique-se de que seu ambiente virtual esteja ativo e as dependências instaladas:

```bash
cd /caminho/para/nbr-gestao
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar Serviço

Fornecemos um script `setup_service.sh` para automatizar a configuração. Ele irá:
1.  Instalar `gunicorn` se estiver faltando.
2.  Atualizar o arquivo `nbr-gestao.service` com seu usuário e caminhos de arquivo atuais.
3.  Vincular o serviço a `/etc/systemd/system/`.
4.  Iniciar e habilitar o serviço.

**Execute o script:**

```bash
chmod +x setup_service.sh
./setup_service.sh
```

### 4. Verificar Serviço

Verifique o status do serviço:

```bash
sudo systemctl status nbr-gestao
```

Para ver os logs:

```bash
journalctl -u nbr-gestao -f
```

## Configuração Manual (Opcional)

Se preferir configurar manualmente, edite `nbr-gestao.service` para corresponder aos seus caminhos e usuário, depois copie-o para `/etc/systemd/system/`.

```bash
sudo cp nbr-gestao.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nbr-gestao
sudo systemctl start nbr-gestao
```
