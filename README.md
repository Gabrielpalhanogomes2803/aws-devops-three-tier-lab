# AWS DevOps Lab — Aplicação de 3 camadas

Laboratório educacional implementado **manualmente** no AWS Academy Learner Lab (região `us-east-1`), com três instâncias EC2 Ubuntu 26.04, rede segmentada, API Python e PostgreSQL. O endpoint de listagem foi validado no navegador com três tarefas reais do banco.

> **Estado do projeto:** GET `/api/tasks` e GET `/health` funcionam. Ainda não existe CRUD completo, autenticação, interface web de tarefas, HTTPS público, IaC, monitoramento ou alta disponibilidade. Não usar em produção sem hardening.

## Arquitetura

```text
Navegador (HTTP :80)
       |
       v
[Subnet pública 10.10.1.0/24]
 Front-end EC2 | Nginx (:80) | Tinyproxy temporário (:8888)
       |
       | TCP 3000 (acesso do SG do Front-end)
       v
[Subnet privada 10.10.2.0/24]
 Back-end EC2 | Python 3.14 + Psycopg 3 | systemd (:3000)
       |
       | TCP 5432 / TLS (acesso do SG do Back-end)
       v
[Subnet privada 10.10.3.0/24]
 Database EC2 | PostgreSQL 18.6 | devops_lab / tasks
```

- VPC: `10.10.0.0/16`, três subnets em `us-east-1a`.
- Subnet pública tem rota default para Internet Gateway. Subnets privadas têm apenas rota local da VPC, **sem NAT Gateway**.
- Back-end e Database não têm IPv4 público. Acesso administrativo por SSH via Front-end como bastion (`ProxyCommand`).
- Um proxy APT **temporário** na máquina pública permitiu instalar pacotes nas instâncias privadas com origem restrita no Tinyproxy e SG. Não confundir esse proxy com o reverse proxy Nginx.
- O proxy e endereços IP deste laboratório são exemplos específicos de uma implantação efêmera; ao recriar a infraestrutura, os valores serão diferentes.

## Validação realizada

```bash
# Front-end
curl -i http://localhost/api/tasks
# Resultado observado: HTTP 200 com três tarefas vindas do PostgreSQL

# Back-end
curl -i 'http://127.0.0.1:3000/api/tasks?utm_source=chatgpt.com'
# Resultado observado: HTTP 200

# Database
sudo pg_lsclusters
# 18 main 5432 online
```

Registros observados: `Configure AWS VPC`, `Deploy Backend API`, `Install PostgreSQL`.

## Conteúdo do repositório

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): infraestrutura, segmentação e fluxos.
- [`docs/SETUP.md`](docs/SETUP.md): reconstrução manual e ordem das operações.
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md): incidentes reais e correções.
- [`docs/SECURITY.md`](docs/SECURITY.md): controles, limitações e dados sensíveis.
- [`docs/TEARDOWN.md`](docs/TEARDOWN.md): checklist de destruição e custos.
- `backend/app.py`: aplicação Python (somente GET).
- `backend/schema.sql`: estrutura e dados didáticos.
- `configs/`: exemplos revisados das configurações do Nginx, systemd, PostgreSQL e Tinyproxy.
- `scripts/verify.sh`: verificações após implantação.

## GitHub

Este repositório **não contém credenciais, chaves PEM nem senhas**. Antes de qualquer commit, execute `git status` e revise os arquivos com `git diff --cached`. O `.gitignore` impede o versionamento acidental de arquivos comuns de credenciais, mas **não substitui a revisão humana**.

```bash
git init
git add README.md .gitignore backend frontend configs docs scripts
git diff --cached --stat
git diff --cached
git commit -m "docs: document manual AWS three-tier lab"
# Criar repositório vazio no GitHub e então:
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/aws-devops-three-tier-lab.git
git push -u origin main
```

Não execute `git remote add` com URL fictícia: troque `SEU-USUARIO` e crie o repositório primeiro. Também é possível usar `gh repo create` se GitHub CLI estiver autenticado.

## Recriar e evoluir

Este repositório é uma **documentação de um lab manual**, não um provisionador automático. Recrie seguindo [`docs/SETUP.md`](docs/SETUP.md), substituindo IPs e senhas. Próximos passos: interface web, POST/PATCH com autenticação, certificado TLS válido, IaC Terraform, CI/CD, observabilidade e backup/restauração testados.

## Encerramento do lab

Antes de destruir os recursos, confirme que não precisa dos dados. Execute [`docs/TEARDOWN.md`](docs/TEARDOWN.md). **Parar EC2 não equivale a apagar a infraestrutura; volumes EBS, snapshots, Elastic IP e outros recursos podem continuar cobrando.**
