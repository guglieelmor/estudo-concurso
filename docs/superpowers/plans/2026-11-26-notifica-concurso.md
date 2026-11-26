# Notifica Concurso Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Skill `/notifica-concurso` que monta o perfil do candidato (LinkedIn, site ou currículo), gera uma análise de concursos compatíveis e instala um verificador diário que manda push pelo ntfy.

**Architecture:** O `notificador/notificador.py`, que já existe, é o verificador determinístico. Ele ganha `--perfil` (um perfil só, lido de arquivo) e `--listar` (imprime em JSON os concursos da página, para o modo Claude). A skill é só markdown: `SKILL.md` orquestra as fases, e `references/` guarda o formato do perfil, a instalação de cada modo e o prompt do agente diário. A skill copia os arquivos de `notificador/` a partir do diretório do plugin instalado (`<base>/../../notificador/`).

**Tech Stack:** Python 3 só com stdlib, GitHub Actions, `gh` CLI, systemd/launchd/schtasks, ntfy.sh, skills do Claude Code em markdown.

**Spec:** `docs/superpowers/specs/2026-11-26-notifica-concurso-design.md`

## Global Constraints

- O script usa só a stdlib do Python 3. Nenhuma dependência nova.
- O canal é só o ntfy, com tópico `concursos-` mais 8 caracteres hex aleatórios.
- A fonte é só `https://www.pciconcursos.com.br/concursos/`.
- O perfil fica em `~/.config/notifica-concurso/perfil.json`. Campos: `topico`, `palavras`, `estados`, `salario_minimo`, `resumo`, `modo`.
- `palavras` e `estados` vazios aceitam tudo. A comparação ignora acento e maiúscula. `estados` usa o nome do PCI (`NACIONAL`, `SAO PAULO`).
- Na primeira execução o script só semeia e não notifica.
- Os textos da skill e as mensagens ao candidato ficam em pt-BR.
- Este repositório não roda notificação para ninguém: nada fica em `.github/workflows/`.

---

### Task 1: Spike — o modo Claude agendado é viável?

O modo Claude precisa de três coisas na tarefa agendada em nuvem: (a) acesso HTTP ao PCI, (b) POST no ntfy e (c) **estado persistente entre execuções**.

A deduplicação só pelo histórico do ntfy não serve. Um concurso fica semanas na página do PCI e o ntfy.sh guarda mensagens por cerca de 12h, então o mesmo aviso seria repetido a cada execução. Por isso, sem (c), o modo sai.

**Files:**
- Modify: `docs/superpowers/specs/2026-11-26-notifica-concurso-design.md` (seção "Claude agendado")

- [ ] **Step 1: Ler o que a skill `schedule` oferece**

Carregar a skill `schedule` e anotar: a tarefa roda sobre um repositório Git? Pode fazer commit e push nele? Tem rede liberada para domínios arbitrários?

- [ ] **Step 2: Criar uma tarefa de teste de execução única**

Com o usuário, criar pela skill `schedule` uma tarefa que roda uma vez com este prompt:

```
Rode e me mostre a saída de cada comando:
curl -s -o /dev/null -w "%{http_code}\n" https://www.pciconcursos.com.br/concursos/
curl -s -d "teste notifica-concurso" https://ntfy.sh/concursos-spike-<8 hex>
echo ok > estado-teste.txt && git add estado-teste.txt && git commit -m "spike: estado" && git push
```

Esperado para o modo ser viável: `200`, push recebido no app ntfy assinando `concursos-spike-<8 hex>` e commit visível no repositório.

- [ ] **Step 3: Registrar a decisão na spec**

Se as três coisas passaram, substituir a "Pré-condição a validar no plano" por:

```
Validado em <data>: a tarefa agendada roda sobre o repositório privado `notifica-concurso` do candidato (o mesmo do modo GitHub Actions), lê o PCI, faz POST no ntfy e guarda `vistos.txt` com commit. Exige `gh`, como o modo GitHub Actions.
```

Se alguma falhou, substituir a seção inteira por:

```
### Claude agendado (fora da v1)

Validado em <data>: a tarefa agendada em nuvem não <motivo>. Sem estado persistente, o mesmo concurso seria avisado a cada execução. Volta quando houver um lugar para guardar a lista de vistos.
```

