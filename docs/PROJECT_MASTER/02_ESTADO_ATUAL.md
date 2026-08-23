# 02 — Estado Atual do App

## Resumo

O projeto começou como um renderer programático de vídeos verticais e evoluiu para conter peças de direção criativa, memória, benchmarking, coleta de assets e storyboard. A base técnica existe, mas a qualidade criativa ainda está **PARCIAL** e as versões VOC-001/002/003 demonstraram que a arquitetura atual ainda não entrega anúncios com qualidade humana.

## Componentes implementados

### Core de render — IMPLEMENTADO
Em `src/voc/` existem módulos para:

- `loader.py` / `validators.py` — leitura e validação de produto, roteiro, template e config;
- `models.py` — modelos de produto, cena, script, timeline e render;
- `timeline.py` — timeline determinística;
- `image_renderer.py` — composição 9:16;
- `text_renderer.py` — fitting/wrap de texto;
- `animation.py` — movimentos simples;
- `renderer.py` — geração frame a frame e encode via FFmpeg;
- `audio.py` / `sound_design.py` — mix e assets sonoros;
- `export.py` — export final;
- `render.py` — entrypoint de render.

Preset atual principal: 720x1280, 30 FPS, H.264/AAC.

### Preparação criativa — PARCIAL

- `creative.py` gera arco curto por papéis como cold_open, tension, reveal, proof, price e CTA.
- `creative_memory.py` lê memória de preferências/reprovações.
- `retention.py` aplica um gate estático contra padrões ruins conhecidos.
- `prepare.py` combina assets, roteiro, TTS, música e SFX.

Problema: ainda é fortemente heurístico e não entende o produto/visual como um diretor humano.

### Asset Director — PARCIAL

`asset_director.py`:

- gera derivados de imagens reais;
- cria crops e full views;
- tenta escolher variantes por função da cena.

Problema: scoring por contraste/detalhe já gerou crops ruins e mutilou produto/arte. Melhorou, mas ainda não existe segmentação semântica de teclado, mouse, embalagem etc.

### Product Collector — PARCIAL

`product_collector.py` e `assets_import.py`:

- tentam descobrir URLs públicas de imagens da Shopee;
- baixam hosts permitidos;
- continuam mesmo se uma URL individual falhar.

Problema: páginas dinâmicas/anti-bot podem impedir recuperar toda a galeria e vídeos. Ainda não é um Product Researcher robusto.

### Benchmarking — PARCIAL

Arquivos principais:

- `benchmarks/records.json` — referências estruturais/editoriais;
- `collect_benchmarks.py` — descoberta de candidatos;
- `analyze_benchmarks.py`;
- `benchmark_video.py` — FFprobe/FFmpeg, duração, cortes, primeiro corte, shot duration;
- `benchmark.py` — perfil agregado.

Decisão corrigida: referências textuais não contam como vídeos analisados. O contador de mídia deve refletir somente arquivos efetivamente processados.

Limitação: FFmpeg entende ritmo e estrutura física, não semântica visual. Ainda falta Benchmark Vision multimodal.

### Creative Plan / Storyboard — IMPLEMENTADO COMO INFRAESTRUTURA, QUALIDADE PARCIAL

- `creative_plan.py` cria um plano por cena com propósito, asset, layout, texto, movimento e justificativa.
- `storyboard.py` renderiza frames e contact sheet.
- `make_storyboard.py` cria o bundle antes do MP4.

Essa arquitetura é correta como gate, mas o primeiro storyboard VOC-003 ainda foi visualmente reprovado.

### Visual Director — PARCIAL

`visual_director.py` deriva direção básica de paleta e papel narrativo.

Problema: regras de cor/layout ainda são heurísticas; não existe ainda uma linguagem visual sofisticada nem análise semântica de composição.

### Feedback / memória — PARCIAL

Diretórios:

- `feedback/` — avaliações estruturadas de versões;
- `memory/` — perfil criativo e benchmark agregado.

Isso permite guardar rejeições e preferências, mas não é treinamento de modelo. É memória/regras/ranking.

### CI / GitHub Actions — IMPLEMENTADO

`.github/workflows/test.yml` executa validação, testes, benchmarking, preparação/storyboard/render conforme configuração.

Decisão atual: desenvolvimento deve migrar para execução local durante a fase de refatoração. GitHub permanece como versionamento e CI de segurança.

## Estrutura relevante do repositório

- `products/VOC-001`, `VOC-002`, `VOC-003` — experimentos de produto/creative;
- `src/voc/` — engine;
- `templates/` — aparência/configs anteriores;
- `assets/` — branding/fontes/música/SFX;
- `benchmarks/` — evidência e referências;
- `feedback/` — feedback humano estruturado;
- `memory/` — memória agregada;
- `docs/` — documentação;
- `output/` — render final.

## Diagnóstico atual

A base de software é útil, mas a arquitetura ainda se comporta mais como **editor programático baseado em heurísticas** do que como **diretor criativo automático multimodal**. O próximo ciclo não deve focar em polir templates; deve substituir decisões heurísticas centrais por pesquisa, entendimento semântico e planejamento visual.