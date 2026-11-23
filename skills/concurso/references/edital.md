# Ler o edital

## Leitura

- Leia o PDF com Read em fatias de até 20 páginas (`pages: "1-20"`, `"21-40"`…) até o fim.
- Nas primeiras fatias, ache: órgão, banca, cargos, datas, estrutura da prova. O conteúdo programático costuma estar num anexo no final.
- Mais de um cargo: liste os cargos e pergunte qual é o do estudante. Daí em diante, extraia só o que vale para esse cargo (estrutura da prova e conteúdo programático costumam variar por cargo).
- Nenhum texto extraído (PDF escaneado): pare e avise que esse tipo de PDF ainda não é suportado.
- Não invente dado ausente. Escreva `não informado no edital`. A data da prova ausente será perguntada na confirmação 1.

## Códigos de tópico

Cada matéria ganha uma sigla de 2 a 3 letras maiúsculas, única no edital (Direito Constitucional `DC`, Português `PT`, Raciocínio Lógico `RL`, Direito Administrativo `DA`, Informática `INF`…). Cada item do conteúdo programático vira `<SIGLA>-NN`, na ordem do edital. Item muito longo, com vários assuntos separados por ponto e vírgula, pode ser quebrado em vários códigos; item curto e relacionado ao vizinho pode ficar junto. Mantenha o texto como aparece no edital.

## Formato do `edital.md`

```markdown
# Edital — <Órgão> <Ano> - <Cargo> (<Banca>)

## Identificação
- Órgão:
- Cargo:
- Banca:
- Ano:
- Edital nº:

## Datas
- Prova objetiva:
- Prova discursiva:
- Inscrição:
- Pedido de isenção:
- Início dos estudos: <data escolhida pelo estudante na confirmação 1>

## Vagas, remuneração, requisitos e taxa
- Vagas:
- Remuneração:
- Requisitos:
- Taxa de inscrição:

## Estrutura da prova

| Matéria | Sigla | Questões | Peso | Tipo | Eliminação |
| --- | --- | --- | --- | --- | --- |
| Direito Constitucional | DC | 20 | 1 | certo/errado | mínimo 5 pontos no bloco |

- Alternativas por questão (múltipla escolha): <4 ou 5>

## Conteúdo programático

### Direito Constitucional (DC)
- DC-01: <texto do edital>
- DC-02: <texto do edital>

### Português (PT)
- PT-01: …

## Pegadinhas do edital
- <regra que muda a estratégia: uma errada anula uma certa no Cebraspe, nota mínima por bloco, discursiva eliminatória, cláusula de barreira…>
```

Se o tipo de questão não estiver explícito, deduza pela banca: Cebraspe = certo/errado; FGV, FCC, Vunesp = múltipla escolha com 5 alternativas. Registre em Pegadinhas que foi dedução.

## Gerar `edital-resumido.pdf`

Depois do "ok" da confirmação 1, converta o `edital.md` final em `<pasta do concurso>/edital-resumido.pdf` seguindo `pdf.md`. O `edital.md` fica: é a fonte que os subagentes leem.
