---
name: concurso
description: Use quando o estudante passar o edital de um concurso público (PDF local ou URL) e quiser um plano de estudo até a prova, ou quando rodar /concurso dentro de (ou apontando para) uma pasta de concurso já gerada para continuar a geração. Gatilhos - edital, concurso público, cronograma de estudo, simulado, banca Cebraspe/FGV/FCC/Vunesp.
argument-hint: <caminho-do-edital.pdf | url-do-edital | pasta-do-concurso>
---

# Estudo para concurso público

Gera, a partir do edital, todo o material de estudo até a véspera da prova: resumo do edital, cronograma diário e, para cada dia, conteúdo com fontes, simulado no estilo da banca e gabarito comentado. Tudo em markdown (mais o resumo do edital em PDF), numa pasta por concurso, no diretório atual.

Argumento recebido: `$ARGUMENTS`

## Antes de tudo: novo ou retomada?

Se o argumento (ou o diretório atual, quando não há argumento) for uma pasta que contém `edital.md` e `cronograma.md`, é **retomada**: pule para a fase 7. Não releia o edital.

Sem argumento e sem pasta de concurso no diretório atual: peça o caminho ou a URL do edital.

## Fases

1. **Obter o edital.**
   - Caminho local: confirme que o arquivo existe.
   - URL: `curl -fsSL "<url>" -o "<scratch>/edital.pdf"` e confira o cabeçalho com `head -c 4 <arquivo>`. Se não for `%PDF`, pare e diga ao estudante que o link não é um PDF direto.
2. **Ler o edital** seguindo `references/edital.md`. Se houver mais de um cargo, pergunte qual é o do estudante antes de continuar. Se o texto não sair (PDF escaneado), avise e pare.
3. **Criar a pasta do concurso** (regras de nome abaixo), copiar o PDF para `edital.pdf` e gravar `edital.md`.
4. **Confirmação 1.** Mostre cargo, banca, data da prova e a tabela de matérias (questões, peso, tipo). Data da prova ausente no edital: pergunte. Corrija o `edital.md` com o que o estudante apontar. Só siga com o "ok" dele. Com o "ok", gere `edital-resumido.pdf` conforme `references/edital.md`.
5. **Gerar `cronograma.md`** seguindo `references/cronograma.md`.
6. **Confirmação 2.** Mostre total de dias, dias por matéria, dias de revisão, reserva final e os avisos de falta de tempo. Avise que serão gerados N dias com busca na web, o que leva tempo e consome bastante uso. Só siga com o "ok" dele.
7. **Gerar os dias de conteúdo.** Liste os dias do tipo `conteúdo` cuja pasta não tem os três arquivos finais (`conteudo.md`, `simulado.md`, `gabarito.md`). Agrupe em blocos de até 7 dias e dispare um subagente (Agent, `general-purpose`) por bloco, no máximo 5 ao mesmo tempo. O prompt de cada um contém:
   - o caminho absoluto da pasta do concurso;
   - as linhas do bloco no cronograma (dia, data, tipo, matérias, códigos);
   - a instrução: "Leia `<pasta do concurso>/edital.md` e siga à risca `<base>/references/dia.md`.", onde `<base>` é o "Base directory for this skill" mostrado ao carregar esta skill (caminho absoluto, já resolvido).
8. **Gerar os dias de revisão e de revisão final**, mesma forma, depois que os dias de conteúdo que eles cobrem estiverem prontos. Dia de revisão cujo conteúdo coberto falhou: deixe pendente e registre.
9. **Fechar.** Grave ou atualize o `LEIA-ME.md` (formato abaixo) e informe: dias gerados, dias que falharam, tópicos sem fonte web, e que rodar `/concurso "<pasta>"` de novo gera só o que faltou.

## Nomes

- Pasta do concurso: `<Órgão> <Ano> - <Cargo> (<Banca>)`, com espaços e acentos. Troque `/ \ : * ? " < > |` por `-`. Ex.: `INSS 2026 - Técnico do Seguro Social (Cebraspe)`.
- Pasta do dia: `dias/Dia NNN - DD-MM - <Matérias>`, número com 3 dígitos, matérias unidas por ` + `. Revisão semanal: `Revisão`. Reserva final: `Revisão Final`.

## `LEIA-ME.md`

```markdown
# <Órgão> <Ano> - <Cargo> (<Banca>)

- Órgão / Cargo / Banca:
- Data da prova:
- Vagas:
- Remuneração:
- Edital: <caminho local ou URL de origem>
- Gerado em: <AAAA-MM-DD>
- Dias gerados: <n> de <total>

## Pendências
<dias que falharam e tópicos sem fonte web; "nenhuma" se vazio>

## Como estudar
Abra a pasta do dia, estude o `conteudo.md`, resolva o `simulado.md` e só então confira o `gabarito.md`.
A lei muda: o conteúdo reflete a data de geração. Perto da prova, confira os artigos mais cobrados na fonte oficial.
```

## Erros comuns

- Pular uma confirmação para "ganhar tempo". As duas existem porque um erro no edital ou no cronograma contamina todos os dias.
- Gerar o material de um dia no contexto principal em vez de despachar subagente: estoura o contexto.
- Na retomada, reler o edital ou regerar dias completos.
- Gravar arquivo final direto: sempre `.tmp` e depois `mv`, para que pasta com três arquivos signifique dia completo.
