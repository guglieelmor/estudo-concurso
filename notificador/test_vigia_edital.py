import json
import os
import subprocess
import sys
import tempfile

from vigia_edital import carrega_config, combina, links

PAGINA = '''<html><script>var a = "<a href='/x'>edital pf</a>";</script>
<a href="/noticias/policia-federal-publica-edital-agente-2027"><img src="f.jpg"></a>
<a href="/noticias/policia-federal-publica-edital-agente-2027" title="PF publica edital">Polícia Federal publica edital para Agente</a>
<a href="https://site.com/noticias/pf-faz-operacao">PF faz operação no porto</a>
<a href="/noticias/prf-abre-inscricoes">PRF abre inscrições</a>
<a href="javascript:void(0)">edital</a>
<a href="/edital.pdf">Edital de abertura nº 1 - TRF 3</a>
</html>'''

ls = links(PAGINA, "https://site.com/noticias/")
urls = [l["url"] for l in ls]
assert urls == [
    "https://site.com/noticias/policia-federal-publica-edital-agente-2027",
    "https://site.com/noticias/pf-faz-operacao",
    "https://site.com/noticias/prf-abre-inscricoes",
    "https://site.com/edital.pdf",
], urls
assert "Agente" in ls[0]["texto"] and "PF publica edital" in ls[0]["texto"], "junta textos do mesmo link"

pf = {"nome": "PF", "termos": ["policia federal|pf"]}
assert combina(ls[0], pf)
assert not combina(ls[1], pf), "sem gatilho (edital/abertura) nao combina"
assert not combina(ls[2], pf), "'pf' nao pode casar com 'prf'"
assert combina(ls[0], {"nome": "x", "termos": ["policia federal", "agente"]}), "todos os termos"
assert not combina(ls[0], {"nome": "x", "termos": ["policia federal", "escrivao"]})
assert combina(ls[3], {"nome": "x", "termos": ["trf 3|trf3"]}), "termo com espaco"
assert combina(ls[1], {"nome": "x", "termos": ["pf"], "gatilhos": ["operacao"]}), "gatilhos proprios"

cfg = {"topico": "editais-abcd", "vigias": [], "modo": "local"}
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump(cfg, f)
assert carrega_config(["--config", f.name], {}) == cfg
assert carrega_config([], {"VIGIAS": '{"topico": "a"}'}) == {"topico": "a"}
os.unlink(f.name)

# Ciclo completo com servidor local: semeia, depois so notifica o novo.
import http.server
import threading

conteudo = {"html": '<a href="/a">PF publica edital antigo</a>'}


class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(conteudo["html"].encode())

    def log_message(self, *a):
        pass


srv = http.server.HTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
d = tempfile.mkdtemp()
cfg = {"topico": "t", "vigias": [{"nome": "PF", "url": f"http://127.0.0.1:{srv.server_port}/", "termos": ["pf"]}]}
env = {**os.environ, "VIGIAS": json.dumps(cfg), "VISTOS": os.path.join(d, "v.json"), "DRY": "1"}
script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vigia_edital.py")
roda = lambda: subprocess.run([sys.executable, script], env=env, capture_output=True, text=True)

r = roda()
assert r.returncode == 0 and "semeando 1" in r.stdout and "---" not in r.stdout, r.stdout + r.stderr
conteudo["html"] += '<a href="/b">PF publica edital de abertura 2027</a>'
r = roda()
assert "--- [t] Edital: PF" in r.stdout and "/b" in r.stdout and "/a\n" not in r.stdout, r.stdout
r = roda()
assert "---" not in r.stdout and "0 novo(s)" in r.stdout, "nao repete aviso"
conteudo["html"] = "<p>sem links</p>"
assert roda().returncode != 0, "pagina sem links deve falhar"
srv.shutdown()
print("ok")
