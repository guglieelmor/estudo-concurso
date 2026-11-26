# Notificador de concursos (skill `notifica-concurso`) — Design

Data: 2026-11-26
Status: aprovado em brainstorming, aguardando revisão da spec

## Objetivo

Skill `/notifica-concurso` no mesmo plugin `concurso`. Ela monta o perfil do candidato a partir do LinkedIn, de um site pessoal ou do currículo, faz perguntas complementares, gera uma análise de quais concursos combinam com esse perfil e configura uma notificação no celular (ntfy) sempre que um concurso compatível aparecer.

A skill é self-service: cada pessoa que instala o plugin configura o próprio perfil e escolhe onde o verificador diário roda.

## Fora de escopo (v1)

- Rodar `/concurso` automaticamente quando chegar um edital.
- Canais além do ntfy (Telegram, e-mail).
- Fontes além do PCI Concursos.
- Filtro por salário no script (o PCI só mostra "até R$ X"). O salário mínimo informado entra na análise e no modo Claude agendado, mas não no filtro por palavra-chave.
- Vários perfis por máquina. Rodar a skill de novo substitui o perfil.

## Público

Qualquer pessoa que instale o plugin, sem experiência técnica presumida. Dependências: Claude Code, Python 3 (só para os modos GitHub Actions e local) e o app ntfy no celular.

## Estrutura

```
skills/notifica-concurso/
├── SKILL.md                  # orquestrador: fases e perguntas
└── references/
    ├── perfil.md             # como extrair o perfil e o formato da análise
    ├── modos.md              # instalação de cada modo de execução
    └── agente-diario.md      # prompt do agente agendado (modo Claude)
notificador/
├── notificador.py            # verificador determinístico (já existe)
├── test_notificador.py
└── notificador.yml           # modelo de workflow, copiado para o repo do candidato
```

O `.github/workflows/notificador.yml` sai da raiz deste repositório e vira `notificador/notificador.yml`. Este repositório não roda notificação para ninguém.

## Fases da skill

1. **Obter o perfil.** O argumento (ou a resposta à pergunta) pode ser:
   - URL de site pessoal ou portfólio: WebFetch.
   - URL do LinkedIn: tenta o WebFetch. Se vier página de login ou conteúdo vazio, explica que o LinkedIn bloqueia leitura e pede o PDF do perfil (no LinkedIn: "Mais" → "Salvar em PDF") ou o texto colado no chat.
   - Caminho de PDF ou texto colado: Read direto.
2. **Extrair** escolaridade (nível e curso), áreas de atuação, experiência (cargos e tempo), certificações, cidade e UF. Seguir `references/perfil.md`.
3. **Perguntas complementares**, uma por vez, só as que o perfil não responder:
   - área ou cargos de interesse (sugerir a partir do perfil);
   - abrangência: nacional, estados específicos ou nacional mais o próprio estado;
   - aceita cargo de escolaridade abaixo da formação (exemplo: superior aceitando técnico de nível médio);
   - aceita mudar de cidade;
   - salário mínimo aceitável.
4. **Análise.** Gerar `perfil-concurso.md` com cargos compatíveis e o motivo, pontos fortes, lacunas a estudar e o filtro resultante (palavras-chave e estados). Mostrar ao candidato e ajustar até ele dar "ok". Depois do "ok", gerar `perfil-concurso.pdf` com o mesmo método de PDF da skill `concurso` (`skills/concurso/references/pdf.md`). Os dois arquivos ficam no diretório atual.
5. **Gravar o perfil** em `~/.config/notifica-concurso/perfil.json`:
   ```json
   {
     "topico": "concursos-8f3k2x9q",
     "palavras": ["tecnologia da informacao", "analista de ti"],
     "estados": ["NACIONAL", "SAO PAULO"],
     "salario_minimo": 5000,
     "resumo": "Bacharel em ADS, 4 anos como desenvolvedor PHP, mora em Campinas-SP"
   }
   ```
   `palavras` e `estados` seguem as regras do `notificador.py`: vazio aceita tudo, sem diferença de acento e maiúscula, `estados` pelo nome usado no PCI (`NACIONAL`, `SAO PAULO`).