Nesse caso, pular a Task 5 e, na Task 6, oferecer só os modos GitHub Actions e local.

- [ ] **Step 4: Apagar a tarefa de teste e commitar**

Apagar a tarefa agendada de teste pela skill `schedule`.

```bash
git add docs/superpowers/specs/2026-11-26-notifica-concurso-design.md
git commit -m "docs: record scheduled-agent feasibility for notifica-concurso"
```

---

### Task 2: `notificador.py` com `--perfil` e `--listar`; workflow vira modelo

**Files:**
- Modify: `notificador/notificador.py` (função `main`)
- Modify: `notificador/test_notificador.py`
- Move: `.github/workflows/notificador.yml` → `notificador/notificador.yml`

**Interfaces:**
- Consumes: `extrai(pagina) -> list[dict]` e `combina(item, usuario) -> bool` (já existem).
- Produces:
  - `carrega_usuarios(argv: list[str], env: dict) -> list[dict]`
  - CLI `python3 notificador.py [--perfil ARQ] [--listar]`
  - `--listar` imprime no stdout uma lista JSON de itens `{url, titulo, orgao, detalhe, prazo, estado}`. Com `--perfil`, filtra pelo perfil. Não lê nem grava `vistos.txt` e não envia nada.

- [ ] **Step 1: Escrever o teste que falha**

Acrescentar ao fim de `notificador/test_notificador.py`, antes do `print("ok")`:

```python
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
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `cd notificador && python3 test_notificador.py`
Expected: `ImportError: cannot import name 'carrega_usuarios'`

- [ ] **Step 3: Implementar**

Em `notificador/notificador.py`, atualizar a docstring do topo:

```python
"""Avisa via ntfy quando aparecem concursos novos no PCI Concursos.

Usuarios:
  --perfil arq.json   um perfil so (formato da skill notifica-concurso), ou
  env USUARIOS        lista JSON: [{"topico": "...", "palavras": [...], "estados": [...]}]
palavras/estados vazios ou ausentes = aceita tudo. Outros campos sao ignorados.
--listar imprime os concursos da pagina em JSON (filtrados pelo perfil, se houver) e sai.
Estado dos ja vistos fica em VISTOS (padrao vistos.txt). Sem esse arquivo, so semeia, nao notifica.
DRY=1 imprime em vez de enviar.
"""
```

Acrescentar antes de `main`:

```python
def carrega_usuarios(argv, env):
    if "--perfil" in argv:
        with open(argv[argv.index("--perfil") + 1], encoding="utf-8") as f:
            return [json.load(f)]
    if env.get("USUARIOS"):
        return json.loads(env["USUARIOS"])
    sys.exit("Informe --perfil arquivo.json ou a env USUARIOS.")
```

Trocar o começo de `main` por:

```python
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
```

O resto de `main`, a partir de `primeira_vez = ...`, fica igual. Remover as linhas antigas `usuarios = json.loads(os.environ["USUARIOS"])`, `caminho = ...`, `itens = extrai(...)` e o `if not itens` duplicado.

- [ ] **Step 4: Rodar o teste**

Run: `cd notificador && python3 test_notificador.py`
Expected: `ok`

- [ ] **Step 5: Conferir `--listar` contra a página real**

Run:

```bash
cd notificador && echo '{"topico":"x","palavras":["tecnologia da informacao"]}' > /tmp/p.json && python3 notificador.py --perfil /tmp/p.json --listar | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d), d[0]['titulo'] if d else '')"
```

Expected: um número maior que 0 e um título com "tecnologia da informação".

- [ ] **Step 6: Transformar o workflow em modelo**

```bash
mkdir -p notificador && git mv -f .github/workflows/notificador.yml notificador/notificador.yml 2>/dev/null || mv .github/workflows/notificador.yml notificador/notificador.yml
rmdir -p .github/workflows 2>/dev/null || true
```

Em `notificador/notificador.yml`, trocar o passo de execução por:

```yaml
      - run: python3 notificador.py
        env:
          USUARIOS: ${{ secrets.USUARIOS }}
