# Segurança e restrições

**Jamais publicar:** chave PEM SSH, valor real de `PGPASSWORD`, arquivos `/etc/devops-backend.env`, `.env`, credenciais AWS, tokens, capturas de tela que revelem segredos, logs contendo autenticação. O `.gitignore` é uma proteção adicional e **não é garantia contra vazamentos**.

- Guardar secrets com permissões `root:devopslab` e `0640`; para produção usar gerenciador de segredos (AWS Secrets Manager ou equivalente), rotação e IAM mínimo.
- A API `/api/tasks` não possui autenticação, autorização, rate limiting ou validação de origem; está publicamente exposta via Nginx. **Não inserir dados pessoais ou confidenciais.**
- Front-end público serve HTTP sem TLS. Configurar HTTPS antes de dados reais, além de cabeçalhos de segurança e autenticação.
- PostgreSQL configurado com TLS `sslmode=require`, mas usando certificado padrão snakeoil: cifra a conexão, **não valida identidade**. Em produção, CA confiável e `sslmode=verify-full`.
- Rotas e SGs segmentam as três camadas; SG stateful permite resposta a conexões autorizadas. Remover entrada e egress TCP 8888 (e egress TCP 80 de testes) quando não precisar instalar atualizações, ou substituir por solução operacional segura.
- Tinyproxy é ferramenta de passagem temporária de pacotes; não transformar em open proxy. SG permite origens `/32`, proxy `Listen` privado, `Allow` por IP e `FilterDefaultDeny Yes`. Bloquear `CONNECT` se não necessário.
- Atualizações pendentes foram observadas em hosts (contagens variáveis após pacotes instalados). Planejar correções e reinício, sem interromper aplicações inadvertidamente.
- `t3.micro`, EBS pequeno, única AZ e ausência de backup validado são limitações didáticas.
