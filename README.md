# devnordestino · artigos

Artigos técnicos de **Jefferson do Vale** sobre Linux, DevOps, infraestrutura e homelab, escritos ao longo
dos meus estudos. Cada post traz o texto completo, a capa e o carrossel publicados nas redes, além dos
scripts que geram essas imagens. Todos os artigos também estão no [dev.to/jefferson682](https://dev.to/jefferson682).

> Conteúdo em português (pt-BR). Versões em outros idiomas virão depois.

## Posts

| Publicado | Artigo | Série |
|---|---|---|
| 24/11/2026 | [Cansei de procurar arquivos em 4 PCs: montei um servidor NFS em casa](posts/2026-11-nfs-home-server/) · [dev.to](https://dev.to/jefferson682/cansei-de-procurar-arquivos-em-4-pcs-montei-um-servidor-nfs-em-casa-1jh6) | Homelab na prática |

## Estrutura

```
posts/AAAA-MM-<slug>/     # um post por pasta (AAAA-MM = quando comecei a escrever)
├── article.md            # o artigo
├── README.md             # status, links e como cada imagem foi gerada
├── captions.md           # legendas de LinkedIn e Instagram
└── images/
    ├── cover/            # capas (dev.to 1000×420, Medium 1400×788) + script
    └── carousel/         # carrossel 1080×1350 em PNG e PDF + script
brand/                    # logo e manual de identidade visual
_template/                # esqueleto de um post novo
```

## Gerando as imagens

Requisitos: Python 3, Pillow, cairosvg e as fontes Ubuntu (`fonts-ubuntu`).

```bash
python3 -m venv --system-site-packages ~/.venvs/arte && ~/.venvs/arte/bin/pip install pillow cairosvg
~/.venvs/arte/bin/python posts/<pasta>/images/carousel/carousel.py
```

Os detalhes de layout, cores e tamanhos estão no [manual de identidade visual](brand/visual-identity/README.md).

## Licença

| O quê | Licença |
|---|---|
| Textos e imagens dos posts | [CC BY-NC 4.0](LICENSE-CONTENT.md): pode usar e adaptar **citando a autoria**, sem fins comerciais |
| Scripts (`*.py`) | [MIT](LICENSE): uso livre |
| Marca devnordestino (logo, nome) | [Todos os direitos reservados](brand/LICENSE.md) |
