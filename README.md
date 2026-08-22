# Vale o Clique

Repositório do projeto **Vale o Clique**, iniciando pelo **Vale o Clique Video Engine V0.1**.

## Escopo atual

A V0.1 resolve apenas:

**input de produto -> MP4 publicável**

A Foundation separa dados factuais (`product.json`), roteiro (`script.json`), template visual e configuração de exportação. O renderer visual ainda não faz parte desta etapa.

## Preset de desenvolvimento

- 720x1280
- 30 FPS
- H.264 / yuv420p
- AAC

O preset 1080x1920 fica preparado para uma fase posterior, sem mudar a arquitetura.

## Validar um produto

```bash
python render.py VOC-001 --validate-only
```

Resultado esperado na Foundation:

```text
OK VOC-001: 1 scene(s), 3.000s, 720x1280@30fps, template=voc_v1
```

## Testes

```bash
python -m pip install -r requirements.txt
pytest -q
```

## Estrutura

```text
products/       inputs por produto
templates/      regras visuais configuráveis
config/         presets de render
assets/         branding, música, fontes e SFX
src/voc/        código do engine
tests/          testes automatizados
output/         vídeos gerados
```

O conteúdo específico de um produto não deve ser hardcoded em `src/`.
