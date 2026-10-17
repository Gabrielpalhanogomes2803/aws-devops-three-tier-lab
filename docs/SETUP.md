# Reconstrução manual — passo a passo

**Pré-requisitos:** AWS Academy Learner Lab com créditos e permissões adequadas; AWS Console; cliente SSH e chave privada guardada fora do Git. Substitua IPs, IDs, senha e endereços a cada nova implantação.

1. **VPC/subnets:** VPC `10.10.0.0/16`; subnets pública `10.10.1.0/24`, privada Back-end `10.10.2.0/24`, privada Database `10.10.3.0/24`, na mesma AZ. Crie IGW e associe rota pública `0.0.0.0/0`. Não atribua IP público às instâncias privadas.
2. **Security Groups:** libere TCP 80 no Front-end, SSH 22 só do seu IP, TCP 3000 no Back-end somente do SG Front-end e TCP 5432 no Database somente do SG Back-end; regras SSH de bastion conforme necessário. Bloqueie acesso público ao banco.
3. **EC2:** três `t3.micro` Ubuntu; dimensionamento exclusivamente didático. Front-end como bastion via SSH, sem copiar a chave PEM para as instâncias.
4. **Nginx no Front-end:** `sudo apt-get update && sudo apt-get install -y nginx`; crie arquivo de site a partir de `configs/nginx/devops-lab.conf`, adapte o IP Back-end; symlink em `sites-enabled`, desabilite o site padrão se necessário, `sudo nginx -t && sudo systemctl reload nginx`.
5. **Back-end:** instale Python e `python3.14-venv` conforme versão disponível. Copie `backend/app.py` para `/opt/devops-lab/app.py`; crie usuário de serviço `devopslab`, ambiente virtual com `--system-site-packages`, instale `python3-psycopg` pelo APT e valide `import psycopg`. Garanta propriedade/permissões do diretório.
6. **Proxy APT temporário:** se não houver NAT, instale Tinyproxy no Front-end (o único host com internet), com arquivo de exemplo em `configs/tinyproxy/`. Restrinja `Listen` ao IP privado; aplique `Allow` apenas aos IPs de Back-end/Database; filtro padrão deny por domínio; permita TCP 8888 no SG Front-end só a esses IPs; permita saída correspondente das instâncias privadas. Teste um repositório permitido **e um domínio bloqueado**. O perfil AppArmor em Ubuntu 26.04 precisa ler a allowlist; acrescentar `/etc/tinyproxy/ubuntu-allowlist r,` em `/etc/apparmor.d/local/tinyproxy`, recarregar `sudo apparmor_parser -r /etc/apparmor.d/tinyproxy`. Configure nos hosts privados `/etc/apt/apt.conf.d/90devops-proxy` com `Acquire::http::Proxy "http://IP-PRIVADO-FRONTEND:8888/";`. **Não publicar 8888 na internet.**
7. **PostgreSQL:** instale `postgresql` no Database. Confirme `sudo pg_lsclusters`. Via `sudo -u postgres psql`, crie `CREATE ROLE devops_app LOGIN;` e `CREATE DATABASE devops_lab OWNER devops_app;`. Defina senha interativamente com `\password devops_app` (não incluir senha em logs, shell, Git). Execute `backend/schema.sql` conectado como `devops_app`.
8. **Acesso remoto DB:** adapte `listen_addresses` ao IP privado DB; acrescente `hostssl devops_lab devops_app IP-PRIVADO-BACKEND/32 scram-sha-256` ao `pg_hba.conf`; reinicie `postgresql@18-main` e valide `sudo ss -lntp | grep ':5432'`. Use `psql "host=... dbname=devops_lab user=devops_app sslmode=require" -W` desde o Back-end para consultar as tarefas.
9. **Credenciais / systemd:** crie `/etc/devops-backend.env` a partir do modelo em `configs/systemd/devops-backend.env.example`, **fora do repositório Git**. `sudo chown root:devopslab ...; sudo chmod 640 ...`. Ajuste `configs/systemd/devops-backend.service`, `sudo systemctl daemon-reload`, `sudo systemctl restart devops-backend`, valide status e journal. O serviço deve rodar com usuário dedicado.
10. **Testes:** `curl -i http://127.0.0.1:3000/api/tasks` no Back-end; `curl -i http://localhost/api/tasks` no Front-end; teste URL pública digitada diretamente no navegador. O handler usa `urlsplit` para aceitar query strings sem retornar falso 404.
11. **Hardening / saída:** remover proxy e portas temporárias, configurar TLS público e certificado PostgreSQL validável antes de produção; criar backups, aplicar atualizações, documentar mudanças. Para desligar custos, consulte `docs/TEARDOWN.md`.

## SSH bastion (no computador local)

```bash
ssh -i ~/Downloads/lab-devops-key.pem \
  -o ProxyCommand="ssh -i ~/Downloads/lab-devops-key.pem -W %h:%p ubuntu@IP-PUBLICO-FRONTEND" \
  ubuntu@IP-PRIVADO-BACKEND
```

Nunca commitar `lab-devops-key.pem`.

## Restrições do laboratório

Sem NAT, o `pip` não teria automaticamente acesso ao PyPI. Usamos Psycopg instalado pelo repositório Ubuntu, com `venv --system-site-packages`. Esse arranjo serve ao laboratório, porém mistura pacotes do SO à resolução de dependências do venv.
