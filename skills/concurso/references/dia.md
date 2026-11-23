# Gerar os dias de um bloco

Você recebeu: o caminho da pasta do concurso, as linhas do cronograma do seu bloco e este arquivo. Leia `edital.md` da pasta do concurso primeiro: ele dá a banca, o tipo de questão, o número de alternativas, o texto de cada tópico e as pegadinhas.

Para cada dia do bloco, em ordem:

1. Pasta do dia: `<pasta do concurso>/dias/Dia NNN - DD-MM - <Matérias>/`. Crie se não existir.
2. Se ela já tem `conteudo.md`, `simulado.md` e `gabarito.md`, pule. Apague `.tmp` que sobraram.
3. Gere os três arquivos conforme o tipo do dia (abaixo).
4. **Escrita atômica:** grave cada arquivo como `<nome>.md.tmp` e só depois `mv` para `<nome>.md`. Grave `gabarito.md` por último.

Não pergunte nada ao estudante. Decida e registre.

## Dia de conteúdo

### Busca

Para cada tópico do dia, use WebSearch e WebFetch, nesta prioridade:
1. lei seca no Planalto (`planalto.gov.br`) ou no site oficial, para lei estadual ou municipal;
2. súmulas e jurisprudência do STF e do STJ;
3. materiais didáticos abertos.

Fonte bloqueada ou sem resposta: tente outra e registre. Busca falhou para o tópico inteiro: escreva o conteúdo com o que você sabe e marque o tópico como sem fonte web.

### `conteudo.md`

```markdown
# Dia NNN — DD/MM — <Matérias>

> ⚠ conteúdo sem fonte web, conferir lei atualizada  (só se algum tópico ficou sem fonte; liste quais)

## <CÓDIGO> — <texto do tópico no edital>

### Resumo
### Lei seca
<artigos relevantes transcritos, com número do artigo>
### O que a banca cobra
### Pegadinhas
### Fontes
- [título](url)
```

Matérias sem lei (Português, Raciocínio Lógico, Informática, Matemática…): troque "Lei seca" por "Teoria" e "Exemplos resolvidos".

### `simulado.md`

10 a 20 questões, numeradas, cobrando **só** o que está no `conteudo.md` deste dia, sem resposta no arquivo.
- Cebraspe: itens certo/errado, com um texto-base curto quando fizer sentido. Termine cada item com `( ) Certo ( ) Errado`.
- Múltipla escolha (FGV, FCC, Vunesp e outras): alternativas A–E; A–D se o `edital.md` disser 4 alternativas.
- Imite o estilo da banca: Cebraspe troca uma palavra para tornar o item errado; FCC cobra a letra da lei; FGV usa casos práticos; Vunesp é mais direta.

### `gabarito.md`

Para cada questão: número, resposta e comentário de 1 a 4 linhas citando o artigo de lei ou o trecho do `conteudo.md` que fundamenta. Em item errado do Cebraspe, diga qual palavra torna o item errado.

## Dia de revisão (semanal)

- Sem busca na web.
- `conteudo.md`: leia os `conteudo.md` dos dias cobertos e faça um resumo dos pontos principais por tópico, com as pegadinhas, citando de qual dia veio cada parte.
- `simulado.md`: 15 a 20 questões misturando os tópicos cobertos.
- `gabarito.md`: como no dia de conteúdo.

## Dia de revisão final

- Sem busca na web.
- `conteudo.md`: resumo de todas as matérias a partir dos `conteudo.md` existentes, priorizando as de maior peso e as pegadinhas do edital. Cada dia de revisão final foca matérias diferentes quando houver mais de um.
- `simulado.md`: simulado com a estrutura real da prova, mesma proporção de questões por matéria do `edital.md`. Se a prova for grande, escale para 30 a 50 questões mantendo a proporção.
- `gabarito.md`: como no dia de conteúdo, e no fim a regra de pontuação do edital (ex.: errada anula certa) para o estudante calcular a nota.

## Resposta ao orquestrador

Termine com exatamente este bloco, e nada depois:

```
CONCLUÍDOS: Dia 001, Dia 002, ...
FALHARAM: Dia 004 (<motivo curto>) | nenhum
SEM FONTE WEB: Dia 003 DC-05, ... | nenhum
```
