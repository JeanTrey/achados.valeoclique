# 05 — Gates e Critérios de Sucesso

## Princípio

O projeto precisa de gates separados. Um único score não pode misturar validade técnica com qualidade criativa.

## Gate 0 — Integridade de entrada

Deve falhar se:

- produto não possui ID;
- não existe fonte/proveniência mínima;
- preço é usado sem timestamp quando deveria ser atual;
- seller claim aparece como fato verificado;
- não há nenhum asset visual utilizável.

## Gate 1 — Product/Asset Quality

Perguntas:

- temos hero/full product?
- temos pelo menos um detalhe real útil?
- há assets duplicados?
- imagem contém texto promocional embutido que pode conflitar com nossa composição?
- algum crop mutila o produto?
- a galeria é insuficiente para o arco proposto?

Se os assets são insuficientes, o diretor deve mudar a estratégia ou buscar contexto adicional; não repetir a mesma imagem por sete cenas.

## Gate 2 — Creative Brief

O plano precisa responder:

1. Por que parar?
2. Por que continuar?
3. Por que acreditar?
4. Por que clicar?

Falha se qualquer uma dessas respostas for essencialmente "porque colocamos texto na tela".

## Gate 3 — Storyboard Machine Check

Checks objetivos:

- número mínimo/máximo de cenas;
- copy por frame abaixo do limite definido pela direção;
- produto não extrapola safe zone de forma não intencional;
- assets consecutivos não são idênticos sem justificativa;
- cada cena registra propósito;
- CTA existe;
- claim visual possui evidência compatível;
- preço histórico não é apresentado como atual.

## Gate 4 — Storyboard Visual/Humano

Durante desenvolvimento, obrigatório.

Perguntas por frame:

- parece uma peça intencional ou um template?
- o olho sabe onde olhar primeiro?
- o produto está legível?
- há espaço negativo suficiente?
- texto ajuda ou atrapalha?
- a cena introduz informação nova?
- a sequência cria curiosidade/progressão?
- qualquer frame-chave seria aceitável isoladamente em um feed?

Se o contact sheet é feio, o MP4 não deve existir.

## Gate 5 — Audio Plan

Antes do render final:

- falas não se sobrepõem;
- roteiro falado é mais curto que o visual permite;
- pausas existem;
- SFX são seletivos;
- música não compete com narração;
- loudness é medido com uma métrica definida, preferencialmente LUFS;
- nenhuma cena precisa ser alongada excessivamente por TTS.

## Gate 6 — Technical Render

Obrigatório:

- 9:16;
- preset atual 720x1280/30fps durante prototipação;
- H.264;
- yuv420p;
- AAC;
- áudio presente quando esperado;
- sem frames faltando;
- sem barras pretas inesperadas;
- reprodução normal em mobile/social.

## Gate 7 — Final Creative Review

Assistir sem olhar código.

Reprovar se:

- parece slideshow;
- começo parece meio de vídeo;
- copy é maior que o produto sem motivo;
- há SFX em toda transição;
- ritmo não acompanha informação;
- anúncio poderia servir para qualquer produto apenas trocando a foto;
- visual é cansativo/cego;
- CTA parece banner genérico;
- áudio parece colocado por cima, e não dirigido junto com o vídeo.

## Gate 8 — Performance, futuro

Quando houver métricas reais, estabelecer thresholds por plataforma/categoria, sem assumir universalidade.

Métricas-alvo futuras:

- retenção 1s/3s;
- average watch time;
- completion rate;
- CTR;
- save/share rate;
- conversão atribuível quando disponível.

## Definição de sucesso da fase atual

A fase de refatoração só termina quando um produto novo consegue passar pelo fluxo com pouca ou nenhuma intervenção manual e gerar um storyboard que um humano considere visualmente publicável antes do render.