"""Gera a identidade dev nordestino: símbolo, versão reduzida e extensa, fundo claro e escuro."""
import os, sys
import cairosvg
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
FONTS = "/usr/share/fonts/truetype/ubuntu/"
BYLINE = "by Jefferson do Vale"

THEMES = {
    # fundo claro: texto escuro, laranja terracota
    "light": dict(accent="#D9622B", text="#1F2937", muted="#6B7280", bg="#FFFFFF"),
    # fundo escuro: texto claro, laranja mais aberto para manter contraste
    "dark": dict(accent="#F59E54", text="#F3F4F6", muted="#9CA3AF", bg="#111827"),
}

# ---------------------------------------------------------------- símbolo
# Grade 64x64, traço único, pontas arredondadas: < mandacaru >
SYMBOL_PATHS = [
    "M15 20 L5 32 L15 44",                      # <
    "M49 20 L59 32 L49 44",                     # >
    "M32 54 L32 12",                            # tronco
    "M32 39 L26 39 Q21 39 21 34 L21 26",        # braço esquerdo
    "M32 31 L38 31 Q43 31 43 26 L43 18",        # braço direito
]
STROKE = 5


def symbol(color, x=0, y=0, size=64):
    s = size / 64
    paths = "".join(f'<path d="{d}"/>' for d in SYMBOL_PATHS)
    return (f'<g transform="translate({x:.2f} {y:.2f}) scale({s:.4f})" fill="none" stroke="{color}" '
            f'stroke-width="{STROKE}" stroke-linecap="round" stroke-linejoin="round">{paths}</g>')


# ---------------------------------------------------------------- texto em curvas
class Face:
    def __init__(self, file):
        self.f = TTFont(FONTS + file)
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.cap = self.f["OS/2"].sCapHeight or int(self.upm * 0.7)
        self.xh = self.f["OS/2"].sxHeight or int(self.upm * 0.5)

    def run(self, text, x, baseline, size, color, tracking=0.0):
        """Devolve (svg, largura) de um texto como paths. tracking em em."""
        s = size / self.upm
        parts, cx = [], 0.0
        for ch in text:
            g = self.cmap[ord(ch)]
            pen = SVGPathPen(self.gs)
            self.gs[g].draw(pen)
            d = pen.getCommands()
            if d:
                parts.append(f'<path transform="translate({x + cx * s:.2f} {baseline:.2f}) '
                             f'scale({s:.5f} {-s:.5f})" d="{d}"/>')
            cx += self.gs[g].width + tracking * self.upm
        width = (cx - tracking * self.upm) * s
        return f'<g fill="{color}">{"".join(parts)}</g>', width

    def width(self, text, size, tracking=0.0):
        return self.run(text, 0, 0, size, "#000", tracking)[1]


MONO = Face("UbuntuMono-B.ttf")
SANS = Face("Ubuntu-R.ttf")


def wordmark(t, x, baseline, size):
    a, wa = MONO.run("dev", x, baseline, size, t["text"])
    b, wb = MONO.run("nordestino", x + wa, baseline, size, t["accent"])
    return a + b, wa + wb


def svg(w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
            f'viewBox="0 0 {w:.2f} {h:.2f}">{rect}{body}</svg>\n')


# ---------------------------------------------------------------- layouts
def icon(t):
    pad = 4
    return svg(64 + 2 * pad, 64 + 2 * pad, symbol(t["accent"], pad, pad))


def icon_tile():
    """Ícone em bloco (favicon, avatar): funciona em qualquer fundo."""
    t = THEMES["dark"]
    body = (f'<rect width="96" height="96" rx="22" fill="{t["bg"]}"/>'
            + symbol(t["accent"], 16, 16))
    return svg(96, 96, body)


def reduzida(t):
    sym, size, gap, pad = 64, 40, 18, 8
    ww = MONO.width("devnordestino", size)
    xh = MONO.xh * size / MONO.upm
    h = sym + 2 * pad
    baseline = pad + sym / 2 + xh / 2           # centraliza a altura-x com o símbolo
    w = pad + sym + gap + ww + pad
    wm, _ = wordmark(t, pad + sym + gap, baseline, size)
    return svg(w, h, symbol(t["accent"], pad, pad, sym) + wm)