```

No repositório do candidato, `notificador.py` fica na raiz. Acrescentar como primeira linha do arquivo o comentário:

```yaml
# Modelo copiado pela skill notifica-concurso para o repositório privado do candidato (.github/workflows/).
```

- [ ] **Step 7: Commit**

```bash
git add notificador/
git commit -m "feat: add ntfy contest notifier script with per-profile mode"
```

---

### Task 3: `references/perfil.md` — extração e análise

**Files:**
- Create: `skills/notifica-concurso/references/perfil.md`

**Interfaces:**
- Produces: o formato de `perfil-concurso.md` e as regras que viram `palavras`, `estados` e `resumo`. As Tasks 5 e 6 usam isso.

- [ ] **Step 1: Escrever o arquivo**

````markdown
# Perfil e análise

## Ler a fonte

- **Site pessoal ou portfólio:** WebFetch pedindo "formação, experiência profissional com cargos e datas, habilidades, certificações, cidade".
- **LinkedIn (`linkedin.com/in/...`):** tente o WebFetch uma vez. Se voltar página de login, "Sign in", "Entrar" ou não trouxer experiência, diga:
  > O LinkedIn bloqueia a leitura sem login. Abra seu perfil, clique em **Mais** → **Salvar em PDF** e me passe o caminho do arquivo. Se preferir, cole aqui o texto do perfil.
- **PDF:** Read no arquivo. Se o texto vier vazio (PDF escaneado), peça o texto colado.

## Extrair

| Campo | Exemplo |
|---|---|
| Escolaridade | Superior completo — Bacharelado em Sistemas de Informação |
| Pós/certificações | MBA em Gestão de Projetos; AWS Cloud Practitioner |
| Áreas | Desenvolvimento web, banco de dados |
| Experiência | Desenvolvedor PHP, 4 anos; suporte técnico, 2 anos |
| Cidade/UF | Campinas - SP |

O que não estiver na fonte fica "não informado". Não invente.

## Perguntar o que falta

Uma pergunta por vez, só as que a fonte não respondeu. Sempre com sugestão:

1. Área ou cargos de interesse. Sugira os compatíveis com a formação (ver tabela abaixo).
2. Abrangência: nacional, só alguns estados ou nacional mais o próprio estado.
3. Aceita cargo de escolaridade abaixo da sua? (superior aceitando nível médio/técnico)
4. Aceita mudar de cidade? Se "não", `estados` fica com `NACIONAL` mais a UF dele.
5. Salário mínimo aceitável (R$).

## Compatibilidade formação → cargos (guia, não lista fechada)

| Formação | Cargos típicos em edital |
|---|---|
| TI (SI, CC, ADS, Eng. Computação) | Analista de TI, Analista de Sistemas, Técnico de TI, Analista Judiciário – Apoio Especializado (TI), Auditor de TI |
| Direito | Analista Judiciário – Área Judiciária, Procurador, Delegado, Defensor, Técnico Judiciário |
| Contabilidade/Economia/Administração | Auditor Fiscal, Analista de Controle Externo, Analista Administrativo, Contador |
| Saúde | o próprio cargo da profissão (Enfermeiro, Médico, Farmacêutico) |
| Engenharias | Engenheiro <área>, Analista de Infraestrutura |
| Licenciaturas | Professor <disciplina> |
| Qualquer superior | Analista Administrativo, Técnico (se aceitar nível médio), Agente/Escrivão de Polícia |

## Montar o filtro

- `palavras`: 3 a 8 termos que aparecem em títulos do PCI, sem acento e em minúsculas. Exemplos: `tecnologia da informacao`, `analista de ti`, `analista de sistemas`. Use termos compostos. A palavra solta `ti` casa só com a palavra inteira, mas é ambígua: prefira `analista de ti`. Se o candidato aceita qualquer área, deixe `[]`.
- `estados`: nomes como o PCI usa, sem acento e em maiúsculas (`NACIONAL`, `SAO PAULO`, `DISTRITO FEDERAL`). Nacional total: `[]`.
- `resumo`: uma frase com formação, experiência principal e cidade. É o que o agente diário usa para julgar compatibilidade.
- Mostre ao candidato quantos concursos abertos hoje passam no filtro:
  `python3 <notificador>/notificador.py --perfil <perfil.json> --listar` e conte os itens. Zero: afrouxe as palavras. Mais de 60: aperte.

## `perfil-concurso.md`

```markdown
# Perfil para concursos — <nome>

Gerado em <data>.

## Quem é
<escolaridade, áreas, experiência, cidade>

