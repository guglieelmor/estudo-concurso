---
name: notifica-edital
description: Use quando o candidato quiser ser avisado no celular assim que sair o edital de um concurso específico (ex. "me avisa quando abrir o edital da PF"), informando o site onde os editais são publicados, ou rodar /notifica-edital para adicionar, listar, remover ou desligar essas vigias. Instala um verificador 2x por dia com push no celular (ntfy).
argument-hint: [url-do-site] [edital que quer acompanhar]
---

# Notificação de edital

Vigia um site que publica editais (portal de notícias de concurso, página da banca, página do órgão) e manda push no celular quando aparece o edital de um concurso específico. Cada par site + edital é uma **vigia**; o candidato pode ter várias.

Argumento recebido: `$ARGUMENTS`

`<base>` = o "Base directory for this skill". `<notificador>` = `<base>/../../notificador` (caminho absoluto). `<cfg>` = `~/.config/notifica-edital`. `<script>` = `<cfg>/vigia_edital.py` depois de instalado, `<notificador>/vigia_edital.py` antes.

No Windows (Bash do Claude Code = Git Bash): use `py` no lugar de `python3`, rode `schtasks` como `MSYS_NO_PATHCONV=1 schtasks ...` e semeie pelo `rodar.cmd` (detalhes em `references/modos.md`).

## Antes de tudo: já configurado?

Se `<cfg>/vigias.json` existir, mostre as vigias numa tabela (nome, site, termos) e o modo.
- Se o argumento trouxer site e edital, vá direto à fase 1 para **adicionar** uma vigia.
- Sem argumento, pergunte: **adicionar** vigia, **remover** vigia (apague do `vigias.json` e vá à fase 6), **desligar tudo** (procedimento "Desligar" do modo em `references/modos.md`, depois apague `<cfg>`).

## Fases

1. **Site e edital.** Do argumento, separe a URL do site e a descrição do edital. Faltando algo, pergunte, uma coisa por vez: "Qual o link do site onde o edital vai ser publicado?" e "Qual edital você quer acompanhar? (órgão, cargo, ano, se souber)".
2. **Termos.** Monte a vigia conforme `references/vigia.md` (nome, termos com siglas e variações, gatilhos). Mostre ao candidato.
3. **Testar no site.** Rode `TERMOS='<termos em JSON>' python3 <notificador>/vigia_edital.py --listar --url <url>` (com gatilhos próprios, acrescente `GATILHOS_TESTE='<gatilhos em JSON>'`) e interprete conforme `references/vigia.md`:
   - `links_na_pagina` 0 ou erro: o site não serve para o verificador. Siga a seção "Site não funciona" de `references/vigia.md`.
   - Algo combina: mostre. Se for o edital que ele quer, **avise já** que o edital parece aberto e pergunte se ainda quer a vigia (para retificações). Se for coisa antiga ou errada, ajuste os termos e teste de novo.
   - Nada combina: normal se o edital ainda não saiu. Rode com `--todos` e confira se os títulos dos links parecem notícias/editais (se só houver menu, a página está errada).
   Ajuste até o candidato dar "ok".
4. **Gravar** em `<cfg>/vigias.json` (formato em `references/vigia.md`). Primeira vez: tópico novo `editais-` mais `python3 -c "import secrets; print(secrets.token_hex(4))"`. Nome de vigia repetido: peça outro.
5. **ntfy** (só na primeira vez). Explique:
   > Instale o app **ntfy** (Play Store, App Store ou F-Droid), toque em **+** e assine o tópico `<topico>`. Esse nome funciona como senha: quem souber recebe seus avisos.

   Se o candidato já usa a `notifica-concurso`, ofereça reaproveitar o tópico de `~/.config/notifica-concurso/perfil.json` (aí não precisa assinar de novo).
   Mande o teste: `curl -s -H "Title: Teste" -d "Notificação de edital configurada" https://ntfy.sh/<topico>`. Pergunte se chegou. Não siga sem confirmação.
6. **Onde rodar.** Primeira vez: pergunte, com prós e contras:
   - **GitHub Actions:** roda com o PC desligado e não gasta seu plano Claude. Precisa de conta no GitHub.
   - **No seu computador:** não precisa de conta. Só roda com o PC ligado.

   Instale conforme `references/modos.md` e grave o `modo` em `vigias.json`. Já instalado: no modo local nada a refazer (o script lê o `vigias.json`); no modo github, regrave o secret (passo 3 de `references/modos.md`). Nos dois, rode uma vez para semear a vigia nova.
7. **Fechar.** Diga: vigias ativas, horários (8h e 18h), que a primeira execução de cada vigia só registra o que já está no site (por isso o teste da fase 3) e que `/notifica-edital` de novo adiciona, remove ou desliga.

## Erros comuns

- Termo curto sozinho e ambíguo (`pf` casa com notícia de operação da PF; o gatilho `edital` ajuda, mas some cargo ou ano quando der).
- Esquecer a sigla ou o nome por extenso (`policia federal|pf`): o site pode usar só um dos dois.
- Gravar vigia sem testar no site: página que exige JavaScript nunca vai avisar.
- Seguir sem o candidato confirmar que o push de teste chegou.
- Gravar o tópico em arquivo dentro de repositório público.
