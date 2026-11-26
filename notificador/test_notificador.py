from notificador import combina, extrai

PAGINA = '''<div class="uf">SÃO PAULO</div>
<div class="na" onclick="myClick(event)" data-url="https://x/1"><div class="ca"><a href="https://x/1" title="Prefeitura abre concurso para Analista de TI">Prefeitura de Campinas</a>
<div class="cd">10 vagas até R$ 8.000,00<br><span>Analista de TI<br><span>Superior</span></span>
</div><div class="ce"><span>10/01/2027</span></div>
<div class="clear"></div></div>
<div class="uf">NACIONAL</div>
<div class="na" onclick="myClick(event)" data-url="https://x/2"><div class="ca"><a href="https://x/2" title="INSS abre concurso para Técnico do Seguro Social">INSS</a>
<div class="cd">1000 vagas<br><span>Técnico<br><span>Médio</span></span>
</div><div class="ce"><span>05/02/2027</span></div>
<div class="clear"></div></div>'''

itens = extrai(PAGINA)
assert [i["estado"] for i in itens] == ["SÃO PAULO", "NACIONAL"], itens
assert itens[0]["prazo"] == "10/01/2027" and "Analista de TI" in itens[0]["detalhe"], itens[0]

ti = {"topico": "t", "palavras": ["ti"]}
assert combina(itens[0], ti)
assert not combina(itens[1], ti), "'ti' nao pode casar com 'tecnico'"
assert combina(itens[1], {"topico": "t", "palavras": ["tecnico"]}), "acento ignorado"
assert combina(itens[0], {"topico": "t", "estados": ["sao paulo"]})
assert not combina(itens[1], {"topico": "t", "estados": ["SÃO PAULO"]})
assert combina(itens[1], {"topico": "t"}), "sem filtro aceita tudo"

import json, os, tempfile
from notificador import carrega_usuarios

perfil = {"topico": "concursos-abcd1234", "palavras": ["ti"], "salario_minimo": 5000, "resumo": "x", "modo": "local"}
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
    json.dump(perfil, f)
assert carrega_usuarios(["--perfil", f.name], {}) == [perfil]
assert carrega_usuarios([], {"USUARIOS": '[{"topico": "a"}]'}) == [{"topico": "a"}]
os.unlink(f.name)
try:
    carrega_usuarios([], {})
    raise AssertionError("sem perfil e sem USUARIOS devia falhar")
except SystemExit:
    pass
print("ok")
