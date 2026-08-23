# 07 — Decisões, Limitações e Pendências

## Decisões não negociáveis

### Execução local durante refatoração
Durante a fase atual, desenvolvimento e testes rápidos devem ocorrer localmente no PC. GitHub fica como versionamento, backup e CI. Evitar usar Actions como loop principal de design.

### Storyboard antes de vídeo
Nenhum novo MP4 deve ser considerado etapa padrão sem storyboard aprovado.

### Sem dependência obrigatória de JPG manual
Import manual continua permitido como fallback, mas o fluxo-alvo parte de URL e pesquisa automática.

### Sem fatos inventados
Seller claims continuam atribuídos. IA não altera especificações.

### Contexto sintético não é evidência
Cena gerada por IA pode representar problema/uso/ambientação. Não pode provar alcance, material, tamanho, resistência, acessórios ou qualquer característica específica.

### Benchmark comprovável
Só mídia realmente processada entra no contador de vídeos analisados. Artigos, páginas de prêmio e guias são referências, não vídeos vistos.

### Não copiar criativos de terceiros
Benchmark extrai padrões estruturais e estatísticos. Não deve copiar roteiro, mídia, música, identidade ou composição específica de um anúncio.

### Creative Memory não é fine-tuning
A memória atual é um sistema explícito de feedback, regras e preferências. Não deve ser descrita como treinamento de modelo.

## Limitações atuais conhecidas

1. **Shopee dinâmica/anti-bot:** o collector pode não recuperar galeria/vídeo completo.
2. **Sem visão semântica robusta:** crops e classificação ainda dependem de heurísticas.
3. **Benchmark estrutural limitado:** FFmpeg não entende intenção/composição.
4. **Tipografia/design ainda heurísticos:** não há Art Director multimodal.
5. **TTS é provider protótipo:** qualidade/ritmo precisa de direção por cena.
6. **Música procedural é segura para protótipo, mas pode soar genérica.**
7. **Sem métricas próprias de performance ainda:** decisões são baseadas em feedback humano + referência externa.
8. **Produto de teste repetido:** VOC-001/002/003 usam KV-789; generalização ainda não foi comprovada em categorias diferentes.

## Riscos técnicos

### Acoplamento entre formatos de JSON e modelos
Já houve quebra por introdução de `creative_duration` sem atualização completa do schema. Toda evolução de contrato deve atualizar modelo, validator, loader, testes e fixtures juntos.

### Heurística fingindo inteligência
Scores simples de contraste, saturação ou contagem de palavras podem parecer automação inteligente e ainda gerar resultados ruins. Sempre exigir evidência visual.

### Pipeline silenciosamente degradado
Se collector/benchmark falhar, o sistema deve registrar claramente quantos assets/vídeos conseguiu processar. Não pode continuar e apresentar baixa evidência como sucesso completo.

### Custo/latência de visão multimodal
Benchmark Vision e Asset Curator semântico podem aumentar custo e tempo. Precisamos de cache, keyframes e análise seletiva.

## Pendências de produto

- Definir se a primeira versão comercial suporta somente Shopee ou múltiplos marketplaces.
- Definir qual provider multimodal será usado localmente/produção.
- Definir provider de TTS final.
- Definir política de geração de imagens contextuais.
- Definir fontes e identidade de marca oficiais do Vale o Clique.
- Definir critérios mínimos de desempenho quando existirem métricas próprias.
- Definir publicação automática apenas depois da qualidade criativa ficar estável.

## Próximo teste correto

Depois da refatoração do Product Researcher + Asset Curator + Creative/Art Director V2, testar com **um produto novo de categoria diferente**, não outro clone do KV-789.

O teste deve começar somente com a URL do produto e medir:

- quantos dados foram recuperados;
- quantos assets foram recuperados;
- quais assets foram rejeitados;
- qual estratégia foi escolhida e por quê;
- storyboard produzido;
- resultado do gate;
- intervenção manual necessária.

## Pergunta que deve guiar cada commit

> Esta mudança aproxima o sistema de tomar uma decisão criativa melhor para um produto novo ou apenas deixa o template atual mais sofisticado?

Se a resposta for apenas "melhora o template", provavelmente não é prioridade.