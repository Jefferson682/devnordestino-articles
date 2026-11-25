"""Carrossel 1080x1350 (4:5) do post de NFS: serve para Instagram e LinkedIn.

Uso: python3 carousel.py [pasta-de-saida]   (padrão: a pasta do script)
Gera slide-01.png ... slide-NN.png e carousel.pdf (LinkedIn só faz "arrastar para o lado" com PDF).
"""
import sys
from PIL import Image, ImageDraw, ImageFont, JpegImagePlugin, PdfImagePlugin  # noqa: F401 (registra JPEG/PDF)

F = "/usr/share/fonts/truetype/ubuntu/"
from pathlib import Path

# raiz do repo de artigos = primeira pasta acima que contém brand/
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "brand").is_dir())
LOGO_DIR = str(ROOT / "brand/logo/png") + "/"
OUT = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent)
LOGO = LOGO_DIR + "devnordestino-short-dark.png"
ICON = LOGO_DIR + "devnordestino-icon-dark.png"

W, H, SS = 1080, 1350, 2          # tamanho final e supersampling
BG, BG2 = (15, 20, 30), (24, 32, 46)
FG, MUTED, DIM = (236, 240, 245), (140, 152, 170), (112, 124, 145)
GREEN, BLUE, RED = (74, 222, 128), (56, 189, 248), (248, 113, 113)
LINE, CODE_BG = (60, 74, 96), (11, 15, 23)
PAD = 90


def f(name, size):
    path = name if name.startswith("/") else F + name
    return ImageFont.truetype(path, int(size * SS))


ARROW = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


BOLD, MED, REG = "Ubuntu-B.ttf", "Ubuntu-M.ttf", "Ubuntu-R.ttf"
MONO, MONOB = "UbuntuMono-R.ttf", "UbuntuMono-B.ttf"


