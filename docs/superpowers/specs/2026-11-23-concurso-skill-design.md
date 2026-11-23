# Skill `concurso` — Design

Data: 2026-11-23
Status: aprovado em brainstorming, aguardando revisão da spec

## Objetivo

Plugin distribuível do Claude Code com uma skill `concurso` que, a partir do edital de um concurso público, gera de uma só vez todo o material de estudo até o dia da prova:

1. Lê o edital (PDF local ou URL) e resume o que importa.
2. Cria um cronograma diário de amanhã até a véspera da prova.
3. Para cada dia, reúne conteúdo da web sobre os tópicos do dia.
4. Para cada dia, gera um simulado no estilo da banca, com gabarito comentado.

## Fora de escopo (v1)

- Simulado interativo no chat e registro de acertos/erros.
- Ajuste do cronograma por desempenho.
- Integração entre concursos (cronograma unificado, matérias em comum).
- Reaproveitamento de conteúdo entre concursos (candidata para v2).
- Disponibilidade de estudo personalizada (dias da semana, horas por dia).
- Scripts auxiliares (pdftotext, cálculo de datas). Adicionar só se aparecer um edital que o Read não consiga ler, como um PDF escaneado.

## Público

Plugin distribuível para qualquer estudante. As instruções precisam funcionar para quem nunca viu a skill. Sem dependências além do Claude Code (Read, Write, Bash com `curl`, WebSearch, WebFetch, Agent).

## Estrutura do plugin

```
concurso-plugin/
├── .claude-plugin/plugin.json
└── skills/concurso/
    ├── SKILL.md              # orquestrador: fases, retomada, regras gerais
    └── references/
        ├── edital.md         # como ler o edital e o formato do edital.md
        ├── cronograma.md     # regras de distribuição e o formato do cronograma.md
        └── dia.md            # prompt do subagente: buscar conteúdo e montar simulado + gabarito
```

O `SKILL.md` fica curto e aponta para os arquivos de referência de cada fase.

## Pasta de saída

Criada no diretório atual. Cada concurso tem a sua pasta, com um nome legível que identifica o concurso visualmente:

```
INSS 2026 - Técnico do Seguro Social (Cebraspe)/
├── LEIA-ME.md
├── edital.pdf
├── edital.md
├── cronograma.md
└── dias/
    ├── Dia 001 - 24-11 - Direito Constitucional/
    │   ├── conteudo.md
    │   ├── simulado.md
    │   └── gabarito.md
    ├── Dia 002 - 25-11 - Português + Raciocínio Lógico/
    └── ...
```

- Nome da pasta do concurso: `<Órgão> <Ano> - <Cargo> (<Banca>)`, com espaços e acentos. Caracteres inválidos em nome de arquivo (`/ \ : * ? " < > |`) são trocados por `-`.
- Nome da pasta do dia: `Dia NNN - DD-MM - <Matérias>`. O número com três dígitos mantém a ordem. Dias de revisão usam `Revisão` como matéria, e os dias da reserva final usam `Revisão Final`.
- `LEIA-ME.md` é o cartão do concurso: órgão, cargo, banca, data da prova, vagas, remuneração, origem do edital (caminho ou URL), data de geração, quantidade de dias gerados e lista de dias ou tópicos sem fonte web.

Vários concursos convivem lado a lado como pastas independentes. Cada um tem o seu cronograma, sem nenhuma coordenação entre eles.

## Fluxo de `/concurso <caminho-ou-url>`

1. **Obter o edital.**
   - Caminho local: usar direto.
   - URL: baixar com `curl -L` para um arquivo temporário e confirmar que é PDF (cabeçalho `%PDF`). Se não for, parar e avisar.
2. **Ler o edital** em fatias de 20 páginas com Read e extrair os dados conforme `references/edital.md`. Se houver vários cargos, perguntar qual é o do estudante.
3. **Criar a pasta do concurso**, copiar o PDF para `edital.pdf` e gravar `edital.md`.
4. **Confirmação 1:** mostrar o resumo (cargo, banca, data da prova, matérias com nº de questões e peso). Se a data da prova não estiver no edital, perguntar. Corrigir o que o estudante apontar.
5. **Gerar `cronograma.md`** conforme `references/cronograma.md`.
6. **Confirmação 2:** mostrar o resumo do cronograma (total de dias, dias por matéria, dias de revisão, avisos de falta de tempo).
7. **Gerar os dias de conteúdo:** disparar subagentes em paralelo, um por bloco de 7 dias, no máximo 5 ao mesmo tempo. Cada um recebe `edital.md`, as linhas do seu bloco no cronograma, o caminho da pasta do concurso e as instruções de `references/dia.md`.
8. **Gerar os dias de revisão e de revisão final**, numa segunda leva, depois que os dias de conteúdo de que dependem estiverem prontos.
9. **Fechar:** atualizar o `LEIA-ME.md` e informar ao estudante os dias gerados, os dias que falharam e os tópicos sem fonte web.

### Retomada

Ao rodar `/concurso` dentro de uma pasta de concurso que já existe, ou apontando para ela, a skill não relê o edital: usa o `edital.md` e o `cronograma.md` existentes. Um dia que já tem os três arquivos (`conteudo.md`, `simulado.md`, `gabarito.md`) é pulado. Os subagentes recebem só os dias pendentes.

