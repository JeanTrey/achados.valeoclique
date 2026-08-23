# 06 — Backlog Priorizado

## P0 — Parar de produzir criatividade ruim automaticamente

### 0.1 Congelar o renderer como executor
- Renderer não escolhe copy.
- Renderer não escolhe estratégia.
- Renderer não escolhe qual claim provar.
- Renderer só executa `creative_plan` aprovado.

### 0.2 Storyboard obrigatório
- Todo produto gera storyboard antes de MP4.
- MP4 automático desabilitado durante refatoração.
- Contact sheet vira artefato principal de revisão.

### 0.3 Separar status de cada módulo
Criar um manifesto de capacidades com `IMPLEMENTADO/PARCIAL/PLANEJADO/REPROVADO` para impedir que features planejadas sejam tratadas como prontas.

---

## P1 — Product Researcher robusto

### 1.1 Entrada única por URL
Objetivo: novo produto começa apenas com URL.

### 1.2 Recuperar galeria e vídeos
- imagens;
- vídeos públicos;
- título;
- marca/modelo;
- preço/data;
- seller claims;
- rating/vendidos quando acessível.

### 1.3 Proveniência
Cada dado e asset deve carregar sua URL/origem.

### 1.4 Fallbacks
Se Shopee bloquear HTML:
- tentar metadados/hydration pública;
- usar browser/provider apropriado futuramente;
- permitir import manual como fallback, não como caminho principal.

---

## P2 — Asset Curator semântico

### 2.1 Classificar imagens
Detectar:
- produto inteiro;
- detalhe;
- texto/infográfico;
- lifestyle;
- embalagem;
- repetição;
- asset inadequado.

### 2.2 Object-aware crops
Não cortar produto por score de contraste. Usar bounding boxes/segmentação/vision para preservar objeto.

### 2.3 Background removal/segmentation
Criar PNG/alpha do produto quando seguro para composições próprias.

### 2.4 Asset adequacy score
Antes de criar roteiro, medir se existe material suficiente para a estratégia escolhida.

---

## P3 — Benchmark Vision real

### 3.1 Dataset comprovável
Processar mídia real e registrar evidência.

### 3.2 Keyframes
Extrair frames em:
- 0s;
- 0.5s;
- 1s;
- primeiros cortes;
- product reveal;
- price;
- CTA;
- final.

### 3.3 Análise multimodal
Para cada frame, obter descrição estruturada:
- assunto;
- composição;
- texto;
- produto/pessoa;
- escala;
- emoção/ação;
- função da cena.

### 3.4 Métricas agregadas
Aprender distribuições, não uma fórmula única.

---

## P4 — Creative Director V2

### 4.1 Classificar produto/contexto
Ex.: utilidade, transformação, desejo estético, conveniência, preço, novidade.

### 4.2 Gerar múltiplas estratégias candidatas
Ex.: 3 briefs diferentes.

### 4.3 Rankear estratégias
Usar:
- asset adequacy;
- benchmark;
- Creative Memory;
- duração;
- quantidade de fatos disponíveis.

### 4.4 Roteiro visual antes de copy final
Primeiro decidir o que mostrar; depois decidir o que escrever/falar.

---

## P5 — Art Director V2

### 5.1 Design system dinâmico
Criar tokens por anúncio:
- type scale;
- font weight;
- accent;
- surface;
- spacing;
- safe areas;
- card rules.

### 5.2 Composições por finalidade
Hook, proof, offer e CTA não podem ser apenas o mesmo card reposicionado.

### 5.3 Text density control
Limite por área ocupada da tela, não só contagem de palavras.

### 5.4 Product dominance check
Garantir que texto não roube protagonismo sem intenção explícita.

---

## P6 — Vision Storyboard Gate

Adicionar análise automática do contact sheet:
- crop mutilado;
- texto excessivo;
- repetição visual;
- baixa diferença entre cenas;
- produto pequeno demais;
- contraste ruim;
- safe zone.

Revisão humana permanece durante desenvolvimento.

---

## P7 — Audio Director V2

- roteiro falado independente da copy visual;
- seleção de voz;
- speech rate por cena;
- pausas e silêncio;
- SFX por evento semântico;
- música por energia/estilo;
- normalização LUFS;
- beat/cut synchronization quando útil.

---

## P8 — Render final e publicação

Somente depois dos módulos acima:
- transições mais sofisticadas;
- motion graphics;
- 1080x1920;
- presets TikTok/Reels/Shorts;
- publicação/analytics futura.

---

## Ordem recomendada de implementação local

1. Congelar renderer e formalizar interfaces.
2. Product Researcher.
3. Asset Curator semântico.
4. Benchmark Vision.
5. Creative Director V2.
6. Art Director V2.
7. Storyboard Gate V2.
8. Audio Director V2.
9. Reintegrar renderer.
10. Testar com produto diferente do KV-789.

## Regra de validação

Não avançar para a próxima grande camada apenas porque testes unitários passam. Cada gate precisa de evidência visual real.