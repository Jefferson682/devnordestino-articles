# devnordestino — logo

Símbolo: `< mandacaru >`, traço único com pontas arredondadas.
Texto: Ubuntu Mono Bold ("dev" neutro + "nordestino" em laranja), convertido em curvas.
Assinatura: Ubuntu Regular.

## Versões

| Arquivo | Uso |
|---|---|
| `icon-*` | Só o símbolo: avatar, marca d'água, espaços pequenos |
| `icon-tile` / `favicon/` | Símbolo em bloco escuro: favicon, ícone de app, avatar redondo |
| `short-*` | Símbolo + nome: header do site, rodapé, capas |
| `full-*` | Símbolo + nome + assinatura: "sobre", apresentações, cartão |

`-light` = para fundo claro · `-dark` = para fundo escuro.
Use o SVG sempre que puder; o PNG é para onde SVG não é aceito.

## Cores

| | Fundo claro | Fundo escuro |
|---|---|---|
| Laranja (símbolo, "nordestino") | `#D9622B` | `#F59E54` |
| Texto ("dev") | `#1F2937` | `#F3F4F6` |
| Assinatura | `#6B7280` | `#9CA3AF` |
| Fundo de referência | `#FFFFFF` | `#111827` |

## Regerar

```bash
python3 -m venv --system-site-packages .venv && .venv/bin/pip install cairosvg
.venv/bin/python source/generate.py .
```

Precisa das fontes Ubuntu instaladas (`fonts-ubuntu`) e do `fontTools`.
