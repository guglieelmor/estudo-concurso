---
name: notifica-concurso
description: Use quando o candidato quiser ser avisado de concursos públicos abertos que combinem com o perfil dele, ou rodar /notifica-concurso para criar, editar ou desligar o aviso. Recebe LinkedIn, site pessoal ou currículo em PDF, analisa o perfil e instala um verificador diário com push no celular (ntfy).
argument-hint: [url-do-linkedin | url-do-site | caminho-do-curriculo.pdf]
---

# Notificação de concursos

Monta o perfil do candidato, gera uma análise de concursos compatíveis e instala um verificador que avisa no celular quando abre um concurso que combina.

Argumento recebido: `$ARGUMENTS`

`<base>` = o "Base directory for this skill". `<notificador>` = `<base>/../../notificador` (caminho absoluto). `<cfg>` = `~/.config/notifica-concurso`.

No Windows (Bash do Claude Code = Git Bash): use `py` no lugar de `python3`, rode `schtasks` como `MSYS_NO_PATHCONV=1 schtasks ...` e semeie pelo `rodar.cmd` (detalhes em `references/modos.md`).

## Antes de tudo: já configurado?

Se `<cfg>/perfil.json` existir, mostre o resumo, as palavras, os estados e o modo e pergunte: **editar** (vá à fase 3 com o perfil atual, mantém o tópico), **recomeçar** (fase 1) ou **desligar** (procedimento "Desligar" do modo em `references/modos.md`, depois apague `<cfg>`).

Em editar/recomeçar: se o modo mudar, rode antes o "Desligar" do modo anterior; no modo github, sempre regrave o secret (passo 3 de `references/modos.md`). No modo local, o script lê o `perfil.json` direto, nada a refazer.

Modo github: os avisos de todas as skills ficam num único repositório privado, `notifica-estudo-concurso`. Se o candidato ainda tiver o repositório antigo desta skill, ofereça migrar (seção "Repositório antigo" de `references/modos.md`).

## Fases

1. **Perfil.** Sem argumento, peça: "Me passe o link do seu LinkedIn, do seu site pessoal ou o caminho do seu currículo em PDF." Leia conforme `references/perfil.md`.
2. **Extrair** os campos de `references/perfil.md` e mostrar ao candidato numa tabela.
3. **Perguntas complementares**, uma por vez, conforme `references/perfil.md`.
4. **Análise.** Monte o filtro e o `perfil-concurso.md` conforme `references/perfil.md`, no diretório atual (se for um repositório git, `git rev-parse --is-inside-work-tree`, avise que `perfil-concurso.*` tem dados do currículo e não deve ir para repositório público). Mostre e ajuste até o "ok". Com o "ok", gere `perfil-concurso.pdf` seguindo `<base>/../concurso/references/pdf.md`.
5. **Gravar** `<cfg>/perfil.json` com `topico`, `palavras`, `estados`, `salario_minimo`, `resumo` (o `modo` entra na fase 7). Tópico novo: `concursos-` mais `python3 -c "import secrets; print(secrets.token_hex(4))"`.
6. **ntfy.** Explique:
   > Instale o app **ntfy** (Play Store, App Store ou F-Droid), toque em **+** e assine o tópico `<topico>`. Esse nome funciona como senha: quem souber recebe seus avisos.

   Depois mande o teste: `curl -s -H "Title: Teste" -d "Notificação de concursos configurada" https://ntfy.sh/<topico>`. Pergunte se chegou. Não siga sem confirmação. Se não chegou, confira o nome do tópico no app.
7. **Onde rodar.** Pergunte, com prós e contras:
   - **GitHub Actions:** roda com o PC desligado e não gasta seu plano Claude. Precisa de conta no GitHub. Filtra por palavra-chave.
   - **No seu computador:** não precisa de conta. Só roda com o PC ligado. Filtra por palavra-chave.

   Instale conforme `references/modos.md` e grave o `modo` em `perfil.json`.
8. **Fechar.** Diga: modo instalado, horários (8h e 18h), que a primeira execução só registra os concursos já abertos (os que já existem estão no `perfil-concurso.pdf`) e que `/notifica-concurso` de novo edita ou desliga.

## Erros comuns

- Inventar formação ou experiência que não está na fonte.
- Seguir sem o candidato confirmar que o push de teste chegou.
- Gravar o tópico em arquivo dentro de repositório público.
- Deixar `palavras` com um termo curto e ambíguo sozinho (`ti`, `adm`).
