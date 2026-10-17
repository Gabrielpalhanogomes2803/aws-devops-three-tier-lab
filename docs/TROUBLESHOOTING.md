# Troubleshooting realizado

| Sintoma observado | Diagnóstico | Correção/validação |
|---|---|---|
| Database não acessava Nginx em `10.10.1.96:80` | SG Database estava sem egress | Saída TCP 80 restrita para IP Front-end (teste temporário); `curl -I` deu 200 |
| Database não acessava API Back-end em TCP 3000 | Comportamento esperado: backend aceita 3000 apenas do SG Front-end | Não liberar acesso desnecessário |
| Instância privada sem acesso a APT | Subnet sem NAT nem rota pública | Proxy APT temporário no Front-end, filtros por domínio e SG restrito |
| Tinyproxy `filter file: Permission denied` | AppArmor `profile=tinyproxy` negou leitura de `/etc/tinyproxy/ubuntu-allowlist` | Adicionar regra de leitura em `local/tinyproxy` (não `local/usr.bin.tinyproxy`), recarregar perfil |
| Proxy devolvia 403 para Ubuntu durante teste no próprio Front-end | Logs `Unauthorized connection from "10.10.1.96"` | Adicionar `Allow 10.10.1.96`, manter filtro Ubuntu; 200 no repositório e 403 em example.com |
| Back-end timeout na porta proxy 8888 | Entrada SG Front-end só incluía o Database | Adicionar `10.10.2.214/32` à porta 8888; `curl` 200 |
| `python3 -m venv` falhou com `ensurepip is not available` | Pacote `python3.14-venv` ausente | Instalar via APT e recriar ambiente virtual incompleto |
| Python retornava 503 em `/api/tasks` | Logs: `password authentication failed for user devops_app` | Corrigir senha no arquivo `/etc/devops-backend.env`, reiniciar systemd; resposta HTTP 200 |
| Navegador recebia `{"error":"Not found"}` | URL tinha `?utm_source=chatgpt.com`, e handler comparava `self.path` inteira | `urlsplit(self.path).path`, permitindo query string; HTTP 200 |

## Comandos úteis

```bash
sudo journalctl -u devops-backend -n 60 --no-pager
sudo journalctl -u tinyproxy -n 30 --no-pager
sudo journalctl -k --no-pager | grep -i 'apparmor.*DENIED'
sudo systemctl is-active devops-backend
sudo pg_lsclusters
sudo ss -lntp | grep -E ':80|:3000|:5432|:8888'
curl -i 'http://127.0.0.1:3000/api/tasks?source=test'
```

Em caso de erro, identifique a camada (DNS, route table, SG/NACL, serviço, credenciais, SQL, HTTP) antes de abrir portas extras.
