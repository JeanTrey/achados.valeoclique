# PROJECT MASTER — Vale o Clique

Este diretório é a fonte de verdade para revisar o projeto antes de novas implementações.

## Objetivo
Transformar o Vale o Clique em um gerador automático e individual de anúncios curtos para TikTok/Reels/Shorts, partindo preferencialmente de um link de produto e produzindo um criativo que pareça dirigido por humanos, não um slideshow programático.

## Como usar
Leia nesta ordem:

1. `01_VISAO_E_OBJETIVO.md` — produto final desejado e princípios.
2. `02_ESTADO_ATUAL.md` — o que existe de verdade hoje no código.
3. `03_HISTORICO_E_FALHAS.md` — VOC-001, VOC-002 e VOC-003; o que aprendemos.
4. `04_ARQUITETURA_ALVO.md` — arquitetura que deve substituir a lógica atual.
5. `05_GATES_E_CRITERIOS.md` — quando um criativo pode avançar ou deve ser barrado.
6. `06_BACKLOG_PRIORIZADO.md` — ordem recomendada da refatoração.
7. `07_DECISOES_E_LIMITACOES.md` — decisões não negociáveis, riscos e pendências.

## Regra de documentação
Cada item deve ser classificado como:

- **IMPLEMENTADO**: existe no código e está conectado ao fluxo.
- **PARCIAL**: existe, mas não resolve o problema por completo.
- **PLANEJADO**: ainda não deve ser apresentado como funcional.
- **REPROVADO**: abordagem testada que não deve orientar a próxima versão.

## Norte do projeto
O motor não existe para simplesmente produzir um MP4 válido. Ele existe para responder, em cada anúncio:

1. Por que alguém pararia de rolar?
2. Por que continuaria assistindo?
3. Por que acreditaria no produto?
4. Por que clicaria?

Se o pipeline não consegue responder essas quatro perguntas, o criativo não está pronto.