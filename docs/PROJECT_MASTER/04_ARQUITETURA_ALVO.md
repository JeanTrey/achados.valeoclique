# 04 — Arquitetura Alvo

## Visão geral

A arquitetura alvo separa entendimento, direção e execução. O renderer deixa de tomar decisões criativas e passa a executar um plano previamente aprovado.

```text
INPUT: link do produto
        ↓
Product Researcher
        ↓
Fact / Claim Resolver
        ↓
Asset Curator
        ↓
Benchmark Vision + Creative Memory
        ↓
Creative Director
        ↓
Art Director
        ↓
Storyboard Builder
        ↓
Storyboard Gate
        ↓
Audio Director
        ↓
Timeline / Renderer
        ↓
Final Creative Gate
        ↓
MP4 + relatório
```

## 1. Product Researcher — PLANEJADO

Responsável por transformar um link em um pacote pesquisável:

- título/marca/modelo;
- preço e timestamp;
- seller claims;
- fotos da galeria;
- vídeos públicos do anúncio, quando disponíveis;
- avaliações/quantidades quando disponíveis;
- contexto de uso detectado;
- links/proveniência de cada informação.

Não deve depender de o usuário enviar JPGs manualmente.

## 2. Fact / Claim Resolver — PLANEJADO/PARCIAL

Classifica cada afirmação como:

- fato objetivo recuperado;
- seller claim;
- inferência de contexto;
- informação ausente.

Regras:

- nunca promover seller claim para fato sem fonte;
- preço sempre com data de consulta;
- dado ausente permanece ausente;
- cenas visuais de prova só podem usar evidência compatível.

## 3. Asset Curator — evolução do Asset Director

Deve entender semanticamente os assets, não apenas calcular contraste.

Classificações desejadas:

- hero/full product;
- teclado/mouse/componente;
- close técnico;
- embalagem;
- dimensão/infográfico;
- lifestyle/contexto;
- prova visual;
- frame com texto promocional embutido;
- asset fraco/rejeitado.

Funções:

- deduplicar;
- detectar imagem que já contém texto pesado;
- preservar objeto inteiro quando necessário;
- segmentar objeto quando seguro;
- gerar derivados só quando aumentam valor visual;
- solicitar/buscar contexto complementar quando a galeria é insuficiente.

## 4. Benchmark Vision — PLANEJADO

Camada multimodal que realmente analisa frames de anúncios de referência.

Deve extrair, por vídeo:

- primeiro frame;
- hook visual;
- presença de pessoa/mão/produto;
- porcentagem aproximada da tela ocupada por texto;
- posição e escala do produto;
- momento do primeiro reveal;
- momento de preço;
- momento de CTA;
- ritmo de cortes;
- mudanças de composição;
- uso de captions, cards, overlays;
- relação entre áudio e movimento;
- estilo: creator-native, demo, comparison, aesthetic, problem/solution etc.

O FFmpeg atual continua útil para métricas físicas, mas não substitui esta camada.

## 5. Creative Memory — PARCIAL

Memória estruturada de:

- padrões aprovados/reprovados;
- feedback humano;
- resultados de desempenho futuros;
- estratégias por categoria de produto;
- decisões visuais que funcionaram ou falharam.

Não deve alterar fatos do produto.

## 6. Creative Director — PARCIAL -> REFAZER

Recebe produto + assets + benchmark + memory e escolhe uma estratégia.

Estratégias possíveis, não obrigatórias:

- problema -> solução;
- comparação;
- before/after;
- price surprise;
- curiosity/reveal;
- immediate benefit;
- demo-first;
- social proof;
- aesthetic/native.

Saída: um **Creative Brief** contendo:

- promessa central;
- hook;
- motivo para continuar;
- sequência de informação;
- evidência usada em cada cena;
- duração alvo;
- densidade de fala;
- CTA.

## 7. Art Director — PARCIAL -> REFAZER

Cria direção visual individual para aquele criativo:

- família tipográfica;
- escala tipográfica;
- paleta;
- margens/safe zones;
- regras de cards;
- densidade de texto;
- tratamento de preço;
- tratamento de CTA;
- estilo de transição;
- gramática de movimento.

Não deve apenas escolher uma cor dominante da imagem.

## 8. Storyboard Builder — PARCIAL

Gera 6–10 frames-chave e um `creative_plan.json`.

Cada cena precisa registrar:

- purpose;
- source asset;
- proof/fact relation;
- crop/composition;
- copy;
- motion intent;
- expected duration;
- audio intent;
- why this scene exists.

## 9. Storyboard Gate — IMPLEMENTADO COMO CONCEITO

Machine checks + revisão visual humana durante desenvolvimento.

Futuramente pode incluir Vision QA automático.

O vídeo não avança se:

- frames parecem repetidos;
- produto está mutilado;
- texto domina a tela sem motivo;
- informação visual não progride;
- prova não corresponde ao claim;
- visual parece slideshow/template genérico.

## 10. Audio Director — PARCIAL

Deve decidir:

- quando narrar;
- quando não narrar;
- velocidade/voz;
- pausas;
- música;
- SFX apenas quando semanticamente úteis;
- loudness alvo em LUFS;
- sincronismo com cortes e movimentos.

## 11. Renderer — IMPLEMENTADO, deve simplificar responsabilidade

Função futura:

- receber plano fechado;
- renderizar frames/movimentos;
- mixar áudio;
- exportar H.264/AAC;
- nunca inventar estratégia, copy ou seleção de evidência.

## 12. Performance Learner — PLANEJADO

Quando houver dados próprios:

- 1s/3s retention;
- average watch time;
- completion rate;
- CTR;
- saves/shares;
- vendas/conversões quando disponível.

Esses sinais devem alimentar ranking de estratégias. Fine-tuning só deve ser considerado depois de volume de dados suficiente.