import sys
from PIL import Image, ImageDraw, ImageFont

F = "/usr/share/fonts/truetype/ubuntu/"
from pathlib import Path

# raiz do repo de artigos = primeira pasta acima que contém brand/
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "brand").is_dir())
LOGO_DIR = str(ROOT / "brand/logo/png") + "/"
LOGO = LOGO_DIR + "devnordestino-short-dark.png"
BG, BG2 = (15, 20, 30), (24, 32, 46)
FG, MUTED = (236, 240, 245), (140, 152, 170)
ACCENT, ACCENT2 = (74, 222, 128), (56, 189, 248)
LINE = (60, 74, 96)


def font(name, size):
    return ImageFont.truetype(F + name, int(size))


def render(W, H, out, title_size, ss=2):
    w, h = W * ss, H * ss
    u = h / 420  # unidade relativa à altura do dev.to
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)

    # gradiente vertical sutil
    for y in range(h):
        t = y / h
        c = tuple(int(BG[i] + (BG2[i] - BG[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)

    # grade de pontos ao fundo
    step = int(28 * u)
    for x in range(0, w, step):
        for y in range(0, h, step):
            d.ellipse([x - u, y - u, x + u, y + u], fill=(32, 42, 58))

    pad = 48 * u
    # ---------- texto à esquerda ----------
    mono = font("UbuntuMono-R.ttf", 18 * u)
    d.text((pad, pad), "$ mount -t nfs4   # TCP 2049", font=mono, fill=ACCENT)

    tf = font("Ubuntu-B.ttf", title_size * u)
    lines = ["Cansei de procurar", "arquivos em 4 PCs"]
    y = pad + 40 * u
    for ln in lines:
        d.text((pad, y), ln, font=tf, fill=FG)
        y += title_size * u * 1.15
    sub = font("Ubuntu-M.ttf", title_size * 0.62 * u)
    y += 6 * u
    d.text((pad, y), "montei um servidor ", font=sub, fill=MUTED)
    x2 = pad + d.textlength("montei um servidor ", font=sub)
    d.text((x2, y), "NFS", font=sub, fill=ACCENT)
    x3 = x2 + d.textlength("NFS", font=sub)
    d.text((x3, y), " em casa", font=sub, fill=MUTED)

    # tags
    tag = font("UbuntuMono-B.ttf", 15 * u)
    tx, ty = pad, h - pad - 26 * u
    for t in ["#linux", "#nfs", "#homelab", "#devops"]:
        tw = d.textlength(t, font=tag)
        d.rounded_rectangle([tx, ty, tx + tw + 20 * u, ty + 26 * u], radius=6 * u,
                            outline=LINE, width=max(1, int(1.5 * u)), fill=BG2)
        d.text((tx + 10 * u, ty + 4 * u), t, font=tag, fill=ACCENT2)
        tx += tw + 30 * u

    # ---------- diagrama à direita ----------
    cx = w - (w * 0.22)
    cy = h * 0.46
    sw, sh = 150 * u, 74 * u
    clients = [("notebook", -1, -1), ("desktop", 1, -1), ("lab", -1, 1), ("WSL", 1, 1)]
    dx, dy = min(w * 0.13, 150 * u), 112 * u
    cw, ch = 104 * u, 44 * u
    lw = max(2, int(2 * u))

    pts = [(cx + sx * dx, cy + sy * dy) for _, sx, sy in clients]
    for px, py in pts:  # linhas tracejadas
        n = 14
        for i in range(n):
            if i % 2:
                continue
            a, b = i / n, (i + 1) / n
            d.line([(cx + (px - cx) * a, cy + (py - cy) * a),
                    (cx + (px - cx) * b, cy + (py - cy) * b)], fill=ACCENT2, width=lw)

    # servidor
    d.rounded_rectangle([cx - sw / 2, cy - sh / 2, cx + sw / 2, cy + sh / 2],
                        radius=10 * u, fill=(20, 40, 32), outline=ACCENT, width=lw)
    for i in range(3):  # "leds"
        d.ellipse([cx - sw / 2 + 14 * u, cy - 22 * u + i * 16 * u,
                   cx - sw / 2 + 22 * u, cy - 14 * u + i * 16 * u], fill=ACCENT)
    sf = font("Ubuntu-B.ttf", 18 * u)
    sm = font("UbuntuMono-R.ttf", 13 * u)
    d.text((cx + 10 * u, cy - 12 * u), "servidor", font=sf, fill=FG, anchor="mm")
    d.text((cx + 10 * u, cy + 14 * u), "/srv/nfs/shared", font=sm, fill=ACCENT, anchor="mm")

    cf = font("UbuntuMono-B.ttf", 15 * u)
    for (name, _, _), (px, py) in zip(clients, pts):
        d.rounded_rectangle([px - cw / 2, py - ch / 2, px + cw / 2, py + ch / 2],
                            radius=8 * u, fill=BG2, outline=LINE, width=lw)
        d.text((px, py), name, font=cf, fill=FG, anchor="mm")

    # logo no canto inferior direito, alinhada com as tags
    logo = Image.open(LOGO).convert("RGBA")
    lh = int(32 * u)
    logo = logo.resize((int(logo.width * lh / logo.height), lh), Image.LANCZOS)
    img.paste(logo, (int(w - pad - logo.width), int(ty + 13 * u - lh / 2)), logo)  # centro alinhado às tags

    img = img.resize((W, H), Image.LANCZOS)
    img.save(out, optimize=True)
    print(out, img.size)


out_dir = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent)
render(1000, 420, f"{out_dir}/cover-devto.png", title_size=44)
render(1400, 788, f"{out_dir}/cover-medium.png", title_size=40)
