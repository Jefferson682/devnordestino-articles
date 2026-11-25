# <título do artigo>

![Capa: <título>](images/cover/cover-medium.png)

> <description do front matter>

📖 **Ler:** [no dev.to](<link>) · [aqui no GitHub](article.md)

Publicado em DD/MM/AAAA · Série **<série>** · `tag1` `tag2` `tag3`

## Carrossel

Resumo do artigo em N slides ([PDF](images/carousel/carousel.pdf)).

<p>
  <img src="images/carousel/slide-01.png" width="32%" alt="Slide 1" />
  <img src="images/carousel/slide-02.png" width="32%" alt="Slide 2" />
  <img src="images/carousel/slide-03.png" width="32%" alt="Slide 3" />
</p>

---

## Bastidores

Como as peças deste post foram produzidas.

| | |
|---|---|
| Status | rascunho · revisão · publicado |
| dev.to | <link> (canonical) |
| Medium | <link> |
| LinkedIn | <link do post> |
| Instagram | <link do post> |

### Imagens

| Arquivo | Tamanho | Gerado por | Template de origem |
|---|---|---|---|
| `images/cover/cover-devto.png` | 1000×420 | `images/cover/cover.py` | `brand/visual-identity/templates/cover.py` |
| `images/cover/cover-medium.png` | 1400×788 | `images/cover/cover.py` | idem |
| `images/carousel/slide-01..NN.png` | 1080×1350 | `images/carousel/carousel.py` | `brand/visual-identity/templates/carousel.py` |
| `images/carousel/carousel.pdf` | — | `images/carousel/carousel.py` | idem |

- **Capa**: <prompt do topo, título, subtítulo com a palavra verde, tags, o que o diagrama mostra>
- **Carrossel**: <roteiro slide a slide: 01 gancho, 02 problema, ...>
- **Diferenças em relação ao template**: <funções novas, cores, layout fora do padrão>
- **Ajustes manuais** (fora do script): <nenhum / descreva>
- Legendas usadas no LinkedIn e no Instagram: [`captions.md`](captions.md).

### Regerar

```bash
# da raiz do repositório
~/.venvs/arte/bin/python posts/<pasta>/images/cover/cover.py
~/.venvs/arte/bin/python posts/<pasta>/images/carousel/carousel.py
```
