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

```bash
journalctl -u nbr-gestao -f
```

### 5. Configuração do Nginx (Acesso Rede/Externo)

O script `setup_service.sh` já instala e configura o **Nginx** automaticamente.
O Nginx funciona como um "proxy reverso", recebendo conexões na porta 80 e encaminhando para sua aplicação.

**Para acessar de outro notebook:**
1.  Descubra o IP do servidor Linux: `hostname -I` (ex: 137.131.208.204)
2.  No navegador do notebook, digite: `http://<IP-DO-SERVIDOR>`

**Nota sobre Arquivos Estáticos:**
O script também roda `python manage.py collectstatic` para reunir CSS/JS na pasta configurada.

## Solução de Problemas (Troubleshooting)

Se você não conseguir acessar pelo IP, verifique:

### 1. Firewall (iptables e UFW)
Às vezes o firewall padrão do Linux (`iptables`) bloqueia conexões mesmo que o UFW pareça estar OK (comum na Oracle Cloud).
Tente rodar estes comandos para "limpar" as regras de bloqueio (cuidado, isso libera tudo por um momento):

```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo netfilter-persistent save
```
Ou, se quiser testar liberando tudo (apenas para teste):
```bash
sudo iptables -F
```

Se depois disso funcionar, você sabe que há uma regra de iptables bloqueando.

### 2. AWS/Azure/Google Cloud/Oracle
Se estiver na nuvem (AWS, Oracle, Azure), você **PRECISA** liberar a **Porta 80 (HTTP)** e **Porta 443 (HTTPS)** no painel do provedor ("Security List", "Security Group" ou "Firewall Rules").
*   **Oracle Cloud:** Vá em VCN > Security Lists > Ingress Rules > Add Rule (Source 0.0.0.0/0, Port 80).

### 3. Verificar se o Nginx está rodando
```bash
sudo systemctl status nginx
```
Se estiver parado ou com erro, verifique os logs:
```bash
sudo journalctl -u nginx -e
```

### 4. Diagnóstico Avançado (Se nada funcionar)

Rode estes comandos no servidor para entender o que está acontecendo:

**A. Verifique se a porta 80 está "ouvindo":**
```bash
sudo ss -tulpn | grep :80
# DEVE retornar algo como: LISTEN 0 511 0.0.0.0:80 ... users:(("nginx"...))
```
Se não retornar nada, o Nginx não está escutando na porta.

**B. Teste o acesso local (de dentro do servidor):**
```bash
curl -I http://localhost
# DEVE retornar: HTTP/1.1 200 OK (ou 301/302)
```
Se der "Connection refused", o serviço web está parado.

**C. Verificar IP Publico:**
Algumas máquinas têm IPs internos diferentes dos externos (NAT). Confirme seu IP público:
```bash
curl -s ifconfig.me
```
Use **este IP** para tentar acessar do Windows.

**D. O Teste Definitivo (tcpdump):**
Este teste vai nos dizer se o bloqueio está NA NUVEM ou NO SERVIDOR.
1. Instale o tcpdump: `sudo apt install tcpdump -y`
2. Rode o comando para monitorar a porta 80:
   ```bash
   sudo tcpdump -i any port 80 -n
   ```
3. Tente acessar o site pelo seu computador (Windows).

**Análise do Resultado:**
*   **Você viu:** `Flags [S]` chegando do seu IP (ex: 177.x.x.x), mas **NENHUMA** resposta saindo.
*   **Diagnóstico:** O pacote **passou pela Nuvem** (AWS/Oracle OK), chegou na placa de rede, mas o **Linux recusou responder**.
*   **Culpado:** Regras de `iptables` persistentes (muito comum na Oracle Cloud).

**Solução (A "Opção Nuclear"):**
Rode estes comandos para limpar **todas** as regras de firewall do Linux instataneamente.

```bash
# Limpa todas as regras de bloqueio
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
sudo iptables -t nat -F
sudo iptables -t mangle -F
sudo iptables -F
sudo iptables -X
```

**Teste agora.** Se funcionar, você precisará salvar isso para não voltar a bloquear no reinício:
```bash
sudo netfilter-persistent save
```

## Configuração Manual (Opcional)

Se preferir configurar manualmente, edite `nbr-gestao.service` para corresponder aos seus caminhos e usuário, depois copie-o para `/etc/systemd/system/`.

```bash
sudo cp nbr-gestao.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable nbr-gestao
sudo systemctl start nbr-gestao
```

## Migrando para PostgreSQL

Se você quiser sair do SQLite e usar PostgreSQL, criamos scripts automáticos.

1.  **Backup:** Garanta que seu `db.sqlite3` está na pasta do projeto.
2.  **Execute o script de migração completa:**
    ```bash
    chmod +x migrate_to_postgres.sh
    ./migrate_to_postgres.sh
    ```
    
    O script irá:
    *   Exportar os dados atuais.
    *   Instalar e configurar o PostgreSQL.
    *   Criar o banco de dados `nbr_gestao`.
    *   Importar os dados para o novo banco.
    *   Reiniciar a aplicação.