## Cargos compatíveis
| Cargo | Por quê | Escolaridade exigida |
|---|---|---|

## Pontos fortes para a prova
- <exemplo: experiência em banco de dados conta em Analista de TI, que cobra SQL>

## Lacunas a estudar
- <exemplo: Direito Administrativo e Constitucional, cobrados em quase todo edital de tribunal>

## Filtro de notificação
- Palavras-chave: ...
- Estados: ...
- Salário mínimo: R$ ...
- Concursos abertos hoje que passam no filtro: N

## Concursos abertos agora que combinam
| Órgão | Cargo/vagas | Inscrição até | Link |
|---|---|---|---|
```

A última tabela vem do `--listar`, com até 10 itens, os mais compatíveis primeiro.
````

- [ ] **Step 2: Commit**

```bash
git add skills/notifica-concurso/references/perfil.md
git commit -m "feat: add profile extraction and analysis reference"
```

---

### Task 4: `references/modos.md` — instalação de cada modo

**Files:**
- Create: `skills/notifica-concurso/references/modos.md`

**Interfaces:**
- Consumes: `notificador/notificador.py` (`--perfil`, env `VISTOS`) e `notificador/notificador.yml` (Task 2).
- Produces: os procedimentos `github`, `local` e `claude`, gravados no campo `modo` do `perfil.json`.

- [ ] **Step 1: Escrever o arquivo**

````markdown
# Modos de execução

`<notificador>` = `<base>/../../notificador`, onde `<base>` é o "Base directory for this skill". Resolva para caminho absoluto antes de usar.
`<cfg>` = `~/.config/notifica-concurso`.

## GitHub Actions (`modo: "github"`)

1. `gh auth status`. Se falhar, peça ao candidato para rodar `! gh auth login` e espere.
2. Crie o repositório num diretório temporário:
   ```bash
   T=$(mktemp -d) && cd "$T"
   gh repo create notifica-concurso --private --clone && cd notifica-concurso
   cp "<notificador>/notificador.py" .
   mkdir -p .github/workflows && cp "<notificador>/notificador.yml" .github/workflows/
   git add . && git commit -m "notificador de concursos" && git push -u origin HEAD
   ```
   Se o repositório já existir (erro "Name already exists"), use `gh repo clone notifica-concurso`, sobrescreva os dois arquivos e faça push.
3. Secret com o perfil (lista com um item):
   ```bash
   python3 -c "import json,sys; print(json.dumps([json.load(open(sys.argv[1]))]))" <cfg>/perfil.json | gh secret set USUARIOS -R "$(gh api user -q .login)/notifica-concurso"
   ```
4. `gh workflow run notificador.yml -R <login>/notifica-concurso`. Espere cerca de 1 minuto e rode `gh run list -R <login>/notifica-concurso -L 1`. Tem que dar `completed success`. Essa execução só semeia.
5. Desligar: `gh workflow disable notificador.yml -R <login>/notifica-concurso`.

## Local (`modo: "local"`)

Copie o script: `cp "<notificador>/notificador.py" <cfg>/`. Comando que o agendador roda:
`python3 <cfg>/notificador.py --perfil <cfg>/perfil.json`, com `VISTOS=<cfg>/vistos.txt`. Rode-o uma vez à mão agora (semeia).

### Linux (systemd)

`~/.config/systemd/user/notifica-concurso.service`:
```ini
[Unit]
Description=Notificador de concursos

[Service]
Type=oneshot
Environment=VISTOS=%h/.config/notifica-concurso/vistos.txt
ExecStart=/usr/bin/env python3 %h/.config/notifica-concurso/notificador.py --perfil %h/.config/notifica-concurso/perfil.json
```

`~/.config/systemd/user/notifica-concurso.timer`:
```ini
[Unit]
Description=Notificador de concursos 2x por dia

