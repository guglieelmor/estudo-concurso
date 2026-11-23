# Gerar os dias de um bloco

Você recebeu: o caminho da pasta do concurso, o caminho do navegador, as linhas do cronograma do seu bloco e este arquivo. Leia `agentes/edital.md` da pasta do concurso primeiro: ele dá a banca, o tipo de questão, o número de alternativas, o texto de cada tópico e as pegadinhas.

Para cada dia do bloco, em ordem:

1. Pasta do dia: `<pasta do concurso>/meus-estudos/Dia NNN - (DD-MM-AAAA) - <Matérias>/`. Crie se não existir.
2. Se ela já tem `conteudo.pdf`, `simulado.pdf` e `gabarito.pdf`, pule. Apague `.tmp` que sobraram.
3. Escreva os três documentos em HTML conforme o tipo do dia (abaixo) e converta cada um em PDF seguindo `pdf.md`. A estrutura mostrada abaixo em markdown é só o esqueleto: vire `<h1>`, `<h2>`, listas e links no HTML.
4. **Escrita atômica:** o PDF nasce como `<nome>.pdf.tmp` e só vira `<nome>.pdf` depois de conferido. Gere `gabarito.pdf` por último. Na pasta do dia ficam só os três PDFs.

Não pergunte nada ao estudante. Decida e registre.

## Dia de conteúdo

### Busca

Para cada tópico do dia, use WebSearch e WebFetch, nesta prioridade:
1. lei seca no Planalto (`planalto.gov.br`) ou no site oficial, para lei estadual ou municipal;
2. súmulas e jurisprudência do STF e do STJ;
3. materiais didáticos abertos.

Fonte bloqueada ou sem resposta: tente outra e registre. Busca falhou para o tópico inteiro: escreva o conteúdo com o que você sabe e marque o tópico como sem fonte web.

### `conteudo.pdf`

```markdown
# Dia NNN — DD/MM/AAAA — <Matérias>

> ⚠ conteúdo sem fonte web, conferir lei atualizada  (só se algum tópico ficou sem fonte; liste quais)

## <CÓDIGO> — <texto do tópico no edital>

### Resumo
### Lei seca
<artigos relevantes transcritos, com número do artigo>
### O que a banca cobra
### Pegadinhas
### Fontes
- [título](url)
### Para aprofundar
- [título](url) — <o que o aluno encontra ali>
```

`Fontes` são as páginas que você usou para escrever. `Para aprofundar` é obrigatório em todo tópico: 1 a 3 links para o aluno estudar além do resumo, como a lei seca no Planalto, uma súmula, um material didático aberto ou uma videoaula gratuita. Só ponha link que você abriu com WebFetch e que respondeu com o conteúdo prometido. Tópico sem nenhum link que funcione: escreva `nenhum link verificado` e trate o tópico como sem fonte web.

Matérias sem lei (Português, Raciocínio Lógico, Informática, Matemática…): troque "Lei seca" por "Teoria" e "Exemplos resolvidos".

### `simulado.pdf`

10 a 20 questões, numeradas, cobrando **só** o que está no `conteudo.pdf` deste dia, sem resposta no arquivo.
- Cebraspe: itens certo/errado, com um texto-base curto quando fizer sentido. Termine cada item com `( ) Certo ( ) Errado`.
- Múltipla escolha (FGV, FCC, Vunesp e outras): alternativas A–E; A–D se o `agentes/edital.md` disser 4 alternativas.
- Imite o estilo da banca: Cebraspe troca uma palavra para tornar o item errado; FCC cobra a letra da lei; FGV usa casos práticos; Vunesp é mais direta.

### `gabarito.pdf`

Para cada questão: número, resposta e comentário de 1 a 4 linhas citando o artigo de lei ou o trecho do `conteudo.pdf` que fundamenta. Em item errado do Cebraspe, diga qual palavra torna o item errado.

## Dia de revisão (semanal)

- Sem busca na web.
- `conteudo.pdf`: leia com Read os `conteudo.pdf` dos dias cobertos e faça um resumo dos pontos principais por tópico, com as pegadinhas, citando de qual dia veio cada parte.
- `simulado.pdf`: 15 a 20 questões misturando os tópicos cobertos.
- `gabarito.pdf`: como no dia de conteúdo.

## Dia de revisão final

- Sem busca na web.
- `conteudo.pdf`: resumo de todas as matérias a partir dos `conteudo.pdf` existentes (leia com Read), priorizando as de maior peso e as pegadinhas do edital. Cada dia de revisão final foca matérias diferentes quando houver mais de um.
- `simulado.pdf`: simulado com a estrutura real da prova, mesma proporção de questões por matéria do `agentes/edital.md`. Se a prova for grande, escale para 30 a 50 questões mantendo a proporção.
- `gabarito.pdf`: como no dia de conteúdo, e no fim a regra de pontuação do edital (ex.: errada anula certa) para o estudante calcular a nota.

## Resposta ao orquestrador

Termine com exatamente este bloco, e nada depois:

```
CONCLUÍDOS: Dia 001, Dia 002, ...
FALHARAM: Dia 004 (<motivo curto>) | nenhum
SEM FONTE WEB: Dia 003 DC-05, ... | nenhum
```
