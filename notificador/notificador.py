"""Avisa via ntfy quando aparecem concursos novos no PCI Concursos.

Usuarios:
  --perfil arq.json   um perfil so (formato da skill notifica-concurso), ou
  env USUARIOS        lista JSON: [{"topico": "...", "palavras": [...], "estados": [...]}]
palavras/estados vazios ou ausentes = aceita tudo. Outros campos sao ignorados.
--listar imprime os concursos da pagina em JSON (filtrados pelo perfil, se houver) e sai.
Estado dos ja vistos fica em VISTOS (padrao vistos.txt). Sem esse arquivo, so semeia, nao notifica.
DRY=1 imprime em vez de enviar.
"""
import html
import json
import os
import re
import sys
import unicodedata
import urllib.request

URL = "https://www.pciconcursos.com.br/concursos/"
NTFY = os.environ.get("NTFY_URL", "https://ntfy.sh")
POR_MENSAGEM = 10  # ntfy limita mensagem a 4 KB


def normaliza(texto):
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", sem_acento).lower().strip()


def baixa(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (notificador-concursos)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def extrai(pagina):
    """Lista de dicts {url, titulo, orgao, detalhe, estado} na ordem da pagina."""
    itens = []
    # Cada secao comeca com <div class="uf">ESTADO</div>; itens seguem ate a proxima.
    for estado, bloco in re.findall(r'<div class="uf">([^<]+)</div>(.*?)(?=<div class="uf">|\Z)', pagina, re.S):
        for url, corpo in re.findall(r'onclick="myClick\(event\)" data-url="([^"]+)"(.*?)<div class="clear">', bloco, re.S):
            m = re.search(r'<div class="ca"><a [^>]*title="([^"]*)"[^>]*>([^<]*)</a>', corpo)
            if not m:
                continue
            detalhe = re.search(r'<div class="cd">(.*?)</div>', corpo, re.S)
            prazo = re.search(r'<div class="ce">(.*?)</div>', corpo, re.S)
            limpa = lambda s: html.unescape(re.sub(r"<[^>]+>", " ", s or "")).split()
            itens.append({
                "url": url,
                "titulo": html.unescape(m.group(1)),
                "orgao": html.unescape(m.group(2)),
                "detalhe": " ".join(limpa(detalhe and detalhe.group(1))),
                "prazo": " ".join(limpa(prazo and prazo.group(1))),
                "estado": estado.strip(),
            })
    return itens


def combina(item, usuario):
    estados = [normaliza(e) for e in usuario.get("estados") or []]
    if estados and normaliza(item["estado"]) not in estados:
        return False
    palavras = [normaliza(p) for p in usuario.get("palavras") or []]
    texto = normaliza(" ".join([item["titulo"], item["orgao"], item["detalhe"]]))
    # \b evita "ti" casar com "tecnico"; palavra composta ("analista de ti") tambem funciona.
    return not palavras or any(re.search(rf"\b{re.escape(p)}\b", texto) for p in palavras)


def envia(topico, itens):
    for i in range(0, len(itens), POR_MENSAGEM):
        lote = itens[i:i + POR_MENSAGEM]
        corpo = "\n\n".join(
            f"{it['orgao']} ({it['estado']})\n{it['detalhe']} - até {it['prazo'] or '?'}\n{it['url']}" for it in lote
        )
        titulo = f"{len(itens)} concurso(s) novo(s)" if len(itens) > 1 else lote[0]["titulo"]
        if os.environ.get("DRY"):
            print(f"--- [{topico}] {titulo}\n{corpo}\n")
            continue
        req = urllib.request.Request(
            f"{NTFY}/{topico}",
            data=corpo.encode(),
            headers={"Title": titulo.encode("utf-8"), "Tags": "mega", **({"Click": lote[0]["url"]} if len(lote) == 1 else {})},
        )
        urllib.request.urlopen(req, timeout=30).read()


def carrega_usuarios(argv, env):
    if "--perfil" in argv:
        with open(argv[argv.index("--perfil") + 1], encoding="utf-8") as f:
            return [json.load(f)]
    if env.get("USUARIOS"):
        return json.loads(env["USUARIOS"])
    sys.exit("Informe --perfil arquivo.json ou a env USUARIOS.")


def main():
    argv = sys.argv[1:]
    itens = extrai(baixa(URL))
    if not itens:
        sys.exit("Nenhum concurso extraido: layout do PCI mudou?")
    if "--listar" in argv:
        usuarios = carrega_usuarios(argv, os.environ) if "--perfil" in argv else [{}]
        print(json.dumps([it for it in itens if combina(it, usuarios[0])], ensure_ascii=False, indent=1))
        return
    usuarios = carrega_usuarios(argv, os.environ)
    caminho = os.environ.get("VISTOS", "vistos.txt")

    primeira_vez = not os.path.exists(caminho)
    vistos = set() if primeira_vez else set(open(caminho, encoding="utf-8").read().split())
    novos = [it for it in itens if it["url"] not in vistos]

    if primeira_vez:
        print(f"Primeira execucao: semeando {len(itens)} concursos sem notificar.")
    else:
        for u in usuarios:
            meus = [it for it in novos if combina(it, u)]
            if meus:
                envia(u["topico"], meus)
            print(f"{u['topico'][:4]}***: {len(meus)} notificado(s)")

    # Guarda so o que esta na pagina hoje: arquivo nao cresce pra sempre.
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(it["url"] for it in itens))
    print(f"{len(itens)} na pagina, {len(novos)} novos.")


if __name__ == "__main__":
    main()
