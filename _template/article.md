---
title: Provisionando uma VM na AWS com Terraform e Ansible
published: false
description: Do zero ao servidor configurado em poucos comandos
tags: terraform, ansible, devops, aws
cover_image: https://url-da-imagem.png
series: Infra como Código na prática
canonical_url:
---

## Introdução

Contexto curto: o problema e o que o leitor vai aprender.

## Pré-requisitos

- Terraform >= 1.6
- Ansible >= 2.15
- Conta AWS configurada

## 1. Criando a infraestrutura

Explique antes do código, não depois.

```hcl
resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = "t3.micro"

  tags = {
    Name = "web-server"
  }
}
```

## 2. Configurando com Ansible

{% raw %}
```yaml
- name: Instalar nginx
  hosts: web
  become: true
  tasks:
    - name: Instala pacote
      ansible.builtin.apt:
        name: "{{ pkg_name }}"
        state: present
```
{% endraw %}

## 3. Executando

```bash
terraform init
terraform apply -auto-approve
ansible-playbook -i inventory.ini site.yml
```

## Conclusão

Resumo + próximos passos + link do repositório.
