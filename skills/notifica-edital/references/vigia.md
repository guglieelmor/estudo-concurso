# Montando uma vigia

## Como o verificador decide

`vigia_edital.py` baixa a página, pega cada link e monta o texto: texto do link + `title` + endereço (hifens e barras viram espaço, sem acento, minúsculo). Um link **combina** quando:
- **todos** os `termos` aparecem (cada termo aceita alternativas com `|`, como palavra inteira: `pf` não casa com `prf`); e
- **pelo menos um** gatilho aparece. Padrão: `edital, editais, abertura, abre, abrem, aberto, abertas, inscricao, inscricoes`.

Link novo que combina = push. Links já vistos ficam guardados; não avisa duas vezes.

## Formato de `<cfg>/vigias.json`

```json
{
  "topico": "editais-1a2b3c4d",
  "modo": "local",
  "vigias": [
    {
      "nome": "PF Agente 2027",
      "url": "https://www.pciconcursos.com.br/noticias/",
      "termos": ["policia federal|pf", "agente"],
      "gatilhos": []
    }
  ]
}
```
`gatilhos` vazio = padrão. Use gatilhos próprios só quando a página for do próprio concurso e os links não dizem "edital" (ex. página da banca: `["inscricoes", "inscricao", "abertura"]`).

## Escolhendo termos

- Órgão por extenso **e** sigla no mesmo termo: `"tribunal regional federal da 3 regiao|trf 3|trf3"`. Sem acento e sem pontuação (`3ª` vira `3`).
- Cargo como segundo termo só se o candidato fizer questão; muitas notícias de abertura não citam todos os cargos no título. Na dúvida, deixe só o órgão e o gatilho cuida do resto.
- Estado/cidade para órgãos que se repetem: prefeitura, PM, Polícia Civil, Detran, TJ (`"policia civil|pc", "sp|sao paulo"`). Sigla de estado curta como `sp` casa em endereço (`/pc-sp-abre...`), o que é bom.
- Ano (`2027`) só se o site costuma pôr no título; senão perde o aviso.
- Teste sempre com `--listar` e mostre o que combinaria hoje.

## Escolhendo a página

Melhor → pior:
1. Página do concurso na banca (Cebraspe, FGV, FCC, Vunesp...): aparece o link do edital quando sai. Use gatilhos próprios se preciso.
2. Seção de notícias de um portal de concursos (ex. `pciconcursos.com.br/noticias/`): atualiza muito e cobre tudo; os itens saem da capa em poucos dias, por isso o verificador roda 2x por dia.
3. Página "concursos" do site do órgão.

Busca do site (`?q=...`) funciona se o resultado vier no HTML (teste com `--listar --todos`).

## Site não funciona

Se `--listar` der erro (403, timeout) ou `links_na_pagina` 0, ou `--todos` só mostrar menu/rodapé: o site monta a página com JavaScript ou bloqueia robôs. Diga isso ao candidato e proponha outra página: a seção de notícias de um portal de concursos que cite o órgão, a página da banca, ou o feed RSS do site, se houver (`/feed`, `/rss`: o verificador lê os `<a>`, então só serve se o feed tiver links em HTML; teste).
