---
title: "Cansei de procurar arquivos em 4 PCs: montei um servidor NFS em casa"
published: true
description: Como transformei um Ubuntu Server ocioso em um servidor de arquivos com NFS para compartilhar projetos e anotações entre vários PCs, e o perrengue que tive para fazer o WSL enxergar a pasta.
tags: linux, homelab, devops, braziliandevs
cover_image: https://dev-to-uploads.s3.us-east-2.amazonaws.com/uploads/articles/6iax8mv3lvurop9l7tyt.png
series: Homelab na prática
canonical_url: https://dev.to/jefferson682/cansei-de-procurar-arquivos-em-4-pcs-montei-um-servidor-nfs-em-casa-1jh6
---

## Introdução

Esses dias me peguei pensando na dificuldade que eu tinha para acessar alguns arquivos simples, de anotações, aquelas coisas que eu deixava quietinhas em um `.txt` para dar uma espiada depois. Isso começou a virar um problema.

Atualmente trabalho como DevOps em uma empresa da área da saúde. Como em toda empresa, recebi um computador para trabalhar, no caso um notebook com Ubuntu Desktop. O problema é que ele não tem uma saída HDMI que suporte a resolução do meu monitor, então, para trabalhar com duas telas, acabei transformando meu desktop pessoal em computador de trabalho também. Além disso, tenho dois PCs com Ubuntu Server que uso como laboratório (subindo k8s, testando playbooks etc.) e, no meu PC com Windows, gosto de testar distros no WSL: quebrar, reconstruir, de tudo um pouco, derivados de Red Hat, Debian e por aí vai.

O problema estava nos pequenos ajustes e anotações. Muitas vezes eu estava no notebook, com uma tela só, ia para o desktop (ou vice-versa) e lá não estava o projeto ou documento em que eu vinha trabalhando ou estudando. Outro problema era achar os arquivos: eu estudava um assunto, anotava, continuava o mesmo assunto em outro PC, anotava de novo e, no fim, não sabia mais onde estava cada informação. Em qual PC estava aquele `.txt` mesmo? Foi aí que pensei: cara... como posso centralizar isso?

## O que eu considerei antes

Sei que já existem ferramentas prontas para problemas parecidos, mas nenhuma se encaixava no que eu realmente precisava.

A primeira seria usar Git, com um remote no GitHub, GitLab etc. Só que eu não quero configurar chave SSH em toda máquina de lab que subo, muito menos commitar um `.env` ou um `notas.txt`. E muitas vezes estamos fazendo troubleshooting numa máquina, já com algumas edições no projeto, mas ainda sem solução. Para trocar de máquina eu teria que commitar, fazer push, ir para a outra máquina, fazer pull e tentar não esquecer nada para não dar conflito. E o que, para mim, é pior: os commits lixo. Sei que dá para fazer squash, mas olha o tamanho da trabalheira...

E tem também aquelas credenciais que eu sei que você anota num `.env` (Deus está vendo). Todo mundo, uma hora ou outra, deixa um `pass.txt` anotado em algum lugar, principalmente quando são senhas de teste e de lab, em que não vale a pena subir um Vault, o Parameter Store da AWS ou ferramentas parecidas.

Existem também Google Drive, Notion, OneDrive etc., mas tem lugares em que vou estar só com um terminal e um `vi`. Para mim, nesse caso, essas ferramentas não servem.

Meu primeiro pensamento foi usar sshfs ou o Syncthing, com os arquivos ficando em um dos dois servidores. Mas havia dois problemas: o sshfs é lento, e o Syncthing pode dar problema caso eu edite o mesmo arquivo em mais de um lugar ao mesmo tempo (tipo um conflito de Git), além de sofrer com pastas como `node_modules`, `.venv` etc.

Daí veio o segundo pensamento: tenho dois PCs relativamente bons, com bastante espaço em disco e subutilizados. Que tal criar um servidor de arquivos?

Pesquisei algumas soluções. Uma delas era formatar um PC e montar um NAS. Pensei em discos redundantes, criptografia... estava eu lá sonhando, até perceber que era matar uma mosca com uma bazuca.

Pensei no Samba, mas, como já uso WSL, não preciso de tudo o que ele oferece. A prioridade não é versionar nada, mas ter o mesmo estado dos arquivos (projetos, `.env`, anotações) em qualquer PC. Eu só queria um lugar para guardar meus arquivos, independentemente do PC que estou usando em casa, e poder sair de um PC para outro e continuar exatamente de onde parei, sem muita dor de cabeça. A solução? **NFS**.