[Timer]
OnCalendar=*-*-* 08,18:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
systemctl --user daemon-reload && systemctl --user enable --now notifica-concurso.timer
systemctl --user list-timers notifica-concurso.timer   # conferir próxima execução
```
Desligar: `systemctl --user disable --now notifica-concurso.timer`.

### macOS (launchd)

`~/Library/LaunchAgents/br.concurso.notifica.plist` (troque `<HOME>` pelo caminho absoluto):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>br.concurso.notifica</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/python3</string>
    <string><HOME>/.config/notifica-concurso/notificador.py</string>
    <string>--perfil</string><string><HOME>/.config/notifica-concurso/perfil.json</string>
  </array>
  <key>EnvironmentVariables</key><dict>
    <key>VISTOS</key><string><HOME>/.config/notifica-concurso/vistos.txt</string>
  </dict>
  <key>StartCalendarInterval</key><array>
    <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
  </array>
</dict></plist>
```
`launchctl load ~/Library/LaunchAgents/br.concurso.notifica.plist`. Desligar: `launchctl unload` no mesmo arquivo e apagá-lo.

### Windows (Agendador de Tarefas)

Grave `%USERPROFILE%\.config\notifica-concurso\rodar.cmd`:
```bat
@echo off
set VISTOS=%USERPROFILE%\.config\notifica-concurso\vistos.txt
py "%USERPROFILE%\.config\notifica-concurso\notificador.py" --perfil "%USERPROFILE%\.config\notifica-concurso\perfil.json"
```
```bat
schtasks /Create /TN NotificaConcurso08 /SC DAILY /ST 08:00 /TR "%USERPROFILE%\.config\notifica-concurso\rodar.cmd"
schtasks /Create /TN NotificaConcurso18 /SC DAILY /ST 18:00 /TR "%USERPROFILE%\.config\notifica-concurso\rodar.cmd"
```
Desligar: `schtasks /Delete /TN NotificaConcurso08 /F` e o mesmo para `NotificaConcurso18`.

## Claude agendado (`modo: "claude"`)

Só existe se a Task 1 do plano validou o modo (ver spec). Faça o passo 1 a 3 do modo GitHub Actions (o repositório guarda o `vistos.txt`), mas **sem** o workflow: não copie `notificador.yml`. Depois, pela skill `schedule`, crie uma tarefa sobre o repositório `<login>/notifica-concurso`, a cada 12h, com o prompt de `references/agente-diario.md` e os campos do perfil preenchidos. Desligar: apagar a tarefa pela skill `schedule`.
````

- [ ] **Step 2: Conferir o systemd neste Fedora**

Run: `systemd-analyze verify` nos dois arquivos gravados num diretório temporário com o conteúdo acima. `%h` é válido em unidade de usuário.
Expected: sem erros (avisos sobre `/usr/bin/env` são aceitáveis).

- [ ] **Step 3: Commit**

```bash
git add skills/notifica-concurso/references/modos.md
git commit -m "feat: add install procedures for each notifier mode"
```

---

### Task 5: `references/agente-diario.md` (só se a Task 1 validou o modo Claude)

**Files:**
- Create: `skills/notifica-concurso/references/agente-diario.md`

**Interfaces:**
- Consumes: `notificador.py --perfil --listar` (Task 2) e o campo `resumo` (Task 3).

- [ ] **Step 1: Escrever o arquivo**

````markdown
# Prompt do agente diário

A skill preenche os `<...>` com o perfil e cria a tarefa agendada com este texto:

---

Você verifica concursos novos para um candidato e avisa pelo ntfy. Trabalhe no repositório atual.

Perfil: <resumo>. Palavras-chave: <palavras>. Estados: <estados>. Salário mínimo: R$ <salario_minimo>. Tópico ntfy: <topico>.

1. `curl -fsSL https://raw.githubusercontent.com/guglieelmor/estudo-concurso/main/notificador/notificador.py -o notificador.py`
2. Grave o perfil em `perfil.json` (os campos acima) e rode `python3 notificador.py --perfil perfil.json --listar > hoje.json`.
3. Se `vistos.txt` não existir: grave nele as `url` de `hoje.json`, uma por linha, faça commit e pare (primeira execução, só semeia).
4. Novos = itens de `hoje.json` cuja `url` não está em `vistos.txt`. Para cada novo, decida se combina com o perfil (cargo compatível com a formação, escolaridade, estado, salário "até R$ X" maior ou igual ao mínimo quando houver). Na dúvida, avise.
5. Para cada um que combina:
   `curl -s -H "Title: <orgao> (<estado>)" -H "Click: <url>" -H "Tags: mega" -d "<detalhe> — até <prazo>. Por que combina: <uma frase>" https://ntfy.sh/<topico>`
