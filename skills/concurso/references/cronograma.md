# Montar o cronograma

Calcule as datas com `date` no Bash (ex.: `date -d "tomorrow" +%F`, `date -d "2026-11-24 +1 day" +%d-%m-%Y`), nunca de cabeça.

## Regras, nesta ordem

1. **Período.** Do `Início dos estudos` gravado no `agentes/edital.md` até a véspera da prova, todos os dias, inclusive fins de semana. `T` = total de dias.
2. **Reserva final.** Os últimos `max(3, ceil(T × 0,10))` dias são `revisão final`: revisão geral e simulado completo no formato real da prova.
3. **Revisão semanal.** Nos dias restantes, cada 7º dia (dia 7, 14, 21…) é `revisão` dos tópicos estudados nos 6 dias anteriores.
4. **Dias de conteúdo.** Os demais. Cada dia de conteúdo tem 2 slots (2 matérias). `S` = 2 × dias de conteúdo.
5. **Peso.** Pontos da matéria = `questões × peso`. Slots da matéria = `S × pontos / soma dos pontos`, arredondando pelo método do maior resto, com no mínimo 1 slot por matéria.
6. **Tópicos por slot.** Distribua os códigos da matéria em ordem entre os slots dela. Mais slots que tópicos: os slots extras repetem os tópicos de maior peso com aprofundamento e questões. Menos slots que tópicos: agrupe vários tópicos no mesmo slot (veja Falta de tempo).
7. **Intercalação.** Monte os dias alternando matérias: as duas matérias de um dia são diferentes sempre que houver mais de uma matéria com slots sobrando, e nenhuma matéria aparece em todos os dias de uma semana se houver alternativa. Um jeito simples: ordene os slots por matéria em fila circular (round-robin ponderado pela quantidade de slots restantes) e tire dois por dia.
8. **Prova muito próxima.** Se não sobrar nenhum dia de conteúdo (T ≤ 3), todos os dias são `revisão final` cobrindo o edital inteiro, com o aviso de falta de tempo.

## Falta de tempo

Quando algum slot recebe mais de 3 tópicos, ou alguma matéria fica com menos slots que a metade dos seus tópicos, há falta de tempo:
- agrupe primeiro os tópicos das matérias de menor peso;
- escreva o aviso no topo do `agentes/cronograma.md` e repita na confirmação 2, dizendo quais matérias ficaram comprimidas.

## Formato do `agentes/cronograma.md`

```markdown
# Cronograma — <Órgão> <Ano> - <Cargo> (<Banca>)

> ⚠ Falta de tempo: <matérias comprimidas e como>. (só se houver)

- Prova: <DD/MM/AAAA>
- Período: <DD/MM/AAAA> a <DD/MM/AAAA> (<T> dias)
- Dias de conteúdo: <n> · Revisão semanal: <n> · Revisão final: <n>

## Dias por matéria

| Matéria | Pontos (questões × peso) | Slots |
| --- | --- | --- |

## Calendário

| Dia | Data | Tipo | Matérias | Tópicos |
| --- | --- | --- | --- | --- |
| 001 | 24-11-2026 | conteúdo | Direito Constitucional + Português | DC-01, DC-02; PT-01 |
| 007 | 30-11-2026 | revisão | Revisão | dias 001–006 |
| 090 | 21-02-2027 | revisão final | Revisão Final | todas as matérias |
```

As colunas Data (`DD-MM-AAAA`) e Matérias são as mesmas que vão no nome da pasta do dia.
