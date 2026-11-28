# Modos de execução

`<notificador>` = `<base>/../../notificador`, onde `<base>` é o "Base directory for this skill". Resolva para caminho absoluto antes de usar.
`<cfg>` = `~/.config/notifica-edital`.

## GitHub Actions (`modo: "github"`)

1. `gh auth status`. Se o `gh` não existir, peça para instalar em https://cli.github.com. Se falhar, peça ao candidato para rodar `! gh auth login -s workflow` e espere. Se `Token scopes` não tiver `workflow` (o push do `.yml` é recusado sem ele), peça `! gh auth refresh -s workflow`.
2. Prepare o repositório único `notifica-estudo-concurso`, compartilhado por todas as skills de aviso (cada uma tem o próprio script, workflow e secret lá dentro). Num diretório temporário:
   ```bash
   T=$(mktemp -d) && cd "$T"
   if gh repo view notifica-estudo-concurso >/dev/null 2>&1; then gh repo clone notifica-estudo-concurso; else gh repo create notifica-estudo-concurso --private --clone; fi
   cd notifica-estudo-concurso
   ```
   Se o repositório já existia, confira `gh repo view notifica-estudo-concurso --json visibility -q .visibility` e **pare** se não for `PRIVATE`. Mexa só nos seus arquivos; os de outras skills (`notificador.py`, `vigia_edital.py` e seus `.yml`) ficam como estão.
   ```bash
   cp "<notificador>/vigia_edital.py" .
   mkdir -p .github/workflows && cp "<notificador>/vigia_edital.yml" .github/workflows/
   git add vigia_edital.py .github/workflows/vigia_edital.yml
   git diff --cached --quiet || git commit -m "vigia de edital"
   git push -u origin HEAD
   ```
3. Secret com as vigias (o próprio `vigias.json`). Rode também sempre que adicionar ou remover vigia:
   ```bash
   gh secret set VIGIAS -R "$(gh api user -q .login)/notifica-estudo-concurso" < <cfg>/vigias.json
   ```
4. `gh workflow run vigia_edital.yml -R <login>/notifica-estudo-concurso`. Espere cerca de 1 minuto e rode `gh run list -R <login>/notifica-estudo-concurso -L 1`. Tem que dar `completed success`. Essa execução só semeia as vigias novas.
   Se falhar, `gh run view <id> -R <login>/notifica-estudo-concurso --log` mostra qual vigia deu problema (site bloqueando o GitHub, por exemplo: troque a página ou use o modo local).
5. Desligar: `gh workflow disable vigia_edital.yml -R <login>/notifica-estudo-concurso` e `gh secret delete VIGIAS -R <login>/notifica-estudo-concurso`. Só este aviso: os de outras skills no mesmo repositório continuam.

### Repositório antigo `notifica-edital`

Versões anteriores criavam um repositório só para esta skill. Se `gh repo view notifica-edital` existir, ofereça migrar: faça os passos 2 a 4 acima (repositório `notifica-estudo-concurso`) e depois desligue o antigo com `gh workflow disable vigia_edital.yml -R <login>/notifica-edital`. Não apague o repositório antigo por conta própria; diga ao candidato que, conferido o novo, ele pode apagá-lo no GitHub em Settings → Delete this repository.

## Local (`modo: "local"`)

Copie o script: `cp "<notificador>/vigia_edital.py" <cfg>/`. Comando que o agendador roda:
`python3 <cfg>/vigia_edital.py --config <cfg>/vigias.json`, com `VISTOS=<cfg>/vistos.json`. Rode-o uma vez à mão agora (semeia) e sempre que adicionar vigia. No Windows, semeie pelo `rodar.cmd` (abaixo).

### Linux (systemd)

`~/.config/systemd/user/notifica-edital.service`:
```ini
[Unit]
Description=Vigia de edital

[Service]
Type=oneshot
Environment=VISTOS=%h/.config/notifica-edital/vistos.json
ExecStart=/usr/bin/env python3 %h/.config/notifica-edital/vigia_edital.py --config %h/.config/notifica-edital/vigias.json
```

`~/.config/systemd/user/notifica-edital.timer`:
```ini
[Unit]
Description=Vigia de edital 2x por dia

[Timer]
OnCalendar=*-*-* 08,18:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
systemctl --user daemon-reload && systemctl --user enable --now notifica-edital.timer
systemctl --user list-timers notifica-edital.timer   # conferir próxima execução
```
Desligar: `systemctl --user disable --now notifica-edital.timer`.

### macOS (launchd)

`~/Library/LaunchAgents/br.concurso.edital.plist` (troque `<HOME>` pelo caminho absoluto):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>br.concurso.edital</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/python3</string>
    <string><HOME>/.config/notifica-edital/vigia_edital.py</string>
    <string>--config</string><string><HOME>/.config/notifica-edital/vigias.json</string>
  </array>
  <key>EnvironmentVariables</key><dict>
    <key>VISTOS</key><string><HOME>/.config/notifica-edital/vistos.json</string>
  </dict>
  <key>StartCalendarInterval</key><array>
    <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
  </array>
</dict></plist>
```
Se `command -v python3` não for `/usr/bin/python3`, troque pelo caminho que ele mostrar.
`launchctl load ~/Library/LaunchAgents/br.concurso.edital.plist`. Desligar: `launchctl unload` no mesmo arquivo e apagá-lo.

### Windows (Agendador de Tarefas)

No Git Bash do Claude Code: `py` no lugar de `python3`; `schtasks` como `MSYS_NO_PATHCONV=1 schtasks ...` (senão `/Create` vira caminho); `/TR` com aspas internas, que aguentam espaços. Semeie rodando o próprio `rodar.cmd`: `cmd //c "%USERPROFILE%\.config\notifica-edital\rodar.cmd"`.

Grave `%USERPROFILE%\.config\notifica-edital\rodar.cmd`:
```bat
@echo off
set VISTOS=%USERPROFILE%\.config\notifica-edital\vistos.json
py "%USERPROFILE%\.config\notifica-edital\vigia_edital.py" --config "%USERPROFILE%\.config\notifica-edital\vigias.json"
```
```bat
schtasks /Create /TN NotificaEdital08 /SC DAILY /ST 08:00 /TR "\"%USERPROFILE%\.config\notifica-edital\rodar.cmd\""
schtasks /Create /TN NotificaEdital18 /SC DAILY /ST 18:00 /TR "\"%USERPROFILE%\.config\notifica-edital\rodar.cmd\""
```
Desligar: `schtasks /Delete /TN NotificaEdital08 /F` e o mesmo para `NotificaEdital18`.
