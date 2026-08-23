# 03 — Histórico e Falhas

## VOC-001 — Referência manual / primeiro alvo

### Contexto
O primeiro vídeo manual serviu como referência de ritmo e linguagem. Auditoria técnica aproximada:

- 720x1280;
- 30 FPS;
- ~18,7 s;
- H.264/AAC;
- imagem quadrada sobre background desfocado;
- texto grande de leitura rápida;
- narração principal;
- música baixa;
- woosh seletivo;
- CTA final "VALE O CLIQUE?" + click.

### Resultado do primeiro motor automático
**REPROVADO criativamente.**

Problemas relatados/observados:

- narração sobreposta;
- falava demais;
- textos grandes e genéricos;
- fonte/cor/tamanho sem direção visual;
- woosh em excesso;
- abertura parecia entrar no meio de um anúncio;
- repetição da mesma imagem;
- aparência de slideshow.

### Aprendizado
A correção de sincronismo de áudio foi válida, mas mostrou que estabilidade técnica não resolve direção criativa.

---

## VOC-002 — tentativa de Creative Memory + Benchmark

### Intenção
Usar o mesmo produto para isolar mudanças no motor, incorporando feedback do VOC-001 e referências externas.

### Erros de pipeline encontrados
Durante a geração houve uma sequência útil de falhas técnicas:

- Retention Gate confundindo duração criativa com expansão do TTS;
- TTS inflando o vídeo;
- schema rejeitando `creative_duration`;
- incompatibilidades entre prepare/validator/model.

Esses bugs foram corrigidos e deixaram o pipeline mais robusto.

### Resultado criativo final
**REPROVADO FORTE.**

O vídeo mostrou que o sistema ainda fazia essencialmente:

`mesmo JPG -> troca de texto -> mesmo JPG -> troca de texto`

Problemas:

- sensação total de slideshow;
- nenhuma nova informação visual por cena;
- reaproveitamento excessivo do material manual;
- texto gigante e pobre;
- contraste agressivo amarelo/preto;
- falta de assets novos;
- falta de individualidade;
- benchmark não estava produzindo impacto visual real no criativo;
- alegação de "aprendizado" era maior que a evidência disponível.

### Correção conceitual
Foi decidido que:

1. referência textual não conta como vídeo visto;
2. benchmark real precisa processar mídia;
3. uma única imagem deve gerar derivados, mas crops não podem substituir entendimento semântico;
4. o renderer não deve ser o cérebro criativo.

---

## VOC-003 — Storyboard First

### Intenção
Parar de renderizar MP4 ruim antes de avaliar os frames-chave.

Foram adicionados:

- `creative_plan.json`;
- storyboard por cena;
- `contact_sheet.jpg`;
- revisão humana obrigatória antes de MP4.

### Primeiro storyboard
**REPROVADO**, mas o mecanismo de gate foi considerado correto.

Problemas observados:

- crops automáticos mutilando teclado/produto;
- seleção de áreas coloridas/textuais da própria arte como se fossem detalhe do produto;
- fundo branco/morto;
- cards cinza genéricos;
- tipografia ainda automática demais;
- preço sem tratamento convincente;
- CTA fraco;
- baixa individualidade visual.

### Mudanças subsequentes
O Asset Director passou a penalizar crops planos/saturados e considerar formato horizontal. O storyboard ganhou fundo reconstruído/desfocado, composição mais limpa e copy menor.

### Situação
A abordagem **Storyboard First permanece aprovada como arquitetura**, mas o diretor visual ainda está em desenvolvimento.

---

## O que não devemos repetir

- polir continuamente um template que já nasceu com lógica errada;
- tratar crop como entendimento visual;
- chamar referências editoriais de treinamento real;
- declarar número de vídeos analisados sem evidência;
- usar mudança de texto como mudança de cena;
- depender do usuário para fornecer cada JPG;
- usar MP4 válido como critério de sucesso;
- renderizar antes de validar storyboard;
- deixar preço/CTA/hook com o mesmo layout genérico de proof;
- usar IA de contexto como prova factual.

## Conclusão histórica

Os três experimentos não foram desperdício: eles delimitaram o problema. O gargalo principal não é FFmpeg, timeline ou encode. O gargalo é **entendimento criativo e visual do produto**. A próxima arquitetura deve ser construída em torno disso.