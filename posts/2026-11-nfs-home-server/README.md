# Cansei de procurar arquivos em 4 PCs: montei um servidor NFS em casa

| | |
|---|---|
| Status | rascunho (`published: false`) |
| Série | Homelab na prática |
| dev.to | — |
| Medium | — |
| LinkedIn | — |
| Instagram | — |

## Imagens

| Arquivo | Tamanho | Gerado por | Template de origem |
|---|---|---|---|
| `images/cover/cover-devto.png` | 1000×420 | `images/cover/cover.py` | — (este post deu origem a `brand/visual-identity/templates/cover.py`) |
| `images/cover/cover-medium.png` | 1400×788 | `images/cover/cover.py` | idem |
| `images/carousel/slide-01..09.png` | 1080×1350 | `images/carousel/carousel.py` | — (deu origem a `brand/visual-identity/templates/carousel.py`) |
| `images/carousel/carousel.pdf` | 9 páginas | `images/carousel/carousel.py` | idem |

### Como foram criadas

- **Capa**: prompt `$ mount -t nfs4   # TCP 2049`, título em 2 linhas ("Cansei de procurar / arquivos em 4 PCs"),
  diagrama do servidor exportando `/srv/nfs/shared` para os PCs, logo reduzida no canto inferior direito.
- **Carrossel** (9 slides): roteiro padrão do manual: gancho → problema → o que descartei → a ideia (diagrama) →
  configuração do servidor/cliente → perrengue do WSL → lição → chamada final com logo extensa.
- **Diferenças em relação ao template**: nenhuma. Os templates são cópia destes scripts.
- **Ajustes manuais**: nenhum.

### Regerar

```bash
# da raiz do repo articles/
~/.venvs/arte/bin/python posts/2026-11-nfs-home-server/images/cover/cover.py
~/.venvs/arte/bin/python posts/2026-11-nfs-home-server/images/carousel/carousel.py
```

Conferido em 2026-11-24, depois da reorganização: os scripts geram imagens idênticas às publicadas.

## Checklist

- [ ] Checklist do manual (`brand/visual-identity/README.md`) conferido
- [ ] `cover_image` do front matter preenchido após subir a capa
- [ ] Legendas revisadas em `captions.md`