6. **Configurar o ntfy.** Gerar `topico` aleatório (`concursos-` mais 8 caracteres de `secrets.token_hex` ou `/dev/urandom`). Explicar a instalação do app e a assinatura do tópico. Mandar um push de teste com `curl` e perguntar se chegou. Sem confirmação, não segue. Avisar que quem souber o tópico recebe os avisos.
7. **Escolher o modo de execução** (pergunta com as três opções e os prós e contras de cada uma) e instalar conforme `references/modos.md`.
8. **Fechar.** Resumir o perfil, o modo escolhido e como desligar.

## Modos de execução

### Claude agendado

- A skill `schedule` do Claude Code cria uma tarefa diária na conta do candidato, com o prompt de `references/agente-diario.md` e o perfil embutido.
- O agente baixa `https://www.pciconcursos.com.br/concursos/`, separa os concursos novos e avalia cada um contra o `resumo`, as palavras-chave, os estados e o salário mínimo. Para cada compatível, manda um push com uma linha de motivo ("Analista de TI, nível superior: bate com sua formação em ADS").
- Para saber o que já foi avisado, consulta o histórico do próprio tópico no ntfy (`/<topico>/json?poll=1&since=…`). O ntfy.sh guarda mensagens por cerca de 12h, então o agendamento roda a cada 12h.
- **Pré-condição a validar no plano:** confirmar que a tarefa agendada em nuvem tem acesso à web e pode fazer POST no ntfy. Se não tiver, este modo sai da v1 e a skill oferece só os outros dois.
- Contra: gasta uso do plano Claude a cada execução.

### GitHub Actions

- Exige `gh` autenticado. A skill confere com `gh auth status` e, se faltar, orienta o `! gh auth login`.
- Cria um repositório privado `notifica-concurso` na conta do candidato, com `notificador.py` e `.github/workflows/notificador.yml` copiados de `notificador/`.
- Grava o perfil como secret `USUARIOS` (lista com um único perfil) via `gh secret set` e dispara a primeira execução com `gh workflow run`. Essa primeira execução só semeia.
- Filtro só por palavra-chave e estado. Não gasta Claude. Funciona com o PC desligado.

### Local

- Linux: systemd user timer (`~/.config/systemd/user/notifica-concurso.{service,timer}`), 2x por dia, `Persistent=true` para rodar a execução perdida quando o PC ligar.
- macOS: `launchd` (`~/Library/LaunchAgents`).
- Windows: Agendador de Tarefas via `schtasks`.
- O script e a lista de vistos ficam em `~/.config/notifica-concurso/`.
- Contra: só roda com o PC ligado.

## Mudanças no `notificador.py`

- Aceitar `--perfil caminho.json`, com um perfil só, como alternativa à env `USUARIOS`. Campos extras (`salario_minimo`, `resumo`) são ignorados.
- Resto sem mudança: mesma fonte, mesma deduplicação e mesma semeadura na primeira execução.

## Reexecução

Se `~/.config/notifica-concurso/perfil.json` já existir, a skill mostra o perfil atual e pergunta:

- **editar:** volta à fase 3 e mantém o tópico;
- **recomeçar:** volta à fase 1;
- **desligar:** remove o agendamento do modo instalado e o arquivo.

O modo instalado fica gravado no próprio `perfil.json` (campo `modo`).

## Testes

- `test_notificador.py` passa a cobrir também `--perfil`.
- Teste manual de cada modo: semear, apagar 3 linhas de `vistos.txt` e conferir o push.
- Teste da skill: rodar com um PDF de currículo de exemplo e com uma URL do LinkedIn, para cobrir o caminho do bloqueio.

## Riscos

- Mudança de layout do PCI quebra o script, que falha com uma mensagem clara. O modo Claude é mais tolerante.
- Tópico do ntfy vazado: qualquer um lê os avisos ou manda spam. A mitigação é o tópico aleatório. Para trocar, basta rodar a skill de novo e escolher "editar".
