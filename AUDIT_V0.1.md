# Auditoria Final — Vale o Clique Video Engine V0.1

Use este checklist depois de colocar os assets reais do VOC-001 no repositório/Codespace.

## 1. Preparar assets reais

Coloque as imagens originais do anúncio em `products/VOC-001/images/` e ajuste os nomes em `products/VOC-001/script.json`.

Coloque a narração em `products/VOC-001/audio/` e referencie cada arquivo na cena correspondente.

Opcionalmente adicione:

- `assets/branding/logo.png`
- `assets/music/<arquivo>.mp3` ou WAV
- `assets/sfx/woosh.wav`
- `assets/sfx/cursor_click.wav`

Não preencha fatos que não estejam verificados no anúncio.

## 2. Preencher Product Data

Atualize `products/VOC-001/product.json` somente com dados confirmados. Para preço, registre também `preco_consultado_em`. Alegações do vendedor podem usar `source_type: seller_claim`.

## 3. Recriar a timeline do VOC-001

O vídeo de referência auditado tem aproximadamente 18,733 s, 720×1280 e 30 FPS. Estruture `script.json` em cenas próximas aos blocos visuais observados (~0-3 s, 3-6 s, 6-10,03 s, 10,03-14,07 s, 14,07-18,73 s), ajustando pelos assets reais e pela narração.

## 4. Executar validação

```bash
python -m pip install -r requirements.txt
pytest -q
python render.py VOC-001 --validate-only
```

Os testes devem passar antes do render final.

## 5. Renderizar

```bash
python render.py VOC-001
```

Saída esperada:

`output/VOC-001.mp4`

## 6. Conferência técnica

Verifique:

- 720×1280
- 30 FPS
- H.264
- yuv420p
- AAC
- reprodução no Android sem erro
- imagem quadrada sem deformação
- background preenchendo 9:16
- ausência de barras pretas
- texto dentro da área segura
- narração sem drift
- click audível no fechamento quando o asset existir

## 7. Conferência visual contra VOC-001

Assistir o original e o gerado lado a lado. Avaliar hook inicial, escala da imagem, intensidade do blur, ritmo dos zooms/pans, peso/tamanho/cor do texto, posição do logo, CTA final e sincronismo de woosh/click.

O objetivo não é pixel-perfect. O critério é o vídeo automático estar publicável sem reconstrução no CapCut.

## 8. Áudio — ponto que exige calibração humana

O requisito informado foi “narração 30 a 40 dB”. Como `dB` sem referência não determina sozinho peak, RMS ou LUFS, a V0.1 mantém o ganho configurável e não força uma normalização que possa piorar o material. Na auditoria com a narração real, medir o arquivo e definir a métrica oficial antes de congelar esse parâmetro.

## 9. Gate de generalização

Depois do VOC-001, crie `products/VOC-002/` apenas trocando `product.json`, `script.json`, imagens e áudio. Não altere `src/voc/`.

O Gate passa quando VOC-002 renderiza corretamente com a mesma engine.

## 10. Hardcode audit

Nenhuma copy ou dado específico do produto deve existir em `src/`. O CI já verifica termos de exemplo. Faça também uma busca pelos termos reais do VOC-001 antes de considerar a V0.1 encerrada.