6. Regrave `vistos.txt` com as `url` de `hoje.json`, apague `hoje.json` e `notificador.py`, faça commit ("vistos <data>") e push.

Não altere nada além de `vistos.txt` e `perfil.json`.
````

- [ ] **Step 2: Commit**

```bash
git add skills/notifica-concurso/references/agente-diario.md
git commit -m "feat: add daily scheduled-agent prompt"
```

---

### Task 6: `SKILL.md`, manifesto do plugin e README

**Files:**
- Create: `skills/notifica-concurso/SKILL.md`
- Modify: `.claude-plugin/plugin.json` (`description`, `keywords`)
- Modify: `.claude-plugin/marketplace.json` (`description` do plugin)
- Modify: `README.md` (nova seção antes de "## Cuidados")

**Interfaces:**
- Consumes: `references/perfil.md` (Task 3), `references/modos.md` (Task 4), `references/agente-diario.md` (Task 5, se existir), `notificador.py --perfil/--listar` (Task 2) e `skills/concurso/references/pdf.md`.

- [ ] **Step 1: Escrever `skills/notifica-concurso/SKILL.md`**

````markdown
---
name: notifica-concurso
description: Use quando o candidato quiser ser avisado de concursos públicos abertos que combinem com o perfil dele, ou rodar /notifica-concurso para criar, editar ou desligar o aviso. Recebe LinkedIn, site pessoal ou currículo em PDF, analisa o perfil e instala um verificador diário com push no celular (ntfy).
argument-hint: [url-do-linkedin | url-do-site | caminho-do-curriculo.pdf]
---

# Notificação de concursos

Monta o perfil do candidato, gera uma análise de concursos compatíveis e instala um verificador que avisa no celular quando abre um concurso que combina.

Argumento recebido: `$ARGUMENTS`

`<base>` = o "Base directory for this skill". `<notificador>` = `<base>/../../notificador` (caminho absoluto). `<cfg>` = `~/.config/notifica-concurso`.

## Antes de tudo: já configurado?

Se `<cfg>/perfil.json` existir, mostre o resumo, as palavras, os estados e o modo e pergunte: **editar** (vá à fase 3 com o perfil atual, mantém o tópico), **recomeçar** (fase 1) ou **desligar** (procedimento "Desligar" do modo em `references/modos.md`, depois apague `<cfg>`).

## Fases

1. **Perfil.** Sem argumento, peça: "Me passe o link do seu LinkedIn, do seu site pessoal ou o caminho do seu currículo em PDF." Leia conforme `references/perfil.md`.
2. **Extrair** os campos de `references/perfil.md` e mostrar ao candidato numa tabela.
3. **Perguntas complementares**, uma por vez, conforme `references/perfil.md`.
4. **Análise.** Monte o filtro e o `perfil-concurso.md` conforme `references/perfil.md`, no diretório atual. Mostre e ajuste até o "ok". Com o "ok", gere `perfil-concurso.pdf` seguindo `<base>/../concurso/references/pdf.md`.
5. **Gravar** `<cfg>/perfil.json` com `topico`, `palavras`, `estados`, `salario_minimo`, `resumo` (o `modo` entra na fase 7). Tópico novo: `concursos-` mais `python3 -c "import secrets; print(secrets.token_hex(4))"`.
6. **ntfy.** Explique:
   > Instale o app **ntfy** (Play Store, App Store ou F-Droid), toque em **+** e assine o tópico `<topico>`. Esse nome funciona como senha: quem souber recebe seus avisos.

   Depois mande o teste: `curl -s -H "Title: Teste" -d "Notificação de concursos configurada" https://ntfy.sh/<topico>`. Pergunte se chegou. Não siga sem confirmação. Se não chegou, confira o nome do tópico no app.
7. **Onde rodar.** Pergunte, com prós e contras:
   - **GitHub Actions:** roda com o PC desligado e não gasta seu plano Claude. Precisa de conta no GitHub. Filtra por palavra-chave.
   - **No seu computador:** não precisa de conta. Só roda com o PC ligado. Filtra por palavra-chave.
   - **Agente Claude agendado** (só se `references/agente-diario.md` existir): avalia cada concurso contra o seu perfil e diz por que combina. Gasta uso do seu plano Claude a cada execução e precisa de conta no GitHub.

   Instale conforme `references/modos.md` e grave o `modo` em `perfil.json`.
