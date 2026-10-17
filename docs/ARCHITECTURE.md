# Arquitetura e inventário (implantação observada em 17/10/2026)

| Recurso | Valor observado | Observação |
|---|---|---|
| Região / AZ | `us-east-1` / `us-east-1a` | Todas as instâncias na mesma AZ |
| VPC | `lab-devops-vpc`, `10.10.0.0/16` | `vpc-0819e19ece4f17b58` |
| Subnet pública | `lab-subnet-public-frontend`, `10.10.1.0/24` | Front-end |
| Subnet privada | `lab-subnet-private-backend`, `10.10.2.0/24` | Back-end |
| Subnet privada | `lab-subnet-private-database`, `10.10.3.0/24` | Database |
| Front-end | `10.10.1.96`; IP público observado `3.82.18.225` | Nginx 1.28.3; Tinyproxy temporário |
| Back-end | `10.10.2.214` | Python 3.14.4, Psycopg 3.3.2, porta 3000 |
| Database | `10.10.3.72` | PostgreSQL 18.6, porta 5432 |
| Instâncias | 3 × `t3.micro` | Ubuntu 26.04 LTS |
| Par de chaves | `lab-devops-key` | PEM local, **não versionar** |

O IP público acima é um dado efêmero de laboratório, não um domínio ou endereço permanente. Sempre recupere o IP atual no Console ao reconstruir.

## Redes e rotas

- Subnet pública associada à `lab-rt-public` (`rtb-0211fb1ad2c3babfe`): rota local da VPC e `0.0.0.0/0` para IGW (`igw-001279c79a684384a`).
- Subnets privadas usam rota local da VPC, sem `0.0.0.0/0` para internet; o gateway que aparece em `ip route` dentro do Ubuntu **não** substitui a rota da VPC.
- Sem NAT Gateway. Tinyproxy foi instalado no Front-end apenas para encaminhar pedidos APT a dois domínios Ubuntu.

## Security Groups (intenção e testes)

| SG | Entrada | Saída |
|---|---|---|
| `lab-sg-frontend` (`sg-024fce58d72fb903c`) | TCP 80 da internet; TCP 22 somente do IP do estudante; TCP 8888 de `10.10.2.214/32` e `10.10.3.72/32` durante instalação | Em geral saída IPv4 liberada no laboratório |
| `lab-sg-backend` (`sg-0fb644e21ae5dc0eb`) | TCP 3000 do SG Front-end; TCP 22 do SG Front-end | Saída IPv4 liberada durante lab |
| `lab-sg-database` (`sg-01e7cdf294b607019`) | TCP 5432 do SG Back-end; TCP 22 do SG Front-end | TCP 80 para Front-end em teste; TCP 8888 para `10.10.1.96/32` durante instalação |

**Revalidar regras reais ao recriar**: estas refletem o histórico do laboratório, não uma exportação atual da AWS. Remover regras temporárias 80/8888 após a instalação, quando apropriado.

## Autenticação e privacidade

- `devops_app` (sem superusuário global) é dono de `devops_lab` e da tabela `tasks`.
- `pg_hba.conf`: regra `hostssl` para `10.10.2.214/32` com `scram-sha-256`.
- `listen_addresses = 'localhost,10.10.3.72'`.
- API usa um arquivo de variáveis protegido em `/etc/devops-backend.env`, carregado pelo systemd; não versionar seu conteúdo real.
- `sslmode=require` exige criptografia mas, com o certificado padrão de laboratório, não garante verificação de identidade do banco.

## Limites arquiteturais

Única AZ, uma instância por camada, nenhum Load Balancer, sem auto scaling, backups verificados ou autenticação na API. O HTTP público é em texto claro, e o endpoint expõe dados de tarefas sem login. Uso **somente didático**.
