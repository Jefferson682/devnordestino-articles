# <título do artigo>

| | |
|---|---|
| Status | rascunho · revisão · publicado |
| Série | <série do front matter> |
| dev.to | <link> |
| Medium | <link> |
| LinkedIn | <link do post> — data |
| Instagram | <link do post> — data |

## Imagens

| Arquivo | Tamanho | Gerado por | Template de origem |
|---|---|---|---|
| `images/cover/cover-devto.png` | 1000×420 | `images/cover/cover.py` | `brand/visual-identity/templates/cover.py` |
| `images/cover/cover-medium.png` | 1400×788 | `images/cover/cover.py` | idem |
| `images/carousel/slide-01..NN.png` | 1080×1350 | `images/carousel/carousel.py` | `brand/visual-identity/templates/carousel.py` |
| `images/carousel/carousel.pdf` | — | `images/carousel/carousel.py` | idem |

### Como foram criadas

- **Capa**: <prompt do topo, título, subtítulo com a palavra verde, tags, o que o diagrama mostra>
- **Carrossel**: <roteiro slide a slide: 01 gancho, 02 problema, ...>
- **Diferenças em relação ao template**: <funções novas, cores, layout fora do padrão>
- **Ajustes manuais** (fora do script): <nenhum / descreva>

### Regerar

```bash
# da raiz do repo articles/
~/.venvs/arte/bin/python posts/<pasta>/images/cover/cover.py
~/.venvs/arte/bin/python posts/<pasta>/images/carousel/carousel.py
```

## Checklist

- [ ] Checklist do manual (`brand/visual-identity/README.md`) conferido
- [ ] `cover_image` do front matter preenchido após subir a capa
- [ ] Legendas revisadas em `captions.md`
