# Driftkings Tactical Minimap V2 — protótipo isolado

**O renderer não substitui o minimapa em batalha. Existe uma ponte diagnóstica opt-in, desligada por defeito; ver TESTE_GAMEFACE.md.**

Abrir [preview.html](preview.html) num navegador para explorar os três temas, os ícones vetoriais próprios, as cores, a grelha e os ajustes de tamanho/contraste/escala. Todos os veículos e posições são inventados. Não há cartografia copiada do cliente, fetch, telemetria ou ligação ao jogo. Os controlos ajustam só esta página; não são o painel Settings do mod.

- [Auditoria obrigatória, Fase 0](AUDITORIA.md).
- [Arquitetura e fronteiras](ARQUITETURA.md).
- [Compatibilidade e matriz de testes](COMPATIBILIDADE.md).
- [Etapa 3: testar a ponte diagnóstica no jogo](TESTE_GAMEFACE.md).
- [Etapa 2: contratos e adaptador nativo](CONTRATOS_NATIVOS.md).
- [Avaliação Fair Play](FAIR_PLAY.md).

## O que está entregue

Protótipo HTML/CSS/JS ES5, SVG próprios em `icons/`, política pura Python 2.7/3 em `Driftkings/core/tactical_minimap.py`, transformação de coordenadas retangulares e orientação de referência, contrato sintético sem retenção de posições, seleção com fallback obrigatório Vanilla e testes Python/Node. O recurso gráfico Lost Contact é apenas uma referência, não é carregado pelo renderer.

O protótipo visual, os SVG e os documentos ficam fora do WOTMOD. A etapa 3 acrescenta ao manifesto um recurso R, HTML/CSS/JS e uma ponte Python separados, apenas para diagnóstico opt-in. Estes não ativam o renderer nem a política de substituição.

## O que falta para as Fases 1–9 em produção

Resolver e validar o transporte completo de entradas e os contratos de input Flash/C++; testar a capacidade do Gameface para desenhar e interagir sem quebrar comandos; implementar handshake/fallback de ponta a ponta; integrar `minimapMode` nos JSON/Settings/perfis e traduções existentes; publicar os recursos do renderer real, além dos recursos diagnósticos já disponíveis; validar cada modo/replay; testar desempenho e obter confirmação adequada para Lost Contact. Só depois disponibilizar seleção Driftkings ao jogador.

Os testes de `selection()` preservam a preferência pedida sem a trocar silenciosamente: devolvem também o modo efetivo Vanilla e uma razão do bloqueio. Isto é infraestrutura, não persistência de perfis já integrada.

## Verificações reproduzíveis

```powershell
python -B -m unittest discover -s tests/core -p 'test_*.py'
F:/Python27/python.exe -B -m unittest discover -s tests/core -p 'test_*.py'
node tests/settings_panel/test_tactical_minimap.js
npm run lint
python -B build_tools/validate_build_data.py
```

A CI executa os testes novos juntamente com os existentes. A aparência não foi verificada automaticamente num navegador nesta sessão: a ferramenta de browser não tinha nenhuma superfície disponível. A conformidade ES5, a estrutura DOM e o comportamento incremental foram verificados por testes; isto não substitui a inspeção visual ou o teste no Gameface.

Etapa 2: foi acrescentado um adaptador de leitura nativo **não instalado**, com origem de snapshot diferente e recusada pelo preview. Ver CONTRATOS_NATIVOS.md para os filtros conservadores, a matemática de input e as limitações. A seleção em Settings e o renderer de batalha continuam por integrar.

Etapa 3: a ponte Gameface transporta só um resumo de diagnóstico, nunca os snapshots/posições do adapter. Está desligada por defeito. A utilização do renderer como minimapa de batalha e a seleção de modo continuam pendentes.
