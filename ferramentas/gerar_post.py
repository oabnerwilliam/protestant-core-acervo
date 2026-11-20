#!/usr/bin/env python3
"""The Protestant Core — gerador de posts (1080x1350).

Uso:
  python3 gerar_post.py moldura <referencia.png> <moldura.png>
      Extrai a moldura (papel vermelho rasgado + papel bege) de um post de referência,
      apagando o texto e mantendo o @ (THEPROTESTANTCORE).
  python3 gerar_post.py post <spec.json>
      Gera o post. spec.json:
      {
        "moldura": "moldura.png",
        "pintura": "pintura.jpg",
        "foco": [0.5, 0.35],        # ponto da pintura que deve ficar no centro da janela (0-1)
        "zoom": 1.0,                # >1 aproxima
        "texto": "“Pois vocês são salvos **pela graça**...”",   # **negrito**
        "atribuicao": "Efésios 2:8-9",                          # ou "- Martinho Lutero"
        "saida": "post.png"
      }
Dependências: pillow, numpy, opencv-python-headless, scipy. Fonte Fraunces (baixada do repositório
google/fonts no GitHub se não existir em ./fonts).
"""
import json, os, sys, urllib.request
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi

W, H = 1080, 1350
AQUI = os.path.dirname(os.path.abspath(__file__))
FONTE = os.path.join(AQUI, "fonts", "Fraunces.ttf")
FONTE_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/Fraunces%5BSOFT,WONK,opsz,wght%5D.ttf"
TINTA = (19, 19, 19)

# ---------------------------------------------------------------- moldura
def montar_moldura(ref_path, out_path):
    src = np.array(Image.open(ref_path).convert("RGB").resize((W, H), Image.LANCZOS))
    a = src.astype(int); R, G, B = a[..., 0], a[..., 1], a[..., 2]
    yy = np.arange(H)[:, None].repeat(W, 1)
    red = (R > 110) & (R - G > 55)
    white = np.minimum(np.minimum(R, G), B) > 165
    light = (G > 165) & (B > 135)
    paper = ((yy < 230) & (red | white)) | ((yy > 440) & light) | (yy >= 720)
    lab, _ = ndi.label(paper)
    keep = (set(np.unique(lab[0])) | set(np.unique(lab[H - 1]))) - {0}
    paper = ndi.binary_closing(np.isin(lab, list(keep)), iterations=2)
    top = np.zeros_like(paper); bot = np.zeros_like(paper)
    for x in range(W):
        col = paper[:, x]
        i = 400 if col[:400].all() else int(np.argmin(col[:400]))
        top[:i, x] = True
        j = int(np.argmin(col[::-1])); bot[H - j:, x] = True
    p = (top | bot) | (paper & ((yy < 230) | (yy > 440)))
    p[:, :3] = p[:, 3:4]; p[:, -3:] = p[:, -4:-3]; p[:3] = p[3:4]; p[-3:] = p[-4:-3]
    alpha = cv2.GaussianBlur(p.astype(np.float32), (3, 3), 0.8, borderType=cv2.BORDER_REPLICATE)

    lum = (R + G + B) / 3
    # assinatura THEPROTESTANTCORE: salva à parte (posicionada no layout) e apaga da moldura
    xs = np.arange(W)[None, :].repeat(H, 0)
    zona_ass = (yy > 1185) & (yy < 1240) & (xs > 370) & (xs < 720)
    ys_, xs_ = np.where((lum < 120) & zona_ass)
    if len(ys_):
        y0a, y1a, x0a, x1a = ys_.min() - 3, ys_.max() + 4, xs_.min() - 3, xs_.max() + 4
        cl = np.clip((200 - lum[y0a:y1a, x0a:x1a]) / 170, 0, 1)
        ass = np.zeros((y1a - y0a, x1a - x0a, 4), np.uint8); ass[..., :3] = 19
        ass[..., 3] = (cl * 255).astype(np.uint8)
        Image.fromarray(ass, "RGBA").save(caminho_assinatura(out_path))
    # apaga o texto e a assinatura
    band = ((yy > 780) & (yy < 1175)) | zona_ass
    dark = ndi.binary_opening((lum < 185) & band, iterations=1) | ((lum < 155) & band)
    dark = ndi.binary_dilation(dark, iterations=4)
    S = 8
    srcf = src.astype(np.float32)
    valid = (~ndi.binary_dilation(dark, iterations=4)).astype(np.float32)
    low = cv2.GaussianBlur(srcf * valid[..., None], (0, 0), 14) / np.maximum(
        cv2.GaussianBlur(valid, (0, 0), 14)[..., None], 1e-3)
    # textura fina: blocos limpos do próprio papel (acima do texto)
    lo2 = srcf - cv2.GaussianBlur(srcf, (0, 0), S)
    clean_rows = [r for r in range(600, 830) if (lum[r, 60:1020].min() > 175)]
    tiles, run = [], []
    for r in clean_rows:
        if run and r != run[-1] + 1:
            if len(run) > 30: tiles.append(lo2[run[0]:run[-1]])
            run = []
        run.append(r)
    if len(run) > 30: tiles.append(lo2[run[0]:run[-1]])
    if not tiles: tiles = [lo2[660:760]]
    rng = np.random.default_rng(7)
    y0, y1 = 790, 1245
    hf = np.zeros((y1 - y0, W, 3), np.float32); ws = np.zeros((y1 - y0, 1, 1), np.float32)
    CF = 14; y = 0
    while y < y1 - y0:
        t = np.roll(tiles[rng.integers(len(tiles))], rng.integers(W), axis=1)
        if rng.random() < .5: t = t[:, ::-1]
        th = t.shape[0]; w = np.ones((th, 1, 1), np.float32)
        ramp = np.linspace(.05, 1, CF)[:, None, None]; w[:CF] = ramp; w[-CF:] = ramp[::-1]
        n = min(th, (y1 - y0) - y)
        hf[y:y + n] += t[:n] * w[:n]; ws[y:y + n] += w[:n]; y += th - CF
    hf /= np.maximum(ws, 1e-3)
    fe = np.ones((y1 - y0, 1, 1), np.float32); r = np.linspace(0, 1, 25)[:, None, None]
    fe[:25] = r; fe[-25:] = r[::-1]
    beige = ((R > 195) & (G > 180) & (B > 145) & (R - B < 80)) | dark
    beige = ndi.binary_erosion(beige, iterations=6).astype(np.float32)
    m = fe * cv2.GaussianBlur(beige, (0, 0), 3)[y0:y1, :, None]
    out = srcf.copy()
    out[y0:y1] = (low[y0:y1] + hf) * m + srcf[y0:y1] * (1 - m)
    rgba = np.dstack([np.clip(out, 0, 255).astype(np.uint8), (alpha * 255).astype(np.uint8)])
    Image.fromarray(rgba, "RGBA").save(out_path)
    print("moldura salva em", out_path)

