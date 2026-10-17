# Destruição segura e controle de custos — AWS Academy

**Cuidado: as ações abaixo apagam recursos e podem apagar o banco de dados permanentemente.** Faça somente quando tiver revisado esta documentação, confirmado que o GitHub contém os arquivos desejados e que não precisa mais dos dados (ou exportou backup seguro). Não envie um `terraform destroy`: este laboratório foi criado **manualmente**, sem estado Terraform.

## Antes de apagar

- [ ] Repositório no GitHub criado; `git push` concluído e arquivos conferidos no site.
- [ ] Nenhuma chave `.pem`, senha, `.env` ou secret exposto no GitHub.
- [ ] Salvar logs ou capturas sanitizadas que desejar para o portfólio.
- [ ] Decidir se precisa de backup da base PostgreSQL. Se sim, `pg_dump` para armazenamento autorizado e seguro; **nunca versionar o dump com dados sensíveis**.
- [ ] Conferir instâncias, região, volumes, endereços e créditos antes de excluir.

## Sequência de exclusão (Console AWS, região `us-east-1`)

1. Em **EC2 → Instances**, identifique por ID/tags as três EC2 deste laboratório e escolha **Terminate instance**. Confirme IDs antes da ação; não terminar recursos de outros projetos. Registre se os EBS estavam configurados como `Delete on termination`.
2. Em **EC2 → Volumes**, procure volumes EBS remanescentes/desanexados associados às três instâncias. Apague apenas os volumes do laboratório após conferir backups e necessidade dos dados. **EBS pode cobrar mesmo com instância parada.**
3. Em **EC2 → Snapshots / AMIs**, verifique snapshots e imagens criadas por você e remova apenas os que não são mais necessários (respeitando dependências de AMI).
4. Em **EC2 → Elastic IP addresses**, verifique se alocou algum EIP: liberar alocações sem uso que pertençam ao laboratório. O IPv4 público automático não é necessariamente um Elastic IP; não presumir que haja EIP.
5. Verifique **Load Balancers, Target Groups, NAT Gateways, Network Interfaces, Endpoints** e outros recursos pagos, caso tenha criado adicionais. Neste histórico **não** foi criado NAT Gateway nem Load Balancer.
6. Em **VPC → Security Groups**, exclua os três SGs do laboratório após terminar EC2 e eliminar dependências entre SGs.
7. Em **VPC → Route Tables**, remova associações específicas e tabelas personalizadas do laboratório conforme a Console permitir.
8. Em **VPC → Internet Gateways**, desanexe e exclua o IGW do laboratório (após dependências liberadas).
9. Em **VPC → Subnets**, exclua as três subnets, após remover ENIs/recursos dependentes.
10. Em **VPC → Your VPCs**, exclua `lab-devops-vpc` e eventuais componentes remanescentes permitidos pela Console. A ordem das etapas 6–10 pode variar conforme dependências exibidas; a exclusão da VPC na Console também pode oferecer limpeza de recursos dependentes.
11. Reavalie **EC2, EBS, Snapshots, Elastic IP, VPC, NAT, Load Balancers, CloudWatch e Billing/Cost Explorer** em `us-east-1` e qualquer outra região utilizada. Confirme que não sobrou nenhum recurso do laboratório.

## Parar vs terminar

- **Stop:** suspende a cobrança de computação EC2 em muitos casos, mas EBS e IPv4 público/Elastic IP e outros recursos podem continuar cobrando; o IP público automático pode mudar.
- **Terminate:** encerra a instância, mas confirme exclusão de volumes, snapshots, EIPs e outros recursos dependentes.
- Créditos e comportamento do Learner Lab podem ter particularidades: confirmar custos e política da sua conta antes de sair.

## Depois de destruir

Atualize o README do GitHub com nota **"Infraestrutura desativada para evitar custos; código e documentação preservados"**. Endereço público e screenshots deixam de provar disponibilidade atual. A recriação deve usar novos IDs e IPs.
