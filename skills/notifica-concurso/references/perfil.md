# Perfil e análise

## Ler a fonte

- **Site pessoal ou portfólio:** WebFetch pedindo "formação, experiência profissional com cargos e datas, habilidades, certificações, cidade".
- **LinkedIn (`linkedin.com/in/...`):** tente o WebFetch uma vez. Se voltar página de login, "Sign in", "Entrar" ou não trouxer experiência, diga:
  > O LinkedIn bloqueia a leitura sem login. Abra seu perfil, clique em **Mais** → **Salvar em PDF** e me passe o caminho do arquivo. Se preferir, cole aqui o texto do perfil.
- **PDF:** Read no arquivo. Se o texto vier vazio (PDF escaneado), peça o texto colado.

## Extrair

| Campo | Exemplo |
|---|---|
| Escolaridade | Superior completo — Bacharelado em Sistemas de Informação |
| Pós/certificações | MBA em Gestão de Projetos; AWS Cloud Practitioner |
| Áreas | Desenvolvimento web, banco de dados |
| Experiência | Desenvolvedor PHP, 4 anos; suporte técnico, 2 anos |
| Cidade/UF | Campinas - SP |

O que não estiver na fonte fica "não informado". Não invente.

## Perguntar o que falta

Uma pergunta por vez, só as que a fonte não respondeu. Sempre com sugestão:

1. Área ou cargos de interesse. Sugira os compatíveis com a formação (ver tabela abaixo).
2. Abrangência: nacional, só alguns estados ou nacional mais o próprio estado.
3. Aceita cargo de escolaridade abaixo da sua? (superior aceitando nível médio/técnico)
4. Aceita mudar de cidade? Se "não", `estados` fica com `NACIONAL` mais a UF dele.
5. Salário mínimo aceitável (R$).

## Compatibilidade formação → cargos (guia, não lista fechada)

| Formação | Cargos típicos em edital |
|---|---|
| TI (SI, CC, ADS, Eng. Computação) | Analista de TI, Analista de Sistemas, Técnico de TI, Analista Judiciário – Apoio Especializado (TI), Auditor de TI |
| Direito | Analista Judiciário – Área Judiciária, Procurador, Delegado, Defensor, Técnico Judiciário |
| Contabilidade/Economia/Administração | Auditor Fiscal, Analista de Controle Externo, Analista Administrativo, Contador |
| Saúde | o próprio cargo da profissão (Enfermeiro, Médico, Farmacêutico) |
| Engenharias | Engenheiro <área>, Analista de Infraestrutura |
| Licenciaturas | Professor <disciplina> |
| Qualquer superior | Analista Administrativo, Técnico (se aceitar nível médio), Agente/Escrivão de Polícia |

## Montar o filtro

- `palavras`: 3 a 8 termos que aparecem em títulos do PCI, sem acento e em minúsculas. Exemplos: `tecnologia da informacao`, `analista de ti`, `analista de sistemas`. Use termos compostos. A palavra solta `ti` casa só com a palavra inteira, mas é ambígua: prefira `analista de ti`. Se o candidato aceita qualquer área, deixe `[]`.
- `estados`: nomes como o PCI usa, sem acento e em maiúsculas (`NACIONAL`, `SAO PAULO`, `DISTRITO FEDERAL`). Nacional total: `[]`.
- `resumo`: uma frase com formação, experiência principal e cidade. Entra no `perfil-concurso.md` (análise); o aviso diário ignora.
- Mostre ao candidato quantos concursos abertos hoje passam no filtro:
  o `perfil.json` ainda não existe: grave `{"palavras":[...],"estados":[...]}` num temporário (`F=$(mktemp)`) e rode `python3 <notificador>/notificador.py --perfil "$F" --listar`. Conte os itens. Zero: afrouxe as palavras. Mais de 60: aperte.

## `perfil-concurso.md`

```markdown
# Perfil para concursos — <nome>

Gerado em <data>.

## Quem é
<escolaridade, áreas, experiência, cidade>

## Cargos compatíveis
| Cargo | Por quê | Escolaridade exigida |
|---|---|---|

## Pontos fortes para a prova
- <exemplo: experiência em banco de dados conta em Analista de TI, que cobra SQL>

## Lacunas a estudar
- <exemplo: Direito Administrativo e Constitucional, cobrados em quase todo edital de tribunal>

## Filtro de notificação
- Palavras-chave: ...
- Estados: ...
- Salário mínimo: R$ ...
- Concursos abertos hoje que passam no filtro: N

## Concursos abertos agora que combinam
| Órgão | Cargo/vagas | Inscrição até | Link |
|---|---|---|---|
```

A última tabela vem do `--listar`, com até 10 itens, os mais compatíveis primeiro.