def caminho_assinatura(moldura):
    return os.path.splitext(moldura)[0] + "_assinatura.png"

def medir_area(rgb):
    """Topo = dobra/rasgo horizontal do papel bege; base = início do papel vermelho de baixo."""
    L = rgb.mean(axis=2)
    perfil = L[700:880, 85:995].mean(axis=1)
    dobra = 700 + int(np.argmin(perfil))
    R, G = rgb[..., 0], rgb[..., 1]
    verm = (R - G) > 60
    cols = range(85, 995, 5)
    base = min(900 + int(np.argmax(verm[900:, x])) for x in cols)
    return dobra, base

# ---------------------------------------------------------------- fontes
def fonte(peso, tam):
    if not os.path.exists(FONTE):
        os.makedirs(os.path.dirname(FONTE), exist_ok=True)
        urllib.request.urlretrieve(FONTE_URL, FONTE)
    f = ImageFont.truetype(FONTE, tam)
    eixos = f.get_variation_axes()
    nomes = [(e["name"] if isinstance(e["name"], str) else e["name"].decode()) for e in eixos]
    alvo = {"Weight": peso, "Optical size": 144, "Softness": 0, "Wonky": 0}
    f.set_variation_by_axes([alvo.get(n, e["default"]) for n, e in zip(nomes, eixos)])
    return f

# ---------------------------------------------------------------- texto
def aspas(t):
    """Troca aspas retas por tipográficas (“ ”)."""
    out, abre = [], True
    for ch in t:
        if ch == '"': out.append("“" if abre else "”"); abre = not abre
        else: out.append(ch)
    return "".join(out)

def tokens(texto):
    """'a **b c**, d' -> palavras; cada palavra = lista de (trecho, negrito).
    Pontuação colada ao negrito continua colada. '\n' força quebra de linha."""
    palavras, atual = [], []
    for i, parte in enumerate(texto.split("**")):
        b = i % 2 == 1
        buf = ""
        for ch in parte:
            if ch == "\n" or ch.isspace():
                if buf: atual.append((buf, b)); buf = ""
                if atual: palavras.append(atual); atual = []
                if ch == "\n": palavras.append("\n")
            else:
                buf += ch
        if buf: atual.append((buf, b))
    if atual: palavras.append(atual)
    return palavras

def larg_palavra(pal, fr, fb, track):
    return sum((fb if b else fr).getlength(t) + track * len(t) for t, b in pal) - track

def quebrar(toks, fr, fb, larg, track):
    esp = fr.getlength(" ") * 0.85
    linhas, atual, x = [], [], 0
    for pal in toks:
        if pal == "\n":
            linhas.append(atual); atual, x = [], 0; continue
        lw = larg_palavra(pal, fr, fb, track)
        if atual and x + esp + lw > larg:
            linhas.append(atual); atual, x = [], 0
        x += (esp if atual else 0) + lw; atual.append(pal)
    if atual: linhas.append(atual)
    return linhas

