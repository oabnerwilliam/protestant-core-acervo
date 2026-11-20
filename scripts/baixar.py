#!/usr/bin/env python3
"""1) buscas.txt: uma busca por linha (ex.: "Luther Worms painting"). Para cada busca nova, salva até 12
candidatos em domínio público e com boa resolução em candidatos/<slug-da-busca>/ (miniatura 640px + index.json).
2) Lê pedidos.txt (um nome de arquivo do Wikimedia Commons por linha, ex.: File:Luther_at_the_Diet_of_Worms.jpg),
baixa cada pintura ainda não baixada (até 2400 px de largura) para pinturas/<slug>.jpg,
salva os metadados em pinturas/<slug>.json e atualiza acervo.json."""
import json, os, re, sys, time, unicodedata, urllib.parse, urllib.request

UA = "ProtestantCoreAcervo/1.0 (https://github.com/oabnerwilliam/protestant-core-acervo)"
API = "https://commons.wikimedia.org/w/api.php"
LARG = 2400

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def limpa(html):
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()
    t = re.split(r"\s*(?:title|label|date|object_type)\s+QS:", t)[0].strip()
    t = re.sub(r"^[A-Z][a-zà-ú]+:\s+", "", t)  # "German: ..." -> "..."
    return t.strip(' "')

PD = re.compile(r"public domain|^pd|cc0|no restrictions", re.I)

def buscar():
    if not os.path.exists("buscas.txt"): return
    for linha in open("buscas.txt", encoding="utf-8"):
        q = linha.split("#", 1)[0].strip()
        if not q: continue
        pasta = "candidatos/" + slug("x:" + q + ".x")
        if os.path.exists(pasta + "/index.json"): continue
        os.makedirs(pasta, exist_ok=True)
        params = urllib.parse.urlencode({"action": "query", "generator": "search", "gsrnamespace": 6,
            "gsrsearch": q + " filetype:bitmap", "gsrlimit": 40, "prop": "imageinfo",
            "iiprop": "url|size|extmetadata", "iiurlwidth": 640, "format": "json"})
        paginas = json.loads(get(f"{API}?{params}")).get("query", {}).get("pages", {})
        cands = []
        for pg in sorted(paginas.values(), key=lambda p: p.get("index", 99)):
            ii = (pg.get("imageinfo") or [{}])[0]; meta = ii.get("extmetadata", {})
            lic = limpa(meta.get("LicenseShortName", {}).get("value"))
            if not PD.search(lic) or min(ii.get("width", 0), ii.get("height", 0)) < 1100: continue
            n = len(cands) + 1
            mini = f"{pasta}/{n:02d}.jpg"
            open(mini, "wb").write(get(ii["thumburl"])); time.sleep(0.5)
            cands.append({"n": n, "commons": pg["title"].replace(" ", "_"), "miniatura": mini,
                "largura": ii["width"], "altura": ii["height"], "licenca": lic,
                "titulo": limpa(meta.get("ObjectName", {}).get("value")),
                "artista": limpa(meta.get("Artist", {}).get("value")),
                "data": limpa(meta.get("DateTimeOriginal", {}).get("value"))})
            if len(cands) >= 12: break
        json.dump({"busca": q, "candidatos": cands}, open(pasta + "/index.json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print(f"BUSCA '{q}': {len(cands)} candidatos em {pasta}")

def slug(nome):
    s = unicodedata.normalize("NFKD", nome.split(":", 1)[-1].rsplit(".", 1)[0])
    s = s.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:80]

def main():
    buscar()
    pedidos = []
    if os.path.exists("pedidos.txt"):
        for linha in open("pedidos.txt", encoding="utf-8"):
            linha = linha.split("#", 1)[0].strip()
            if not linha: continue
            if "commons.wikimedia.org/wiki/" in linha:
                linha = urllib.parse.unquote(linha.split("/wiki/", 1)[1])
            if not linha.startswith("File:"): linha = "File:" + linha
            pedidos.append(linha.replace(" ", "_"))
    acervo = json.load(open("acervo.json", encoding="utf-8")) if os.path.exists("acervo.json") else []
    feitos = {a["commons"] for a in acervo}
    os.makedirs("pinturas", exist_ok=True)
    erros = 0
    for nome in pedidos:
        if nome in feitos: continue
        q = urllib.parse.urlencode({"action": "query", "titles": nome, "prop": "imageinfo",
            "iiprop": "url|size|extmetadata|mime", "iiurlwidth": LARG, "format": "json"})
        try:
            pag = next(iter(json.loads(get(f"{API}?{q}"))["query"]["pages"].values()))
            info = pag["imageinfo"][0]
        except Exception as e:
            print(f"ERRO {nome}: não encontrado ({e})", file=sys.stderr); erros += 1; continue
        url = info.get("thumburl") if info["width"] > LARG else info["url"]
        meta = info.get("extmetadata", {})
        s = slug(nome)
        ext = ".png" if url.lower().endswith(".png") else ".jpg"
        caminho = f"pinturas/{s}{ext}"
        open(caminho, "wb").write(get(url)); time.sleep(1)
        reg = {
            "commons": nome, "arquivo": caminho,
            "pagina": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(nome),
            "titulo": limpa(meta.get("ObjectName", {}).get("value")) or nome[5:].rsplit(".", 1)[0].replace("_", " "),
            "artista": limpa(meta.get("Artist", {}).get("value")),
            "data": limpa(meta.get("DateTimeOriginal", {}).get("value")),
            "licenca": limpa(meta.get("LicenseShortName", {}).get("value")),
            "largura_original": info["width"], "altura_original": info["height"],
        }
        json.dump(reg, open(f"pinturas/{s}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        acervo.append(reg); feitos.add(nome)
        print("OK", nome, "->", caminho, "|", reg["licenca"])
    json.dump(acervo, open("acervo.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if erros: print(f"{erros} pedido(s) com erro", file=sys.stderr)

if __name__ == "__main__":
    main()
