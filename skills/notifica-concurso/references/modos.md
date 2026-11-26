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
