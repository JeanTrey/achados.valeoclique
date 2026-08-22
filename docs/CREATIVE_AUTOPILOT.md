# Creative Autopilot — Vale o Clique

## Objetivo

Reduzir o input operacional para algo próximo de:

`dados + imagens do produto -> roteiro -> narração -> música -> SFX -> vídeo`

sem acoplar essa lógica ao renderer.

## Roteiro

`src/voc/creative.py` gera uma estrutura editorial curta usando somente informações presentes em `ProductData`.

Regras:
- não inventa preço, avaliação, vendidos ou características;
- `seller_claim` vira narração atribuída: `Segundo o anúncio, ...`;
- preço usa a data de consulta quando disponível;
- fechamento padrão mantém `VALE O CLIQUE?`.

O roteiro automático é um ponto de partida editorial e deve continuar auditável antes de publicação em produção.

## Narração

`src/voc/narration.py` implementa um primeiro provedor TTS com `edge-tts`, desacoplado do renderer.

- voz padrão inicial: `pt-BR-AntonioNeural`;
- texto exato da narração é salvo ao lado do áudio;
- arquivos gerados permanecem no produto para que novos renders sejam reproduzíveis;
- no futuro o provedor pode ser trocado sem alterar o renderer.

O requisito de volume de narração entre 30 e 40 dB continua pendente de definição da métrica objetiva (peak/RMS/LUFS). Não será aplicado ganho arbitrário apenas para satisfazer um número ambíguo.

## Música

`src/voc/sound_design.py` gera uma cama musical instrumental original e determinística.

Isso foi escolhido para a V0.1 em vez de baixar uma faixa aleatória chamada de “sem copyright”. Uma música de biblioteca normalmente ainda possui copyright e apenas concede uma licença de uso. A síntese local evita redistribuição de gravação de terceiros e facilita reprodutibilidade.

Parâmetros atuais:
- aproximadamente 104 BPM;
- instrumental eletrônico discreto;
- mix pensado para ficar abaixo da narração;
- seed fixa para reprodução idêntica.

## Efeitos sonoros

Também são gerados localmente:
- `woosh.wav`;
- `cursor_click.wav`.

O woosh é aplicado seletivamente pelas cenas. O cursor click continua reservado ao encerramento.

## Preparação automática

Com dependências instaladas:

```bash
python prepare.py VOC-001
python render.py VOC-001
```

`prepare.py`:
1. carrega dados factuais;
2. gera cenas editoriais;
3. associa imagens existentes em `products/VOC-XXX/images/`;
4. cria texto da narração;
5. sintetiza a voz;
6. gera música original;
7. gera SFX padrão se estiverem ausentes;
8. grava `script.json`;
9. deixa o projeto pronto para o renderer.

Para testar apenas a estrutura sem chamar TTS remoto:

```bash
python prepare.py VOC-001 --no-tts
```

## Próximo Gate

Ainda precisamos recuperar/adicionar as imagens originais do anúncio do KV-789. A identificação do produto já foi confirmada, mas o short-link original não pôde ser resolvido automaticamente no ambiente de pesquisa.
