# Sistema de Balanceamento de Posições

## Visão Geral

O sistema implementa uma estratégia de balanceamento de posições que visa manter a exposição líquida (net) o mais próxima possível de zero, distribuindo o capital de forma otimizada entre posições compradas e vendidas.

## Princípios Fundamentais

1. **Neutralidade de Capital**
   - Exposição total dividida igualmente entre compras e vendas
   - Exemplo: Com R$ 50.000,00, R$ 25.000,00 para compras e R$ 25.000,00 para vendas

2. **Seleção de Ativos**
   - Compra: Score FuzzyFajuto ≥ 1.50
   - Venda: Score FuzzyFajuto ≤ -1.50
   - Ordenação por magnitude do score e preço

3. **Limites de Exposição**
   - Máximo de posições por lado: 15 (configurável)
   - Exposição máxima por ativo: 8% do lado
   - Tamanho mínimo de posição: R$ 1.000,00

## Processo de Balanceamento

### 1. Seleção Inicial
```python
# Exemplo de seleção
buy_candidates = [
    {'symbol': 'PETR4', 'score': 2.0, 'price': 32.50},
    {'symbol': 'VALE3', 'score': 1.8, 'price': 65.20}
]

sell_candidates = [
    {'symbol': 'ITUB4', 'score': -2.0, 'price': 28.90},
    {'symbol': 'BBDC4', 'score': -1.9, 'price': 15.75}
]
```

### 2. Distribuição de Capital
- Cálculo da exposição por ativo:
  ```python
  exposicao_por_lado = exposicao_total / 2
  exposicao_por_ativo = min(
      exposicao_por_lado / num_posicoes,
      exposicao_por_lado * max_exposure_per_stock
  )
  ```

### 3. Ajuste de Quantidades
- Quantidades calculadas em lotes:
  - Ações normais: múltiplos de 100
  - Ações caras (>R$50): múltiplos de 10
- Ajuste para respeitar limites:
  ```python
  quantidade = min(
      exposicao_por_ativo / preco,
      max_exposure_per_stock / preco
  )
  ```

### 4. Balanceamento Final
1. Ordenar posições por score e exposição
2. Selecionar número igual de posições em cada lado
3. Ajustar quantidades para minimizar diferença líquida

## Exemplo Prático

```python
# Exemplo de balanceamento
portfolio = {
    'buys': [
        {'symbol': 'PETR4', 'qty': 307, 'price': 32.50, 'exposure': 9977.50},
        {'symbol': 'VALE3', 'qty': 153, 'price': 65.20, 'exposure': 9975.60}
    ],
    'sells': [
        {'symbol': 'ITUB4', 'qty': 345, 'price': 28.90, 'exposure': 9970.50},
        {'symbol': 'BBDC4', 'qty': 633, 'price': 15.75, 'exposure': 9969.75}
    ]
}

# Resultado
exposicao_compra = 19953.10
exposicao_venda = 19940.25
exposicao_net = 12.85 (0.06% de diferença)
```

## Monitoramento e Ajustes

### 1. Relatório de Risco
- Exposição total por lado
- Exposição líquida (net)
- Concentração de posições (HHI)
- Maiores posições

### 2. Ajustes Automáticos
- Redução de posições mais caras se necessário
- Aumento gradual de limites para ativos com melhor score
- Rebalanceamento diário

## Configurações

```json
{
    "model": {
        "max_position_per_side": 15,
        "exposicao_financeira_total": 50000.0,
        "max_exposure_per_stock": 0.08
    }
}
```

## Boas Práticas

1. **Diversificação**
   - Evitar concentração em setores
   - Limitar exposição por ativo
   - Manter número similar de posições em cada lado

2. **Gestão de Risco**
   - Monitorar exposição líquida
   - Ajustar quantidades para lotes viáveis
   - Considerar liquidez dos ativos

3. **Otimização**
   - Priorizar ativos com melhor score
   - Balancear por valor monetário
   - Manter tolerância de 2% para diferenças

## Troubleshooting

1. **Exposição Desbalanceada**
   - Verificar limites por ativo
   - Ajustar quantidades para lotes
   - Considerar ativos alternativos

2. **Posições Muito Pequenas**
   - Aumentar exposição por ativo
   - Reduzir número de posições
   - Focar em ativos mais baratos

3. **Falta de Oportunidades**
   - Ajustar thresholds de score
   - Revisar lista de ativos
   - Considerar diferentes timeframes 