## `edital.md`

Seções:

- **Identificação:** órgão, cargo, banca, ano, número do edital.
- **Datas:** prova objetiva, prova discursiva (se houver), inscrição, isenção.
- **Vagas, remuneração, requisitos, taxa de inscrição.**
- **Estrutura da prova:** uma tabela com matéria, nº de questões, peso, tipo de questão (certo/errado ou múltipla escolha) e critério de eliminação.
- **Conteúdo programático:** cada matéria com os tópicos numerados por um código (`DC-01`, `DC-02`, `PT-01`…), com o texto como aparece no edital.
- **Pegadinhas do edital:** penalidade por item errado (por exemplo, no Cebraspe uma errada anula uma certa), nota mínima por bloco, discursiva eliminatória e outras regras que mudam a estratégia.

## Regras do cronograma

1. **Período:** de amanhã até a véspera da prova, todos os dias, com volume uniforme.
2. **Reserva final:** os últimos 10% dos dias, com no mínimo 3, são de revisão geral e simulados completos no formato real da prova.
3. **Peso:** os dias de conteúdo são distribuídos entre as matérias na proporção de `nº de questões × peso`.
4. **Intercalação:** 2 matérias por dia, alternando, para nunca passar uma semana seguida numa só matéria.
5. **Revisão semanal:** a cada 7 dias, um dia de revisão dos tópicos daquela semana.
6. **Falta de tempo:** se não houver dias suficientes para todos os tópicos, agrupar os de menor peso no mesmo dia e avisar o estudante explicitamente na confirmação 2 e no topo do `cronograma.md`.

O `cronograma.md` é uma tabela com dia, data, tipo (conteúdo, revisão ou revisão final), matérias e códigos dos tópicos.

## Subagente do dia (`references/dia.md`)

Para cada dia de conteúdo do bloco:

1. **Busca:** WebSearch e WebFetch dos tópicos, priorizando as fontes nesta ordem:
   1. lei seca no Planalto (ou no site oficial, para lei estadual ou municipal);
   2. súmulas e jurisprudência do STF e do STJ;
   3. materiais didáticos abertos.

   Se uma fonte bloquear o acesso, tentar outra e registrar.
2. **`conteudo.md`:** para cada tópico, um resumo, os artigos de lei relevantes transcritos, o que a banca costuma cobrar, as pegadinhas e as fontes com link. Matérias sem lei (Português, Raciocínio Lógico, Informática) recebem teoria e exemplos resolvidos.
3. **`simulado.md`:** de 10 a 20 questões no formato da banca, cobrando só o que está no `conteudo.md` daquele dia.
   - Cebraspe: itens certo/errado.
   - FGV, FCC, Vunesp e outras de múltipla escolha: 5 alternativas (A–E). Usar 4 alternativas se o edital disser isso.
4. **`gabarito.md`:** resposta e comentário de cada questão, citando o artigo de lei ou o trecho do `conteudo.md` que a fundamenta.

Para cada dia de revisão e de revisão final:

- Sem busca na web.
- `conteudo.md`: um resumo dos pontos principais dos dias cobertos (a semana, no caso da revisão semanal, ou todas as matérias, no caso da revisão final), feito a partir dos `conteudo.md` desses dias.
- `simulado.md`: questões misturando os tópicos cobertos. Na revisão final, o simulado segue a estrutura real da prova (proporção de questões por matéria).

### Escrita atômica

Cada arquivo é gravado primeiro com o sufixo `.tmp` e depois renomeado. Assim, uma pasta de dia com os três arquivos finais está sempre completa, e a regra de retomada é confiável.

### Erros

- Se a busca falhar num tópico, gerar o conteúdo a partir do conhecimento do modelo e colocar no topo do `conteudo.md` o aviso `⚠ conteúdo sem fonte web, conferir lei atualizada`.
- O subagente devolve ao orquestrador a lista de dias concluídos, dias que falharam e tópicos sem fonte web.
- O orquestrador inclui isso no resumo final e no `LEIA-ME.md`. Dias que falharam podem ser gerados de novo rodando `/concurso` outra vez, pela retomada.

## Testes

Teste manual com um edital real e uma data de prova próxima, por volta de 10 dias, para gerar pouco material:

1. Os campos do `edital.md` batem com o PDF (matérias, nº de questões, pesos, data).
2. A distribuição do cronograma é proporcional ao peso, com intercalação, revisão semanal e reserva final corretas.
3. O `conteudo.md` traz fontes reais com links.
4. O `simulado.md` cobra só o que está no `conteudo.md` do dia e segue o formato da banca.
5. Retomada: apagar a pasta de um dia, rodar `/concurso` de novo, e só aquele dia deve ser regenerado.
6. Entrada por URL: baixar um edital por link direto. Uma URL que não seja PDF deve ser rejeitada.

## Riscos conhecidos

- **Custo e tempo:** gerar tudo de uma vez para muitos dias consome muitos tokens e leva bastante tempo. O estudante é avisado na confirmação 2, com o total de dias.
- **Lei desatualizada:** conteúdo buscado no dia da geração pode mudar até a prova. O `LEIA-ME.md` registra a data de geração.
- **PDF escaneado:** o Read pode não extrair texto. Nesse caso a skill avisa e para. A extração por OCR fica para uma versão futura.
