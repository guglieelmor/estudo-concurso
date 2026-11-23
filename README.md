<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/logo-dark.svg">
    <img alt="Estudo para Concurso Público" src="docs/logo-light.svg" width="480">
  </picture>
</p>

> Passe o edital, receba o plano de estudo inteiro até o dia da prova.
> Para cada dia: o que estudar, o material reunido da web e um simulado
> no estilo da banca, com gabarito comentado.

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)](docs/superpowers/specs/2026-11-23-concurso-skill-design.md)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-d97757)](https://claude.com/claude-code)
[![Idioma](https://img.shields.io/badge/idioma-pt--BR-green)](#)

## Por que usar

O edital tem 80 páginas, a prova é daqui a três meses e a primeira semana vai embora montando planilha. Esta skill faz esse trabalho por você.

- **Lê o edital por você.** O PDF, local ou por link, vira um resumo com o que importa: cargo, banca, data, matérias com número de questões e peso, conteúdo programático e as regras que mudam a estratégia, como a errada que anula a certa no Cebraspe.

- **Monta um cronograma que respeita o peso.** Todos os dias, de amanhã até a véspera da prova, são distribuídos na proporção de `questões × peso`. São duas matérias por dia, intercaladas, com revisão a cada sete dias e uma reserva final de revisão geral. Se faltar tempo, a skill avisa em vez de esconder.

- **Junta o conteúdo de cada dia.** Lei seca do Planalto, súmulas e jurisprudência do STF e do STJ, e materiais abertos, organizados por tópico do edital e sempre com o link da fonte.

- **Entrega um simulado por dia.** Questões no formato da banca: certo/errado no Cebraspe e cinco alternativas na FGV, FCC e Vunesp. O simulado cobra só o que você estudou naquele dia, e o gabarito comenta cada questão, citando o artigo.

- **Tudo em arquivos simples.** Uma pasta por concurso, uma pasta por dia, tudo em markdown. Abra no editor, no Obsidian ou imprima. Nada fica preso dentro do chat.

- **É honesta sobre os limites.** Conteúdo sem fonte web leva um aviso no topo. A data de geração fica registrada, porque a lei muda. Antes de começar, a skill mostra quantos dias vai gerar.

## Como funciona

<p align="center">
  <img alt="Fluxo: edital, resumo, cronograma e material de cada dia" src="docs/banner.svg" width="100%">
</p>

```
edital ──▶ resumo ──▶ cronograma ──▶ dias
PDF ou     matérias,  até a véspera   conteúdo + simulado + gabarito,
link       pesos,     da prova        gerados em paralelo
           data
```

A skill confirma com você duas vezes, porque um erro nessas etapas contamina todo o resto:

1. **Depois de ler o edital:** você confere as matérias, os pesos e a data. Se o edital tiver vários cargos, ela pergunta qual é o seu.
2. **Depois de montar o cronograma:** você vê o total de dias e a distribuição por matéria.

A partir daí, vários agentes trabalham em paralelo, cada um com um bloco de 7 dias, e geram todo o material. Os dias de revisão saem por último, a partir do conteúdo que já foi gerado.

O design completo está em [`docs/superpowers/specs/2026-11-23-concurso-skill-design.md`](docs/superpowers/specs/2026-11-23-concurso-skill-design.md).

## Início rápido

Instale o plugin no Claude Code:

```bash
claude plugin marketplace add guglieelmor/estudo-concurso
claude plugin install concurso@estudo-concurso
```

Na pasta onde quer guardar seus estudos, rode a skill com o edital:

```
/concurso ~/Downloads/edital-inss-2026.pdf
/concurso https://cdn.cebraspe.org.br/concursos/inss_26/arquivos/ED_1.PDF
```

O único requisito é o Claude Code. O download por link usa o `curl` do sistema.

## O que é gerado

```
INSS 2026 - Técnico do Seguro Social (Cebraspe)/
├── LEIA-ME.md        # cartão do concurso: cargo, banca, data, vagas, salário, avisos
├── edital.pdf        # o edital original
├── edital.md         # resumo do edital
├── cronograma.md     # tabela dia a dia
└── dias/
    ├── Dia 001 - 24-11 - Direito Constitucional/
    │   ├── conteudo.md
    │   ├── simulado.md
    │   └── gabarito.md
    ├── Dia 002 - 25-11 - Português + Raciocínio Lógico/
    ├── ...
    ├── Dia 007 - 30-11 - Revisão/
    ├── ...
    └── Dia 090 - 21-02 - Revisão Final/
```

| Arquivo | O que tem |
| --- | --- |
| `LEIA-ME.md` | Identificação do concurso, origem do edital, data de geração, tópicos sem fonte web |
| `edital.md` | Estrutura da prova, conteúdo programático com códigos (`DC-01`, `PT-03`…), pegadinhas do edital |
| `cronograma.md` | Dia, data, tipo (conteúdo, revisão, revisão final), matérias e tópicos |
| `conteudo.md` | Resumo, artigos de lei, o que a banca cobra, pegadinhas e fontes com link |
| `simulado.md` | 10 a 20 questões no formato da banca, só sobre o conteúdo do dia |
| `gabarito.md` | Resposta e comentário de cada questão, com a fonte |

Para o dia a dia: abra a pasta do dia, estude o `conteudo.md`, resolva o `simulado.md` e só então confira o `gabarito.md`.

## Bancas suportadas

| Banca | Formato do simulado |
| --- | --- |
| Cebraspe | Certo / errado |
| FGV | Múltipla escolha, 5 alternativas |
| FCC | Múltipla escolha, 5 alternativas |
| Vunesp | Múltipla escolha, 5 alternativas |
| Outras | Formato descrito no edital (4 ou 5 alternativas) |

## Mais de um concurso

Rode `/concurso` para cada edital. Cada concurso ganha uma pasta e um cronograma independentes:

```
Concursos/
├── INSS 2026 - Técnico do Seguro Social (Cebraspe)/
└── TRT-2 2027 - Analista Judiciário (FCC)/
```

Os cronogramas não se coordenam entre si. Se você estudar para os dois ao mesmo tempo, a divisão do tempo fica por sua conta.

## Se algo der errado no meio

Rode `/concurso` de novo apontando para a pasta do concurso. O edital não é relido, e os dias que já estão completos são pulados. Só os dias que faltam são gerados.

Quando a busca na web falha num tópico, o conteúdo é gerado mesmo assim, com o aviso `⚠ conteúdo sem fonte web, conferir lei atualizada` no topo. A lista desses tópicos fica no `LEIA-ME.md`.

## Cuidados

- **Leva tempo e consome bastante uso.** Todo o material sai de uma vez. Uma prova daqui a 90 dias significa 90 pastas com busca na web.
- **A lei muda.** O conteúdo reflete a data em que foi gerado. Perto da prova, confira na fonte oficial os artigos mais cobrados.
- **PDF escaneado** (imagem, sem texto) ainda não é suportado. Nesse caso a skill avisa e para.
- **O material é um apoio.** Não substitui o edital oficial nem a leitura da lei seca.