Resumindo as opções:

| Opção | Por que descartei |
|---|---|
| Git (GitHub/GitLab) | Chave SSH em toda máquina, risco de commitar `.env`, commits lixo para trocar de PC |
| Google Drive / Notion / OneDrive | Não funcionam num servidor que só tem terminal e `vi` |
| sshfs | Lento |
| Syncthing | Conflito ao editar em dois lugares, sofrem com `node_modules`/`.venv` |
| NAS dedicado | Bazuca para matar mosca |
| Samba | Mais do que eu preciso, já que uso WSL |
| **NFS** | ✅ Simples, nativo no Linux, uma única cópia dos arquivos |

## Pré-requisitos

- Mais de um PC
- Linux (qualquer um). Aqui usei Ubuntu Server, Ubuntu Desktop, Pop!_OS, Oracle Linux e Ubuntu no WSL
- Vontade de arrumar problema para dar manutenção depois

## O cenário

O NFS (Network File System) é um protocolo que permite compartilhar uma pasta de uma máquina Linux pela rede. Os outros PCs montam essa pasta como se fosse um diretório local. A instalação é bem simples: um pacote para o servidor e outro para os clientes.

```plaintext
                  ┌──────────────────────────┐
                  │  cabugi (Ubuntu Server)  │
                  │  /srv/nfs/shared         │
                  └────────────┬─────────────┘
                               │ NFSv4 (TCP 2049)
          ┌────────────────────┼────────────────────┐
          │                    │                    │
   Notebook (Ubuntu)    Desktop (Pop!_OS)    Windows + WSL
     ~/shared              ~/shared            ~/shared
```

Dá para aumentar a segurança da pasta compartilhada filtrando os IPs dos clientes ou até adicionando autenticação. Mas, nesta V0 de laboratório, acabei liberando tudo para a minha rede interna, que considero "segura" na medida do possível: aqui tenho duas redes, uma exclusiva para mim (trabalho e estudo) e outra para os demais dispositivos da casa, como TVs e smartphones.

Como eu já tinha dois Ubuntu Server ligados 24/7, faltava só implementar. Então vamos à receitinha de bolo.

## 1. Configurando o servidor

Primeiro, acesse o servidor onde os arquivos vão ficar centralizados. No meu caso, não é tudo que quero colocar em rede, mas estudos e algumas pastas de "anotações de troubleshooting" são interessantes de ter em mais de um lugar.

Você pode literalmente ir até o servidor ou, no meu caso, como ele não tem periféricos, acessar via SSH:

```bash
ssh sysadmin@10.220.0.19
```

Onde `sysadmin` é o meu usuário e `10.220.0.19` é o IP da máquina.

Depois de acessar, instale o pacote do servidor e crie a pasta que será compartilhada:

```bash
sudo apt update && sudo apt install -y nfs-kernel-server
sudo mkdir -p /srv/nfs/shared && sudo chown 1000:1000 /srv/nfs/shared
```

O `chown 1000:1000` define como dono da pasta o usuário e o grupo de ID 1000. Na maioria das distros, esse é o ID do primeiro usuário criado na instalação, ou seja, provavelmente o seu. Isso importa porque o NFS (no modo padrão, sem Kerberos) valida permissões pelo **número** do usuário (UID/GID), e não pelo nome.

> 💡 **Dica:** confira o seu UID e GID com `id -u` e `id -g`. Se não forem 1000, ajuste o `chown` e as opções `anonuid`/`anongid` mais abaixo.

### Descobrindo a sub-rede

Agora você precisa descobrir a faixa da sua sub-rede:

```bash
ip -4 addr show | grep inet
```

Cada linha `inet` é um endereço IP em uma interface. Interface é uma "porta de rede" da máquina, que pode ser física (cabo, Wi-Fi) ou virtual (Docker, k3s, VPN). Uma máquina pode ter várias.

No meu caso:

```text
inet 127.0.0.1/8         scope host  lo           ← loopback
inet 10.220.0.19/24  ... dynamic     enp1s0       ← placa de rede real (cabo)
inet 10.42.1.0/32        ...         flannel.1    ← rede interna do k3s
inet 10.42.1.1/24        ...         cni0         ← rede interna do k3s
```

A interface que interessa é a placa de rede real (`enp1s0`). O IP é `10.220.0.19/24`, e o `/24` indica que os três primeiros blocos são a rede. Então minha sub-rede é `10.220.0.0/24` (de `10.220.0.1` a `10.220.0.254`).