def quebrar_equilibrado(toks, fr, fb, larg, track):
    """Mesma quantidade de linhas do ajuste guloso, mas com linhas de tamanho parecido."""
    paras, atual = [], []
    for t in toks:
        if t == "\n": paras.append(atual); atual = []
        else: atual.append(t)
    paras.append(atual)
    out = []
    for p in paras:
        n = len(quebrar(p, fr, fb, larg, track))
        lo, hi = larg * 0.5, larg
        while hi - lo > 2:
            mid = (lo + hi) / 2
            if len(quebrar(p, fr, fb, mid, track)) > n: lo = mid
            else: hi = mid
        out += quebrar(p, fr, fb, hi, track)
    return out

def escrever(d, x, y, palavra, f, track):
    for ch in palavra:
        d.text((x, y), ch, font=f, fill=TINTA, anchor="ls")
        x += f.getlength(ch) + track
    return x - track

# ---------------------------------------------------------------- post
def janela(alpha):
    vazio = alpha[:900] < 128
    linhas = np.where(vazio.any(axis=1))[0]
    return int(linhas.min()), int(linhas.max())

def gerar(spec):
    mold = Image.open(spec["moldura"]).convert("RGBA")
    al = np.array(mold)[..., 3]
    jt, jb = janela(al)
    caixa_h = jb + 30  # pintura vai um pouco além da borda rasgada
    pint = Image.open(spec["pintura"]).convert("RGB")
    zoom = float(spec.get("zoom", 1.0)); fx, fy = spec.get("foco", [0.5, 0.4])
    esc = max(W / pint.width, caixa_h / pint.height) * zoom
    pw, ph = int(pint.width * esc + .5), int(pint.height * esc + .5)
    pint = pint.resize((pw, ph), Image.LANCZOS)
    cx = min(max(int(fx * pw - W / 2), 0), pw - W)
    # centro vertical da janela visível (~meio entre topo e base rasgados)
    meio = (jt + jb) / 2
    cy = min(max(int(fy * ph - meio), 0), ph - caixa_h)
    base = Image.new("RGB", (W, H), (60, 55, 50))
    base.paste(pint.crop((cx, cy, cx + W, cy + caixa_h)), (0, 0))
    # sombra suave do papel sobre a pintura
    sh = Image.fromarray(al).filter(ImageFilter.GaussianBlur(7))
    sh = Image.fromarray(np.roll(np.array(sh), 5, axis=0))
    escuro = Image.new("RGB", (W, H), (0, 0, 0))
    base = Image.composite(escuro, base, sh.point(lambda v: int(v * .38)))
    base.paste(mold, (0, 0), mold)

    # texto + assinatura: grupo centralizado verticalmente entre a dobra do papel e o vermelho
    texto = aspas(spec["texto"].strip()); atrib = spec.get("atribuicao", "").strip()
    rgb = np.array(mold.convert("RGB")).astype(int)
    dobra, verm = medir_area(rgb)
    MARG_TOPO, MARG_BASE, GAP, DESCER = 42, 34, 46, 22
    area_topo, area_base = dobra + MARG_TOPO, verm - MARG_BASE
    ass = Image.open(caminho_assinatura(spec["moldura"])) if os.path.exists(caminho_assinatura(spec["moldura"])) else None
    ass_h = ass.height if ass else 0
    margem, larg = 85, 910
    for tam in range(50, 31, -1):
        fr, fb = fonte(320, tam), fonte(420, tam)
        track = -0.045 * tam
        lin = quebrar_equilibrado(tokens(texto), fr, fb, larg, track)
        if atrib: lin += quebrar(tokens(atrib), fr, fb, larg, track)
        lh = round(tam * 1.33)
        asc, desc = round(tam * .74), round(tam * .22)
        bloco = asc + (len(lin) - 1) * lh + desc
        grupo = bloco + (GAP + ass_h if ass else 0)
        if grupo <= area_base - area_topo: break
    else:
        print("AVISO: texto longo demais para um card — encurte ou divida em carrossel.", file=sys.stderr)
    topo = area_topo + max(0, (area_base - area_topo - grupo) // 2) + DESCER
    topo = min(topo, verm - 16 - grupo)  # nunca encosta no vermelho
    d = ImageDraw.Draw(base)
    esp = fr.getlength(" ") * 0.85
    y = topo + asc
    for linha in lin:
        x = margem
        for pal in linha:
            for t, b in pal:
                x = escrever(d, x, y, t, fb if b else fr, track) + track
            x += esp - track
        y += lh
    if ass:
        ya = topo + bloco + GAP
        base.paste(ass, ((W - ass.width) // 2, ya), ass)
    base.save(spec.get("saida", "post.png"), quality=95)
    print(f"ok: {spec.get('saida','post.png')} (fonte {tam}px, {len(lin)} linhas)")

if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "moldura":
        montar_moldura(sys.argv[2], sys.argv[3])
    elif len(sys.argv) >= 3 and sys.argv[1] == "post":
        gerar(json.load(open(sys.argv[2], encoding="utf-8")))
    else:
        print(__doc__)