class Slide:
    def __init__(self):
        self.img = Image.new("RGB", (W * SS, H * SS), BG)
        self.d = ImageDraw.Draw(self.img)
        for y in range(H * SS):
            t = y / (H * SS)
            self.d.line([(0, y), (W * SS, y)], fill=tuple(int(BG[i] + (BG2[i] - BG[i]) * t) for i in range(3)))
        step = 30 * SS
        for x in range(0, W * SS, step):
            for y in range(0, H * SS, step):
                self.d.ellipse([x - SS, y - SS, x + SS, y + SS], fill=(30, 40, 56))

    # coordenadas sempre em px do slide final; multiplico por SS aqui
    def text(self, x, y, s, font, fill, anchor="la"):
        self.d.text((x * SS, y * SS), s, font=font, fill=fill, anchor=anchor)

    def tw(self, s, font):
        return self.d.textlength(s, font=font) / SS

    def rich(self, x, y, parts, font):
        """Uma linha com trechos de cores diferentes: [(texto, cor), ...]"""
        for s, c in parts:
            self.text(x, y, s, font, c)
            x += self.tw(s, font)

    def wrap(self, x, y, s, font, fill, width, lh):
        words, line = s.split(), ""
        for w in words:
            test = (line + " " + w).strip()
            if self.tw(test, font) > width and line:
                self.text(x, y, line, font, fill); y += lh; line = w
            else:
                line = test
        if line:
            self.text(x, y, line, font, fill); y += lh
        return y

    def box(self, x0, y0, x1, y1, fill=BG2, outline=LINE, r=16, width=2):
        self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=r * SS,
                                 fill=fill, outline=outline, width=width * SS)

    def code(self, x, y, w, lines, size=30):
        font, lh = f(MONO, size), size * 1.45
        h = sum(0.5 if l == "" else 1 for l in lines) * lh + 48
        self.box(x, y, x + w, y + h, fill=CODE_BG, outline=LINE)
        for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
            cx = x + 28 + i * 24
            self.d.ellipse([(cx - 6) * SS, (y + 22 - 6) * SS, (cx + 6) * SS, (y + 22 + 6) * SS], fill=c)
        yy = y + 46
        for ln in lines:
            if ln == "":
                yy += lh * 0.5
                continue
            if isinstance(ln, str):
                col = DIM if ln.lstrip().startswith("#") else FG
                ln = [("$ ", GREEN), (ln, col)] if not ln.startswith(("#", " ")) else [(ln, col)]
            self.rich(x + 28, yy, ln, font)
            yy += lh
        return y + h

    def mark(self, x, y, ok, size=34):
        c = GREEN if ok else RED
        s, w = size * SS, 5 * SS
        X, Y = x * SS, y * SS
        if ok:
            self.d.line([(X, Y + s * .55), (X + s * .38, Y + s * .9), (X + s, Y + s * .1)], fill=c, width=w, joint="curve")
        else:
            self.d.line([(X + s * .1, Y + s * .1), (X + s * .9, Y + s * .9)], fill=c, width=w)
            self.d.line([(X + s * .9, Y + s * .1), (X + s * .1, Y + s * .9)], fill=c, width=w)

    def diagram(self, cx, cy, scale=1.0, labels=("notebook", "desktop", "lab", "WSL")):
        u = scale
        dx, dy, cw, ch, sw, sh = 250 * u, 200 * u, 190 * u, 76 * u, 280 * u, 130 * u
        pos = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        for sx, sy in pos:
            px, py = cx + sx * dx, cy + sy * dy
            n = 16
            for i in range(0, n, 2):
                a, b = i / n, (i + 1) / n
                self.d.line([((cx + (px - cx) * a) * SS, (cy + (py - cy) * a) * SS),
                             ((cx + (px - cx) * b) * SS, (cy + (py - cy) * b) * SS)], fill=BLUE, width=int(4 * u * SS))
        self.box(cx - sw / 2, cy - sh / 2, cx + sw / 2, cy + sh / 2, fill=(20, 40, 32), outline=GREEN, r=18 * u, width=3)
        for i in range(3):
            ex, ey = cx - sw / 2 + 30 * u, cy - 34 * u + i * 30 * u
            self.d.ellipse([(ex - 7 * u) * SS, (ey - 7 * u) * SS, (ex + 7 * u) * SS, (ey + 7 * u) * SS], fill=GREEN)
        self.text(cx + 18 * u, cy - 20 * u, "servidor", f(BOLD, 36 * u), FG, "mm")
        self.text(cx + 18 * u, cy + 28 * u, "/srv/nfs/shared", f(MONO, 26 * u), GREEN, "mm")
        for (sx, sy), name in zip(pos, labels):
            px, py = cx + sx * dx, cy + sy * dy
            self.box(px - cw / 2, py - ch / 2, px + cw / 2, py + ch / 2, r=14 * u)
            self.text(px, py, name, f(MONOB, 30 * u), FG, "mm")

    def chrome(self, n, total, last=False):
        # capa: logo reduzida legível | internos: só o ícone | último: logo grande no conteúdo
        if not last:
            src, lh = (LOGO, 64) if n == 1 else (ICON, 64)
            logo = Image.open(src).convert("RGBA")
            logo = logo.resize((int(logo.width * lh * SS / logo.height), lh * SS), Image.LANCZOS)
            self.img.paste(logo, (PAD * SS - (6 * SS if n != 1 else 0), (PAD - lh // 2) * SS), logo)
        self.text(W - PAD, PAD, f"{n:02d}/{total:02d}", f(MONO, 30), MUTED, "rm")
        if not last:
            self.text(W - PAD, H - PAD + 10, "→", f(ARROW, 32), BLUE, "rs")
            self.text(W - PAD - 44, H - PAD + 10, "arrasta", f(MONOB, 32), BLUE, "rs")
        self.text(PAD, H - PAD + 10, "NFS no homelab", f(MONO, 30), MUTED, "ls")

    def save(self, path):
        out = self.img.resize((W, H), Image.LANCZOS)
        out.save(path, optimize=True)
        return out


TOP = 230   # onde começa o conteúdo, abaixo do cabeçalho


def kicker(s, text, y=TOP):
    s.text(PAD, y, text, f(MONOB, 34), GREEN)
    return y + 70


def title(s, lines, y, size=76):
    for ln in lines:
        if isinstance(ln, str):
            ln = [(ln, FG)]
        s.rich(PAD, y, ln, f(BOLD, size))
        y += size * 1.18
    return y


# ------------------------------------------------------------------ slides
def s1(s):
    s.text(PAD, TOP, "$ mount -t nfs4", f(MONO, 32), GREEN)
    y = title(s, ["Cansei de", "procurar arquivos", "em 4 PCs"], TOP + 80, 92)
    s.rich(PAD, y + 20, [("montei um servidor ", MUTED), ("NFS", GREEN), (" em casa", MUTED)], f(MED, 50))
    s.diagram(W / 2, 1000, 0.9)


def s2(s):
    y = kicker(s, "# o problema")
    y = title(s, ["Em qual PC estava", [("aquele ", FG), (".txt", GREEN), (" mesmo?", FG)]], y)
    y += 50
    items = [("notebook", "do trabalho, uma tela só"), ("desktop", "pessoal, virou de trabalho"),
             ("2x ubuntu server", "laboratório: k8s, playbooks"), ("windows + WSL", "testar distros e quebrar tudo")]
    for name, desc in items:
        s.box(PAD, y, W - PAD, y + 124)
        s.text(PAD + 34, y + 26, name, f(MONOB, 34), FG)
        s.text(PAD + 34, y + 72, desc, f(REG, 32), MUTED)
        y += 140
    y += 24
    s.wrap(PAD, y, "Projetos, .env e anotações espalhados. No fim, eu não sabia mais onde estava cada coisa.",
           f(MED, 36), FG, W - 2 * PAD, 50)


def s3(s):
    y = kicker(s, "# o que eu descartei")
    y = title(s, ["Ferramenta pronta", "não faltava..."], y)
    y += 30
    rows = [("Git", "commits lixo e chave SSH em todo lab"),
            ("Drive / Notion", "não rodam num servidor só com vi"),
            ("sshfs", "lento"),
            ("Syncthing", "conflito editando em dois lugares"),
            ("NAS", "bazuca para matar mosca"),
            ("Samba", "mais do que eu precisava")]
    for name, why in rows:
        s.mark(PAD, y + 6, False, 30)
        s.text(PAD + 60, y, name, f(MONOB, 36), FG)
        s.text(PAD + 60, y + 46, why, f(REG, 32), MUTED)
        y += 102
    y += 6
    s.box(PAD - 16, y - 14, W - PAD + 16, y + 92, fill=(20, 40, 32), outline=GREEN)
    s.mark(PAD + 4, y + 8, True, 34)
    s.text(PAD + 64, y + 4, "NFS", f(MONOB, 40), GREEN)
    s.text(PAD + 64, y + 50, "simples, nativo no Linux, uma cópia só", f(REG, 32), FG)


def s4(s):
    y = kicker(s, "# a ideia")
    y = title(s, ["Uma pasta.", "Uma cópia.", [("Todos os PCs.", GREEN)]], y, 84)
    s.diagram(W / 2, 980, 0.95)


def s5(s):
    y = kicker(s, "# servidor")
    y = title(s, ["Do lado do servidor,", "são 3 passos"], y, 70)
    y += 40
    y = s.code(PAD, y, W - 2 * PAD, ["# 1. instalar", "sudo apt install nfs-kernel-server", "",
                                     "# 2. criar a pasta", "sudo mkdir -p /srv/nfs/shared", "",
                                     "# 3. exportar para a rede", "sudo vim /etc/exports", "sudo exportfs -ra"], 34)
    y += 40
    s.wrap(PAD, y, "No /etc/exports: quem pode montar (sua sub-rede) e como (rw, sync, all_squash...). "
                   "Cada opção explicada no artigo.", f(REG, 32), MUTED, W - 2 * PAD, 46)


def s6(s):
    y = kicker(s, "# clientes")
    y = title(s, ["Nos PCs, uma linha", [("no ", FG), ("/etc/fstab", GREEN)]], y, 70)
    y += 40
    y = s.code(PAD, y, W - 2 * PAD, ["sudo apt install nfs-common", "", "# /etc/fstab",
                                     [("IP:/srv/nfs/shared  /home/eu/shared  nfs4", FG)],
                                     [("  _netdev,nofail,", MUTED)],
                                     [("  x-systemd.automount", MUTED)], "", "sudo mount -a"], 36)
    y += 70
    s.text(PAD, y, "~/shared aparece igual em todo PC.", f(MED, 42), FG)
    s.text(PAD, y + 62, "Edita num, continua no outro.", f(MED, 42), GREEN)


def s7(s):
    y = kicker(s, "# o perrengue")
    y = title(s, ["No Linux nativo: de primeira.", [("No WSL: ", FG), ("timeout.", RED)]], y, 62)
    y += 40
    steps = [("ss", "servidor escutando na 2049? sim"),
             ("telnet", "porta aberta? sim"),
             ("nc -p 900", "porta privilegiada? conecta"),
             ("tcpdump", "e o mount continuava travando")]
    for cmd, desc in steps:
        s.box(PAD, y, W - PAD, y + 92)
        s.text(PAD + 30, y + 46, cmd, f(MONOB, 36), BLUE, "lm")
        s.text(PAD + 270, y + 46, desc, f(REG, 31), FG, "lm")
        y += 110
    y += 40
    s.box(PAD, y, W - PAD, y + 230, fill=(20, 40, 32), outline=GREEN)
    s.text(PAD + 34, y + 34, "a correção", f(MONOB, 32), GREEN)
    s.rich(PAD + 34, y + 88, [("noresvport", GREEN), ("  no cliente", FG)], f(MONOB, 42))
    s.rich(PAD + 34, y + 150, [("insecure", GREEN), ("    no servidor", FG)], f(MONOB, 42))


def s8(s):
    y = kicker(s, "# a lição")
    y = title(s, ["Mudei duas coisas", "de uma vez."], y, 80)
    y += 30
    y = s.wrap(PAD, y, "Funcionou, mas eu não sabia qual delas tinha resolvido. Voltei e testei separado:",
               f(REG, 34), MUTED, W - 2 * PAD, 48)
    y += 30
    for sint, causa, col in [("Operation not permitted", "servidor sem insecure", RED),
                             ("timeout", "cliente em porta privilegiada", RED)]:
        s.box(PAD, y, W - PAD, y + 126)
        s.text(PAD + 30, y + 24, sint, f(MONOB, 34), col)
        s.text(PAD + 30, y + 70, "→", f(ARROW, 32), MUTED)
        s.text(PAD + 70, y + 70, causa, f(REG, 32), FG)
        y += 146
    y += 30
    s.text(PAD, y, "Mude uma coisa por vez.", f(BOLD, 54), GREEN)


def s9(s):
    y = kicker(s, "# artigo completo", 300)
    y = title(s, ["Passo a passo,", "cada opção explicada", "e o troubleshooting", "inteiro no dev.to"], y, 70)
    y += 60
    s.box(PAD, y, W - PAD, y + 110, fill=(20, 40, 32), outline=GREEN)
    s.text(W / 2, y + 55, "link nos comentários / na bio", f(MONOB, 36), GREEN, "mm")
    y += 190
    logo = Image.open(LOGO_DIR + "devnordestino-full-dark.png").convert("RGBA")
    lw = 780 * SS
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    s.img.paste(logo, ((W * SS - lw) // 2, int(y * SS)), logo)


SLIDES = [s1, s2, s3, s4, s5, s6, s7, s8, s9]
pages = []
for i, fn in enumerate(SLIDES, 1):
    sl = Slide()
    last = i == len(SLIDES)
    fn(sl)
    sl.chrome(i, len(SLIDES), last)
    pages.append(sl.save(f"{OUT}/slide-{i:02d}.png").convert("RGB"))
pages[0].save(f"{OUT}/carousel.pdf", save_all=True, append_images=pages[1:], resolution=150)
print("ok", len(pages))