### Exportando a pasta

Adicione a linha abaixo em `/etc/exports`, trocando `10.220.0.0/24` pela sua sub-rede:

```text
/srv/nfs/shared  10.220.0.0/24(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000)
```

O que cada pedaço faz:

| Pedaço | O que faz | Por quê |
|---|---|---|
| `/srv/nfs/shared` | Pasta exportada | É o que os clientes vão montar |
| `10.220.0.0/24` | Quem pode montar: qualquer IP `10.220.0.x` | Só a sua rede local |
| `rw` | Leitura e escrita | O padrão seria `ro`, só leitura |
| `sync` | Só confirma a escrita depois de gravar no disco | Mais seguro. `async` é mais rápido, mas pode perder dados se o servidor cair |
| `no_subtree_check` | Desliga uma verificação extra de caminho | É o recomendado. A verificação causa erros quando arquivos são renomeados |
| `all_squash` | Trata todo usuário do cliente como anônimo | Resolve a bagunça de UIDs diferentes entre PCs |
| `anonuid=1000,anongid=1000` | O "anônimo" passa a ser o UID/GID 1000 | Tudo o que você criar, de qualquer PC, fica com o mesmo dono |

Salve o arquivo e aplique a configuração:

```bash
sudo exportfs -ra && sudo exportfs -v
```

O `-ra` relê o `/etc/exports` e reaplica os compartilhamentos; o `-v` lista o que está sendo exportado, para você conferir.

Se o `ufw` estiver ativo, libere a porta. O NFSv4 só precisa da 2049:

```bash
sudo ufw allow from 10.220.0.0/24 to any port 2049 proto tcp
```

> ⚠️ **IP fixo:** garanta que o servidor tenha IP fixo, por reserva de DHCP no roteador ou configuração estática no netplan. Sem isso, ao reiniciar, o roteador pode entregar outro endereço para o servidor, e os clientes vão procurar a pasta no IP antigo.

No meu caso, acabei não fixando o IP porque gosto de arrumar problemas :) Na verdade, gosto quando quebra, para simular um problema real e testar meus "dotes" de troubleshooting.

Para validar se o serviço subiu:

```bash
systemctl status nfs-server --no-pager
```

A minha saída foi esta:

```text
sysadmin@cabugi:~$ systemctl status nfs-server --no-pager
● nfs-server.service - NFS server and services
     Loaded: loaded (/usr/lib/systemd/system/nfs-server.service; enabled; preset: enabled)
    Drop-In: /run/systemd/generator/nfs-server.service.d
             └─order-with-mounts.conf
     Active: active (exited) since Tue 2026-11-24 18:19:06 UTC; 3h 45min ago
    Process: 265962 ExecStartPre=/usr/sbin/exportfs -r (code=exited, status=0/SUCCESS)
    Process: 265964 ExecStart=/usr/sbin/rpc.nfsd (code=exited, status=0/SUCCESS)
   Main PID: 265964 (code=exited, status=0/SUCCESS)
        CPU: 14ms
```

O esperado é `active (exited)`. O "exited" assusta, mas é normal: o serviço só configura o `nfsd` do kernel e termina. Quem atende de verdade fica rodando dentro do kernel.

## 2. Configurando os clientes

Em derivados de Debian (Ubuntu, Pop!_OS, Ubuntu no WSL):

```bash
sudo apt install -y nfs-common && mkdir -p ~/shared
```

Em derivados de Red Hat (no meu caso, Oracle Linux):

```bash
sudo dnf install -y nfs-utils && mkdir -p ~/shared
```

Adicione em `/etc/fstab`, trocando `IP_DO_SERVIDOR` e `SEU_USER`:

```text
IP_DO_SERVIDOR:/srv/nfs/shared  /home/SEU_USER/shared  nfs4  defaults,_netdev,nofail,x-systemd.automount,x-systemd.idle-timeout=600  0 0
```

| Opção | O que faz |
|---|---|
| `_netdev` | Avisa que depende de rede, então só monta depois que a rede subir |
| `nofail` | Se o servidor estiver fora, o boot continua normalmente |
| `x-systemd.automount` | Só monta quando você acessa a pasta pela primeira vez |
| `x-systemd.idle-timeout=600` | Desmonta depois de 10 minutos sem uso |

Recarregue o systemd e faça a montagem:

```bash
sudo systemctl daemon-reload && sudo mount -a
```

