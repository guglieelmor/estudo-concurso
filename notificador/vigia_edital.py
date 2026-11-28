"""Avisa via ntfy quando um edital especifico aparece num site que publica editais.

Config (--config arq.json, formato da skill notifica-edital, ou env VIGIAS com o mesmo JSON):
  {"topico": "...", "vigias": [{"nome": "PF 2027", "url": "https://...",
                                "termos": ["policia federal|pf", "agente"],
                                "gatilhos": ["edital", "abertura"]}]}
termos: TODOS precisam aparecer; "a|b" = um ou outro. gatilhos: basta UM (ausente = GATILHOS).
O texto comparado de cada link e: texto do link + title + endereco (hifens viram espaco).
--listar [nome] imprime em JSON os links que combinam (ou, com --todos, todos os links) e sai.
Estado em VISTOS (padrao vistos-edital.json). Vigia sem estado so semeia, nao notifica.
DRY=1 imprime em vez de enviar.
"""
import html
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request

NTFY = os.environ.get("NTFY_URL", "https://ntfy.sh")
GATILHOS = ["edital", "editais", "abertura", "abre", "abrem", "aberto", "abertas", "inscricao", "inscricoes"]
POR_MENSAGEM = 10  # ntfy limita mensagem a 4 KB


def normaliza(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[-_/.+]", " ", sem_acento)).lower().strip()


def baixa(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (vigia-edital)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")


def links(pagina, base):
    """Lista de dicts {url, texto} sem repetir url, na ordem da pagina."""
    pagina = re.sub(r"<(script|style)\b.*?</\1>", " ", pagina, flags=re.S | re.I)
    vistos, saida = set(), []
    for attrs, corpo in re.findall(r"<a\b([^>]*)>(.*?)</a>", pagina, re.S | re.I):
        href = re.search(r'href\s*=\s*["\']([^"\'#]+)', attrs, re.I)
        if not href or href.group(1).lower().startswith(("javascript:", "mailto:", "tel:")):
            continue
        url = urllib.parse.urljoin(base, html.unescape(href.group(1).strip()))
        title = re.search(r'title\s*=\s*["\']([^"\']*)', attrs, re.I)
        texto = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", corpo)).split())
        extra = " ".join(html.unescape(title.group(1)).split()) if title else ""
        if extra and extra not in texto:
            texto = f"{texto} {extra}".strip()
        if url in vistos:
            # Mesmo link repetido (imagem + titulo): junta os textos.
            for it in saida:
                if it["url"] == url and texto and texto not in it["texto"]:
                    it["texto"] = f"{it['texto']} {texto}".strip()
            continue
        vistos.add(url)
        saida.append({"url": url, "texto": texto})
    return saida


def _tem(termo, texto):
    return any(re.search(rf"\b{re.escape(normaliza(alt))}\b", texto) for alt in termo.split("|") if alt.strip())


def combina(link, vigia):
    texto = normaliza(f"{link['texto']} {urllib.parse.unquote(link['url'])}")
    gatilhos = vigia.get("gatilhos") or GATILHOS
    return all(_tem(t, texto) for t in vigia.get("termos") or []) and any(_tem(g, texto) for g in gatilhos)


def envia(topico, vigia, achados):
    for i in range(0, len(achados), POR_MENSAGEM):
        lote = achados[i:i + POR_MENSAGEM]
        corpo = "\n\n".join(f"{a['texto'] or '(sem título)'}\n{a['url']}" for a in lote)
        titulo = f"Edital: {vigia['nome']}"
        if os.environ.get("DRY"):
            print(f"--- [{topico}] {titulo}\n{corpo}\n")
            continue
        req = urllib.request.Request(
            f"{NTFY}/{topico}",
            data=corpo.encode(),
            headers={"Title": titulo.encode("utf-8"), "Tags": "rotating_light", "Priority": "high", "Click": lote[0]["url"]},
        )
        urllib.request.urlopen(req, timeout=30).read()


def carrega_config(argv, env):
    if "--config" in argv:
        with open(argv[argv.index("--config") + 1], encoding="utf-8") as f:
            return json.load(f)
    if env.get("VIGIAS"):
        return json.loads(env["VIGIAS"])
    sys.exit("Informe --config arquivo.json ou a env VIGIAS.")


def listar(argv, cfg):
    i = argv.index("--listar")
    nome = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("--") else None
    if "--url" in argv:  # testar um site antes de gravar a vigia
        vigias = [{"nome": "teste", "url": argv[argv.index("--url") + 1],
                   "termos": json.loads(os.environ.get("TERMOS", "[]")),
                   "gatilhos": json.loads(os.environ.get("GATILHOS_TESTE", "[]"))}]
    else:
        vigias = [v for v in cfg["vigias"] if nome in (None, v["nome"])]
    saida = {}
    for v in vigias:
        todos = links(baixa(v["url"]), v["url"])
        saida[v["nome"]] = {"links_na_pagina": len(todos),
                            "combinam": todos if "--todos" in argv else [l for l in todos if combina(l, v)]}
    print(json.dumps(saida, ensure_ascii=False, indent=1))


def main():
    argv = sys.argv[1:]
    cfg = carrega_config(argv, os.environ) if ("--config" in argv or os.environ.get("VIGIAS")) else {"vigias": []}
    if "--listar" in argv:
        return listar(argv, cfg)
    if not cfg.get("topico"):
        sys.exit("Config sem topico.")
    caminho = os.environ.get("VISTOS", "vistos-edital.json")
    estado = json.load(open(caminho, encoding="utf-8")) if os.path.exists(caminho) else {}
    falhas = 0
    for v in cfg.get("vigias", []):
        chave = f"{v['nome']}|{v['url']}"
        try:
            todos = links(baixa(v["url"]), v["url"])
        except Exception as e:  # um site fora do ar nao derruba as outras vigias
            print(f"{v['nome']}: erro ao baixar ({e})")
            falhas += 1
            continue
        if not todos:
            print(f"{v['nome']}: nenhum link na pagina (site mudou ou exige JavaScript?)")
            falhas += 1
            continue
        achados = [l for l in todos if combina(l, v)]
        if chave not in estado:
            print(f"{v['nome']}: primeira execucao, semeando {len(achados)} link(s) sem notificar.")
            estado[chave] = [a["url"] for a in achados]
            continue
        novos = [a for a in achados if a["url"] not in estado[chave]]
        if novos:
            envia(cfg["topico"], v, novos)
        # Acumula: noticia que sai da capa e volta nao notifica de novo.
        estado[chave] = sorted(set(estado[chave]) | {a["url"] for a in achados})
        print(f"{v['nome']}: {len(todos)} links, {len(achados)} combinam, {len(novos)} novo(s) notificado(s).")
    # Remove estado de vigias apagadas.
    ativas = {f"{v['nome']}|{v['url']}" for v in cfg.get("vigias", [])}
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in estado.items() if k in ativas}, f, ensure_ascii=False, indent=1)
    if falhas:
        sys.exit(f"{falhas} vigia(s) com problema.")


if __name__ == "__main__":
    main()