8. **Fechar.** Diga: modo instalado, horários (8h e 18h), que a primeira execução só registra os concursos já abertos (os que já existem estão no `perfil-concurso.pdf`) e que `/notifica-concurso` de novo edita ou desliga.

## Erros comuns

- Inventar formação ou experiência que não está na fonte.
- Seguir sem o candidato confirmar que o push de teste chegou.
- Gravar o tópico em arquivo dentro de repositório público.
- Deixar `palavras` com um termo curto e ambíguo sozinho (`ti`, `adm`).
````

- [ ] **Step 2: Atualizar os manifestos**

`.claude-plugin/plugin.json`:

```json
{
  "name": "concurso",
  "description": "Lê o edital de um concurso público e gera cronograma diário, conteúdo da web e simulado com gabarito para cada dia até a prova. Também avisa no celular quando abre um concurso compatível com o seu perfil.",
  "author": { "name": "guglieelmor" },
  "repository": "https://github.com/guglieelmor/estudo-concurso",
  "keywords": ["concurso", "edital", "estudo", "simulado", "cronograma", "notificacao"]
}
```

Em `.claude-plugin/marketplace.json`, mesma `description` no item do plugin `concurso`.

- [ ] **Step 3: Seção no README, antes de `## Cuidados`**

```markdown
## Aviso de concursos abertos

Rode `/notifica-concurso` com o link do seu LinkedIn, do seu site ou o caminho do seu currículo em PDF. A skill:

1. lê seu perfil e pergunta o que faltar (área, estados, salário mínimo);
2. gera `perfil-concurso.pdf` com os cargos que combinam com você, seus pontos fortes, as lacunas a estudar e os concursos abertos hoje;
3. configura o app **ntfy** no seu celular e manda um aviso de teste;
4. instala um verificador que roda às 8h e às 18h, no GitHub Actions ou no seu computador, você escolhe.

Rode `/notifica-concurso` de novo para editar o perfil ou desligar os avisos.
```

- [ ] **Step 4: Validar o manifesto**

Run: `python3 -m json.tool .claude-plugin/plugin.json >/dev/null && python3 -m json.tool .claude-plugin/marketplace.json >/dev/null && echo ok`
Expected: `ok`

- [ ] **Step 5: Commit**

```bash
git add skills/notifica-concurso/SKILL.md .claude-plugin/ README.md
git commit -m "feat: add notifica-concurso skill"
```

---

### Task 7: Teste ponta a ponta

**Files:** nenhum (só verificação; correções voltam à task de origem).

- [ ] **Step 1: Instalar o plugin local**

No Claude Code, dentro deste repositório: `/plugin marketplace add ./` e depois `/plugin install concurso@estudo-concurso` (ou update, se já instalado). Reinicie a sessão.

- [ ] **Step 2: Caminho do LinkedIn**

`/notifica-concurso https://www.linkedin.com/in/<qualquer-perfil>`. Esperado: a skill detecta o bloqueio e pede o PDF ou o texto colado.

- [ ] **Step 3: Caminho do PDF, modo local**

Passe um currículo em PDF, responda às perguntas e escolha "No seu computador". Esperado:
- `perfil-concurso.pdf` com cabeçalho `%PDF` no diretório atual;
- push de teste recebido;
- `systemctl --user list-timers notifica-concurso.timer` mostra a próxima execução;
- `<cfg>/vistos.txt` existe (semeado).

Para forçar um aviso: `sed -i '1,3d' ~/.config/notifica-concurso/vistos.txt && systemctl --user start notifica-concurso.service`. Chega push se algum dos 3 removidos passa no filtro. Senão, `journalctl --user -u notifica-concurso -n 5` mostra `0 notificado(s)`.

- [ ] **Step 4: Reexecução**

`/notifica-concurso` sem argumento. Esperado: oferece editar, recomeçar ou desligar. Escolha desligar e confira que o timer sumiu e `<cfg>` foi apagado.

- [ ] **Step 5: Modo GitHub Actions** (se houver `gh` autenticado)

Repita a fase 7 escolhendo GitHub Actions. Esperado: repositório privado `notifica-concurso` criado, `gh run list` com `completed success`, `gh secret list` mostrando `USUARIOS`. Depois desligue pela skill.