> 💡 O `mount -a` monta a pasta direto, sem passar pelo automount, mas funciona normalmente. A partir do próximo reboot, o automount assume. Se quiser ativá-lo já, use `sudo systemctl restart remote-fs.target` no lugar do `mount -a`.

### No WSL

Confira se o systemd está habilitado em `/etc/wsl.conf`:

```ini
[boot]
systemd=true
```

Se precisou adicionar, rode `wsl --shutdown` no PowerShell do Windows e abra a distro de novo. Depois, adicione a linha no `fstab` com uma opção a mais, o `noresvport`, e repita o passo anterior:

```text
IP_DO_SERVIDOR:/srv/nfs/shared  /home/SEU_USER/shared  nfs4  defaults,_netdev,nofail,noresvport,x-systemd.automount,x-systemd.idle-timeout=600  0 0
```

> ⚠️ O `noresvport` exige um ajuste no servidor também. Explico o porquê (e o perrengue até chegar nele) na seção **Resolução de problemas**, mais abaixo.

## 3. Testando

Em um PC:

```bash
echo "teste de $(hostname)" >> ~/shared/teste.txt
```

Em outro:

```bash
cat ~/shared/teste.txt
```

Se aparecer o texto com o hostname do primeiro PC, está pronto.

## Resolução de problemas

Caso o texto não apareça no outro PC, vale verificar alguns pontos. No meu caso, os PCs com Linux nativo funcionaram lindamente, mas as distros no WSL tiveram um probleminha, e os arquivos não apareceram.

### A pasta está montada?

No cliente, rode:

```bash
findmnt -T ~/shared
```

| O que aparece em SOURCE / FSTYPE | Diagnóstico |
|---|---|
| `10.220.0.19:/srv/nfs/shared` e `nfs4` | ✅ Montado. O problema está em outro lugar (permissão, firewall) |
| `systemd-1` e `autofs` | ⏳ O automount está armado, mas a montagem ainda não disparou. Rode `ls ~/shared` e repita o `findmnt` |
| Seu disco local (`/dev/sda2`, `ext4` etc.) | ❌ Não está montado. Os arquivos foram gravados no disco local |

Uma forma alternativa de ver:

```bash
df -h ~/shared
```

### Não montou? Descubra o porquê

Primeiro, tente montar na mão para ver o erro que o `nofail` escondeu:

```bash
sudo mount -v ~/shared
```

No meu caso, o problema era **timeout**: o comando ficava parado e, depois de um tempo, desistia.

Conferi se o servidor estava escutando na porta 2049:

```bash
sudo ss -tlnp | grep 2049
```

Depois, fiz um telnet a partir do cliente e conectou, ou seja, descartei problema na porta do servidor:

```bash
telnet 10.220.0.19 2049
```

> 🤓 **Curiosidade:** dias depois, achei esta linha no `dmesg` do servidor: `svc: svc_tcp_read_marker nfsd RPC fragment too large: 2146762749`. Em hexadecimal, esse número é `FF F4 FF FD`, a sequência que o telnet envia quando você aperta Ctrl+C. O servidor NFS esperava uma mensagem RPC e recebeu "comandos de telnet". É inofensivo, mas é o tipo de rastro que você mesmo deixa e depois fica caçando.

Em seguida, fiz mais dois testes: um saindo por uma porta alta (o padrão de qualquer programa) e outro forçando a saída pela porta 900, para imitar o cliente NFS do kernel, que por padrão usa uma porta abaixo de 1024 (as "portas privilegiadas", que só o root pode usar):

```bash
nc -zv -w 5 10.220.0.19 2049                # sai por uma porta alta
sudo nc -zv -w 5 -p 900 10.220.0.19 2049    # força a saída pela porta 900
```

E fiquei escutando do lado do servidor:

```bash
sudo tcpdump -ni any host 10.220.0.29 and port 2049
```

(`10.220.0.29` é o IP do PC com Windows. Meu WSL está no modo de rede *mirrored*, então divide o IP com o Windows. Para conferir o seu, rode `wslinfo --networking-mode`.)

### A solução

Desconfiei da porta de origem: o cliente NFS do kernel sai por uma porta privilegiada, e o WSL passa pela pilha de rede do Windows. Então fiz **dois ajustes de uma vez**.

No cliente (WSL), adicionei `noresvport` no `/etc/fstab`, para o cliente sair por uma porta alta:

```text
10.220.0.19:/srv/nfs/shared  /home/jefferson/shared  nfs4  defaults,_netdev,nofail,noresvport,x-systemd.automount,x-systemd.idle-timeout=600  0 0
```

No servidor, adicionei `insecure` no `/etc/exports`, para aceitar conexões vindas de portas altas. Por padrão, o servidor usa a opção `secure` e só aceita portas abaixo de 1024:

```text
/srv/nfs/shared  10.220.0.0/24(rw,sync,no_subtree_check,all_squash,anonuid=1000,anongid=1000,insecure)
```

| Pedaço | Onde | O que faz |
|---|---|---|
| `noresvport` | Cliente (`fstab`) | O cliente sai por uma porta alta (acima de 1024) em vez de uma privilegiada |
| `insecure` | Servidor (`exports`) | O servidor aceita clientes vindos de portas altas |

Apliquei no servidor:

```bash
sudo exportfs -ra && sudo exportfs -v
```

E montei novamente no cliente:

```bash
sudo mount -v ~/shared && findmnt -T ~/shared
```

Funcionou: o `findmnt` passou a mostrar `10.220.0.19:/srv/nfs/shared` e `nfs4`.

### Mas qual dos dois resolveu?

Mudei duas coisas juntas, então não dava para saber. Fica a lição de troubleshooting que eu mesmo ignorei: **mude uma coisa por vez**.

Para escrever este post, voltei e testei separado. Tirei o `insecure` do servidor e mantive o `noresvport` no cliente. O resultado foi um erro **imediato**:

```text
mount.nfs4: mount(2): Operation not permitted
```

Repare que o sintoma é outro. E isso responde a pergunta:

| Sintoma | Causa provável |
|---|---|
| `Operation not permitted`, na hora | Cliente saindo por porta alta e servidor sem `insecure` |
| Timeout (o comando trava e desiste) | A conexão nem se completa. No meu caso, era o cliente saindo por porta privilegiada a partir do WSL |

Ou seja:

1. O problema original (timeout) **não era** o servidor recusando porta alta, porque isso dá erro na hora.
2. Quem resolveu de fato foi o **`noresvport`**, que tirou o cliente da porta privilegiada.
3. O **`insecure`** virou necessário **por causa** do `noresvport`. Um não funciona sem o outro.

Por que a porta privilegiada dava timeout eu ainda não sei. O curioso é que o `nc` forçando a porta 900 conecta normalmente. Minha suspeita é que, no modo mirrored, o Linux e o Windows dividem as mesmas portas, e o cliente NFS do kernel (que escolhe sozinho uma porta entre 665 e 1023) acabava pegando uma que o Windows usava. Não consegui confirmar (inclusive, sou bem ruinzinho em troubleshooting com Windows). Se você souber, me conta nos comentários!

> 💡 Os PCs com Linux nativo não precisam do `noresvport`. Mas, como o `insecure` vale para a sub-rede inteira, eles continuam funcionando normalmente com porta privilegiada.

## Limitações (leia antes de copiar)

- **Sem autenticação:** qualquer dispositivo da sub-rede consegue montar, ler e escrever na pasta. Lembre disso antes de colocar aquele `pass.txt` lá.
- **Sem redundância nem backup:** se o disco do servidor morrer, os arquivos vão junto.
- **Edição simultânea:** o NFS resolve o problema de ter várias cópias espalhadas, mas, se você abrir o mesmo arquivo em dois PCs e salvar nos dois, vale o último a salvar.
- **Depende do servidor ligado:** se ele cair, a pasta some nos clientes (o `nofail` só garante que o boot não trave).

## Conclusão

Se você quer um servidorzinho para centralizar seus arquivos localmente e acessá-los de qualquer PC da sua casa, essa é uma solução simples, barata e rápida de implementar.

Mais para frente, vou subir uma VPN (OpenVPN) em um container nesse servidor, para acessar esses mesmos arquivos de fora de casa. Também penso em brincar com autenticação, apenas como "laboratório".

Não recomendo essa solução para quem precisa de segurança. Do jeito que fiz, não existe redundância, backup nem nenhum nível de proteção. Então, não faça isso se quiser guardar dados sensíveis ou que não possam ser perdidos.

Para mim, foi só uma facilidade para organizar minhas pastinhas de trabalho e estudo em um lugar só e acessá-las de qualquer máquina da casa. Fora isso, esses labs são meu hobby, então, para mim, é diversão ficar testando coisas e quebrando meus sistemas.

E é isso. Te vejo no próximo post!
