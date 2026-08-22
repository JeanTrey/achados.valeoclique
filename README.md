# Vale o Clique Video Engine V0.1

Motor programático para transformar **dados + roteiro + imagens + áudio** em MP4 vertical publicável. Não automatiza CapCut.

## Status

Pipeline implementado: loader/validação → timeline determinística → composição 9:16 → background blur → imagem `contain` → textos adaptativos → branding/CTA → animações sutis → mix de narração/música/SFX → H.264/AAC.

Preset atual: **720×1280, 30 FPS**. O preset 1080×1920 existe apenas para migração futura.

## Executar

```bash
python -m pip install -r requirements.txt
python render.py VOC-001 --validate-only
python render.py VOC-001
```

`VOC-001` ainda exige os assets reais em `products/VOC-001/images/` e, opcionalmente, `audio/`. O engine não inventa dados ausentes.

## Testes

```bash
pytest -q
```

O teste end-to-end gera um vídeo sintético curto e verifica H.264, AAC, `yuv420p` e dimensões. GitHub Actions também executa compile, validação, testes e auditoria contra hardcode editorial.

## Áudio

A solicitação de narração “30 a 40 dB” foi preservada como requisito de calibração. Como dB isolado não define uma métrica digital (peak/RMS/LUFS), a V0.1 não aplica normalização destrutiva arbitrária. O ganho de narração é configurável no template; música e SFX permanecem abaixo dela. Quando `assets/sfx/cursor_click.wav` existe, ele é automaticamente posicionado no encerramento.

## Estrutura

- `products/VOC-XXX/`: fatos, roteiro, imagens e narração
- `templates/voc_v1.json`: aparência, branding e mix
- `config/preview.json`: 720p
- `src/voc/`: engine sem conteúdo específico de produto
- `assets/`: logo, fontes, música e SFX
- `output/`: MP4 gerado

Consulte `AUDIT_V0.1.md` para o checklist de validação final com os assets reais.
