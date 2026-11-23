# Gerar PDF

Todo PDF da skill sai de um HTML convertido por um navegador em modo headless.

## Navegador

`command -v google-chrome google-chrome-stable chromium chromium-browser microsoft-edge brave-browser | head -1`. No macOS, teste também `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`. O orquestrador acha o navegador uma vez e passa o caminho aos subagentes.

## HTML

Uma página por arquivo, `<meta charset="utf-8">`, fonte sem serifa, tabelas com borda, `@page { margin: 2cm }`. Use `<h1>`/`<h2>`/`<h3>` para a estrutura e `<a href>` nos links de fonte, para que fiquem clicáveis no PDF. Grave o HTML num diretório temporário (`mktemp -d`), nunca na pasta do concurso.

## Conversão

```bash
"<navegador>" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="<destino>.pdf.tmp" "file://<tmp>/<nome>.html"
head -c 4 "<destino>.pdf.tmp"   # tem que ser %PDF
mv "<destino>.pdf.tmp" "<destino>.pdf"
```

Só faça o `mv` se o cabeçalho for `%PDF`. Assim, um `.pdf` na pasta sempre é um arquivo completo.