def extensa(t):
    sym, size, bsize, gap, pad = 96, 46, 19, 22, 10
    ww = MONO.width("devnordestino", size)
    cap = MONO.cap * size / MONO.upm
    bcap = SANS.cap * bsize / SANS.upm
    line_gap = 14
    block = cap + line_gap + bcap               # altura do bloco de texto
    top = pad + (sym - block) / 2
    base1 = top + cap
    base2 = base1 + line_gap + bcap
    tx = pad + sym + gap
    wm, _ = wordmark(t, tx, base1, size)
    by, bw = SANS.run(BYLINE, tx + 2, base2, bsize, t["muted"], tracking=0.02)
    w = tx + max(ww, bw) + pad
    return svg(w, sym + 2 * pad, symbol(t["accent"], pad, pad, sym) + wm + by)


# ---------------------------------------------------------------- saída
def save(name, content, png_width):
    os.makedirs(f"{OUT}/svg", exist_ok=True)
    os.makedirs(f"{OUT}/png", exist_ok=True)
    with open(f"{OUT}/svg/{name}.svg", "w") as f:
        f.write(content)
    cairosvg.svg2png(bytestring=content.encode(), write_to=f"{OUT}/png/{name}.png",
                     output_width=png_width)


for theme, t in THEMES.items():
    save(f"devnordestino-icon-{theme}", icon(t), 512)
    save(f"devnordestino-short-{theme}", reduzida(t), 1200)
    save(f"devnordestino-full-{theme}", extensa(t), 1600)

tile = icon_tile()
save("devnordestino-icon-tile", tile, 512)
os.makedirs(f"{OUT}/favicon", exist_ok=True)
with open(f"{OUT}/favicon/favicon.svg", "w") as f:
    f.write(tile)
for px, name in [(32, "favicon-32.png"), (180, "apple-touch-icon.png"), (512, "icon-512.png")]:
    cairosvg.svg2png(bytestring=tile.encode(), write_to=f"{OUT}/favicon/{name}", output_width=px)

# ---------------------------------------------------------------- prancha de apresentação
W, PAD = 1800, 70
rows = [("icon", 200), ("short", 600), ("full", 740)]
panels = []
for theme, t in THEMES.items():
    imgs = [Image.open(f"{OUT}/png/devnordestino-{k}-{theme}.png").convert("RGBA") for k, _ in rows]
    imgs = [im.resize((wd, int(im.height * wd / im.width)), Image.LANCZOS) for im, (_, wd) in zip(imgs, rows)]
    tile_im = Image.open(f"{OUT}/png/devnordestino-icon-tile.png").convert("RGBA").resize((150, 150), Image.LANCZOS)
    h = PAD * 2 + 40 + max(imgs[0].height, tile_im.height) + 60 + imgs[1].height + 60 + imgs[2].height
    p = Image.new("RGBA", (W // 2, h), t["bg"])
    d = ImageDraw.Draw(p)
    lab = ImageFont.truetype(FONTS + "UbuntuMono-R.ttf", 22)
    d.text((PAD, PAD - 20), f"fundo {'claro' if theme == 'light' else 'escuro'}", font=lab, fill=t["muted"])
    y = PAD + 40
    p.alpha_composite(imgs[0], (PAD, y))
    p.alpha_composite(tile_im, (PAD + imgs[0].width + 50, y + (imgs[0].height - 150) // 2))
    y += max(imgs[0].height, 150) + 60
    p.alpha_composite(imgs[1], (PAD, y)); y += imgs[1].height + 60
    p.alpha_composite(imgs[2], (PAD, y))
    panels.append(p)
H = max(p.height for p in panels)
sheet = Image.new("RGB", (W, H), "#ffffff")
for i, p in enumerate(panels):
    sheet.paste(p, (i * W // 2, 0))
sheet.save(f"{OUT}/preview.png")
print("ok")
