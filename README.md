<p align="center">
  <img alt="Estudo para Concurso Público" src="docs/logo.svg" width="480">
</p>

> Passe o edital, receba o plano de estudo inteiro até o dia da prova.
> Para cada dia: o que estudar, o material reunido da web e um simulado
> no estilo da banca, com gabarito comentado.
> E, antes disso, um aviso no celular quando abrir um concurso que combina com você
> ou quando sair o edital que você está esperando.

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-orange)](docs/superpowers/specs/2026-11-23-concurso-skill-design.md)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-d97757)](https://claude.com/claude-code)
[![Idioma](https://img.shields.io/badge/idioma-pt--BR-green)](#)

## Por que usar

O edital tem 80 páginas, a prova é daqui a três meses e a primeira semana vai embora montando planilha. Este plugin faz esse trabalho por você, e ainda avisa quando é hora de começar.

- **Lê o edital por você.** O PDF, local ou por link, vira um resumo com o que importa: cargo, banca, data, matérias com número de questões e peso, conteúdo programático e as regras que mudam a estratégia, como a errada que anula a certa no Cebraspe.

- **Monta um cronograma que respeita o peso.** Todos os dias, de amanhã até a véspera da prova, são distribuídos na proporção de `questões × peso`. São duas matérias por dia, intercaladas, com revisão a cada sete dias e uma reserva final de revisão geral. Se faltar tempo, a skill avisa em vez de esconder.

- **Junta o conteúdo de cada dia.** Lei seca do Planalto, súmulas e jurisprudência do STF e do STJ, e materiais abertos, organizados por tópico do edital e sempre com o link da fonte.

- **Entrega um simulado por dia.** Questões no formato da banca: certo/errado no Cebraspe e cinco alternativas na FGV, FCC e Vunesp. O simulado cobra só o que você estudou naquele dia, e o gabarito comenta cada questão, citando o artigo.

- **Tudo em arquivos simples.** Uma pasta por concurso, uma pasta por dia, material de estudo em PDF. Abra em qualquer leitor ou imprima. Nada fica preso dentro do chat.

- **Avisa quando abre um concurso para você.** O `/notifica-concurso` lê seu LinkedIn, site ou currículo, aponta os cargos compatíveis com a sua formação e manda um push no celular (app ntfy) sempre que sair um edital que bate com seu perfil. A verificação roda duas vezes por dia, no GitHub Actions ou no seu computador.

- **Avisa quando sai o edital que você espera.** O `/notifica-edital` vigia o site que você indicar (portal de concursos, página da banca ou do órgão) e manda um push no celular assim que aparece o edital do concurso que você quer, como o da PF ou do TRF.

- **É honesta sobre os limites.** Conteúdo sem fonte web leva um aviso no topo. A data de geração fica registrada, porque a lei muda. Antes de começar, a skill mostra quantos dias vai gerar.

## Como funciona

<p align="center">
  <img alt="Fluxo: edital, resumo, cronograma e material de cada dia" src="docs/banner.svg" width="100%">
</p>

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

Se o Claude Code já estava aberto, rode `/reload-plugins` para carregar as skills sem reiniciar a sessão.

### Mantenha a skill sempre atualizada

O Claude Code só atualiza sozinho os marketplaces oficiais da Anthropic. Para marketplaces de terceiros, como este, o auto-update vem desligado. Ative uma vez:

1. No Claude Code, rode `/plugin`.
2. Abra a aba **Marketplaces** e selecione `estudo-concurso`.
3. Escolha **Enable auto-update**.

A partir daí, o Claude Code busca a versão nova ao iniciar e avisa quando houver atualização. Rode `/reload-plugins` para carregá-la sem reiniciar a sessão.

Para atualizar na mão, a qualquer momento:

```bash
claude plugin marketplace update estudo-concurso
claude plugin update concurso@estudo-concurso
```

Depois rode `/reload-plugins` no Claude Code para usar a versão nova.

Na pasta onde quer guardar seus estudos, rode a skill com o edital:

```
/concurso ~/Downloads/edital-inss-2026.pdf
/concurso https://cdn.cebraspe.org.br/concursos/inss_26/arquivos/ED_1.PDF
```

Para ser avisado de concursos abertos que combinam com você, rode com seu perfil:

```
/notifica-concurso https://www.linkedin.com/in/seu-perfil
/notifica-concurso ~/Documentos/curriculo.pdf
```

Para ser avisado quando sair o edital de um concurso específico, diga onde olhar e qual edital:

```
/notifica-edital https://www.pciconcursos.com.br/noticias/ edital da Polícia Federal para Agente
```

O LinkedIn costuma bloquear a leitura sem login. Nesse caso a skill pede o PDF do perfil (no LinkedIn: **Mais** → **Salvar em PDF**). Os avisos precisam de uma preparação rápida: veja [Antes de criar avisos](#antes-de-criar-avisos).

O único requisito é o Claude Code. O download por link usa o `curl` do sistema. Os PDFs são gerados com Chrome, Chromium, Edge ou Brave em modo headless, então um deles precisa estar instalado.

## O que é gerado

```
INSS 2026 - Técnico do Seguro Social (Cebraspe)/
├── LEIA-ME.pdf       # cartão do concurso: cargo, banca, data, vagas, salário, avisos
├── edital.pdf        # o edital original
├── edital-resumido.pdf  # resumo do edital em PDF
├── cronograma.pdf    # tabela dia a dia
├── agentes/          # markdown que os agentes leem (fonte dos PDFs acima)
└── meus-estudos/
    ├── Dia 001 - (24-11-2026) - Direito Constitucional/
    │   ├── conteudo.pdf
    │   ├── simulado.pdf
    │   └── gabarito.pdf
    ├── Dia 002 - (25-11-2026) - Português + Raciocínio Lógico/
    ├── ...
    ├── Dia 007 - (30-11-2026) - Revisão/
    ├── ...
    └── Dia 090 - (21-02-2027) - Revisão Final/
```

| Arquivo | O que tem |
| --- | --- |
| `LEIA-ME.pdf` | Identificação do concurso, origem do edital, data de geração, tópicos sem fonte web |
| `edital-resumido.pdf` | Estrutura da prova, conteúdo programático com códigos (`DC-01`, `PT-03`…), pegadinhas do edital |
| `cronograma.pdf` | Dia, data, tipo (conteúdo, revisão, revisão final), matérias e tópicos |
| `conteudo.pdf` | Resumo, artigos de lei, o que a banca cobra, pegadinhas e fontes com link |
| `simulado.pdf` | 10 a 20 questões no formato da banca, só sobre o conteúdo do dia |
| `gabarito.pdf` | Resposta e comentário de cada questão, com a fonte |

Para o dia a dia: abra a pasta do dia, estude o `conteudo.pdf`, resolva o `simulado.pdf` e só então confira o `gabarito.pdf`.

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

Quando a busca na web falha num tópico, o conteúdo é gerado mesmo assim, com o aviso `⚠ conteúdo sem fonte web, conferir lei atualizada` no topo. A lista desses tópicos fica no `LEIA-ME.pdf`.

## Antes de criar avisos

O `/notifica-concurso` e o `/notifica-edital` mandam push no celular e instalam um verificador que roda sozinho. A skill conduz tudo, mas deixe isto pronto antes para não parar no meio.

### 1. App ntfy no celular

O [ntfy](https://ntfy.sh) é um app gratuito e sem cadastro que recebe notificações. O aviso chega por um **tópico**, um nome que funciona como canal.

1. Instale o **ntfy** pela [Play Store](https://play.google.com/store/apps/details?id=io.heckel.ntfy), pela [App Store](https://apps.apple.com/app/ntfy/id1625396347) ou pelo [F-Droid](https://f-droid.org/packages/io.heckel.ntfy/).
2. Abra o app e permita notificações.
3. **Não crie tópico ainda.** A skill gera um nome aleatório (`concursos-1a2b3c4d` ou `editais-1a2b3c4d`) e pede para você tocar em **+** e assinar esse nome.
4. A skill manda um aviso de teste e só continua depois que você confirmar que ele chegou.

Cuidados:
- **O tópico é a senha.** O servidor público ntfy.sh não tem login: quem souber o nome recebe seus avisos. Não poste o nome nem o coloque em repositório público.
- **Android:** se o aviso atrasar ou não chegar, tire o ntfy da otimização de bateria (Configurações → Apps → ntfy → Bateria → Sem restrições).
- Os dois comandos podem usar o mesmo tópico. O `/notifica-edital` oferece reaproveitar o do `/notifica-concurso`.

### 2. Onde o verificador vai rodar

O verificador confere os sites às 8h e às 18h. A skill pergunta onde instalar:

| | GitHub Actions | No seu computador |
|---|---|---|
| Roda com o PC desligado | sim | não |
| Precisa de conta | GitHub (grátis) | nenhuma |
| Precisa instalar | `gh` (GitHub CLI) | Python 3 |
| Gasta seu plano Claude | não | não |
| Site que bloqueia servidores | pode falhar | costuma funcionar |

Na dúvida, escolha **GitHub Actions**: aviso de edital só serve se chegar no dia.

### 3a. Preparar o GitHub Actions

1. Crie uma conta em [github.com](https://github.com/signup), se ainda não tiver.
2. Instale o GitHub CLI:
   - Windows: `winget install --id GitHub.cli`
   - macOS: `brew install gh`
   - Linux: veja [cli.github.com](https://cli.github.com) (Debian/Ubuntu: `sudo apt install gh`)
3. Faça login com permissão para criar workflows. No Claude Code, rode:
   ```
   ! gh auth login -s workflow
   ```
   Responda **GitHub.com**, **HTTPS**, **Yes** (autenticar o Git) e **Login with a web browser**. Copie o código mostrado e cole na página que abrir.
4. Confira com `! gh auth status`. A linha `Token scopes` precisa ter `repo` e `workflow`. Se você já estava logado sem `workflow`, rode `! gh auth refresh -s workflow`.

Todos os avisos ficam num único repositório **privado** na sua conta, o `notifica-estudo-concurso`. A primeira skill que você configurar cria o repositório; as outras só acrescentam o verificador delas. Cada aviso tem o próprio workflow (`notificador.yml` para concursos, `vigia_edital.yml` para editais) e guarda seu perfil ou suas vigias num *secret* próprio, que não aparece no código. Desligar um aviso não afeta os outros.

Se você configurou antes dessa mudança e tem os repositórios `notifica-concurso` ou `notifica-edital`, rode o comando de novo: a skill oferece mover o aviso para o `notifica-estudo-concurso` e desliga o antigo. Cada execução leva menos de um minuto; duas por dia ficam bem dentro dos 2.000 minutos mensais grátis do GitHub para repositórios privados.

Se uma execução falhar (site fora do ar, página mudou), o GitHub manda um e-mail. Para ver o histórico: aba **Actions** do repositório.

### 3b. Preparar o seu computador

Só precisa do Python 3, sem bibliotecas extras.
- Windows: `winget install Python.Python.3.12` (ou [python.org](https://www.python.org/downloads/), marcando **Add python.exe to PATH**). Confira com `py --version`.
- macOS: já vem com `python3`; se pedir, aceite instalar as ferramentas de linha de comando.
- Linux: já vem instalado na maioria das distribuições (`python3 --version`).

A skill registra o verificador no agendador do sistema (systemd no Linux, launchd no macOS, Agendador de Tarefas no Windows) e guarda a configuração em `~/.config/notifica-concurso/` ou `~/.config/notifica-edital/`. Se o computador estiver desligado ou dormindo às 8h ou 18h: no Linux a verificação roda quando ele ligar; no macOS, quando acordar do repouso (desligado, pula); no Windows, pula aquele horário.

### Editar ou desligar

Rode o mesmo comando de novo (`/notifica-concurso` ou `/notifica-edital`) sem argumento. A skill mostra o que está configurado e oferece editar, adicionar, remover ou desligar. Desligar remove o agendamento (ou desativa o workflow no GitHub) e apaga a configuração local.

## Aviso de concursos abertos

Rode `/notifica-concurso` com o link do seu LinkedIn, do seu site ou o caminho do seu currículo em PDF. A skill:

1. lê seu perfil e pergunta o que faltar (área, estados, salário mínimo);
2. gera `perfil-concurso.pdf` com os cargos que combinam com você, seus pontos fortes, as lacunas a estudar e os concursos abertos hoje;
3. configura o app **ntfy** no seu celular e manda um aviso de teste;
4. instala um verificador que roda às 8h e às 18h, no GitHub Actions ou no seu computador, você escolhe.

Rode `/notifica-concurso` de novo para editar o perfil ou desligar os avisos.

## Aviso de edital específico

Rode `/notifica-edital` com o link do site onde o edital vai ser publicado e o concurso que você espera. A skill:

1. monta os termos de busca (nome do órgão e sigla, cargo, estado) e testa no site, mostrando o que combinaria hoje. Se o edital já saiu, você fica sabendo na hora;
2. configura o app **ntfy** (pode usar o mesmo tópico do `/notifica-concurso`) e manda um aviso de teste;
3. instala um verificador que roda às 8h e às 18h, no GitHub Actions ou no seu computador.

Dá para acompanhar vários editais: rode `/notifica-edital` de novo para adicionar, remover ou desligar. Sites que montam a página com JavaScript não funcionam; nesse caso a skill sugere outra página.

## Cuidados

- **Leva tempo e consome bastante uso.** Todo o material sai de uma vez. Uma prova daqui a 90 dias significa 90 pastas com busca na web.
- **A lei muda.** O conteúdo reflete a data em que foi gerado. Perto da prova, confira na fonte oficial os artigos mais cobrados.
- **PDF escaneado** (imagem, sem texto) ainda não é suportado. Nesse caso a skill avisa e para.
- **Os avisos dependem do site.** O `/notifica-edital` lê a página como ela chega do servidor. Se o site mudar de layout, bloquear robôs ou montar a página com JavaScript, o aviso pode não chegar. A verificação acusa erro quando a página vem sem links, mas confira o site de vez em quando para o concurso que mais importa.
- **O material é um apoio.** Não substitui o edital oficial nem a leitura da lei seca.
