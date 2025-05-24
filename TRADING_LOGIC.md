# Lógica do Sistema Fuzzy Fajuto

## 1. Cálculo dos Indicadores

### 1.1 Vetores Base
```python
# Vetores de dados
ibov_returns = []      # Retornos diários do IBOV
stock_returns = []     # Retornos diários do papel
close_prices = []      # Preços de fechamento
fuzzy_fajuto = []      # Score Fuzzy Fajuto

# Médias Móveis Exponenciais
ema_3 = []            # EMA 3 dias
ema_5 = []            # EMA 5 dias
ema_10 = []           # EMA 10 dias
ema_15 = []           # EMA 15 dias
ema_20 = []           # EMA 20 dias

# RSI
rsi_10 = []           # RSI 10 dias

# Parâmetros de Exposição
EXPOSURE_PER_POSITION = 15000  # Exposição fixa por posição
```

## 2. Cálculo do Score Fuzzy Fajuto

### 2.1 Comparação com IBOV
```python
# Se retorno do papel > retorno do IBOV
if stock_returns[today] > ibov_returns[today]:
    fuzzy_fajuto[today] += 1.0
# Se retorno do papel < retorno do IBOV
elif stock_returns[today] < ibov_returns[today]:
    fuzzy_fajuto[today] -= 1.0
```

### 2.2 Comparação com EMAs
```python
# EMA 3 dias
if close_prices[today] > ema_3[today]:
    fuzzy_fajuto[today] += 0.25
else:
    fuzzy_fajuto[today] -= 0.25

# EMA 5 dias
if close_prices[today] > ema_5[today]:
    fuzzy_fajuto[today] += 0.25
else:
    fuzzy_fajuto[today] -= 0.25

# EMA 10 dias
if close_prices[today] > ema_10[today]:
    fuzzy_fajuto[today] += 0.25
else:
    fuzzy_fajuto[today] -= 0.25

# EMA 15 dias
if close_prices[today] > ema_15[today]:
    fuzzy_fajuto[today] += 0.25
else:
    fuzzy_fajuto[today] -= 0.25

# EMA 20 dias
if close_prices[today] > ema_20[today]:
    fuzzy_fajuto[today] += 0.25
else:
    fuzzy_fajuto[today] -= 0.25
```

### 2.3 RSI
```python
# RSI 10 dias
if rsi_10[today] > 65:
    fuzzy_fajuto[today] += 0.25
elif rsi_10[today] < 35:
    fuzzy_fajuto[today] -= 0.25
```

## 3. Regras de Negociação

### 3.1 Cálculo de Quantidades
```python
def calculate_quantity(exposure, price):
    """
    Calcula quantidade em múltiplos de 100 para cada ordem
    """
    raw_quantity = (exposure / 4) / price  # Divide exposição por 4 ordens
    # Arredonda para o múltiplo de 100 mais próximo
    quantity = round(raw_quantity / 100) * 100
    # Garante quantidade mínima de 100
    return max(100, quantity)

def truncate_price(price, decimals=2):
    """
    Trunca o preço para o número especificado de casas decimais
    """
    factor = 10 ** decimals
    return int(price * factor) / factor
```

### 3.2 Sinais de Compra
```python
if fuzzy_fajuto[today] >= 1.50:
    # Calcula quantidade para cada ordem
    order_quantity = calculate_quantity(EXPOSURE_PER_POSITION, close_prices[today])
    
    # Preço base truncado
    base_price = truncate_price(close_prices[today], 2)
    
    # Ordens de compra para amanhã
    orders = [
        {
            'type': 'market',  # Ordem na abertura
            'price': None,
            'quantity': order_quantity
        },
        {
            'type': 'limit',
            'price': truncate_price(base_price * 0.995, 2),  # -0.5%
            'quantity': order_quantity
        },
        {
            'type': 'limit',
            'price': truncate_price(base_price * 0.99, 2),   # -1.0%
            'quantity': order_quantity
        },
        {
            'type': 'limit',
            'price': truncate_price(base_price * 0.985, 2),  # -1.5%
            'quantity': order_quantity
        }
    ]
```

### 3.3 Sinais de Venda
```python
if fuzzy_fajuto[today] <= -1.50:
    # Calcula quantidade para cada ordem
    order_quantity = calculate_quantity(EXPOSURE_PER_POSITION, close_prices[today])
    
    # Preço base truncado
    base_price = truncate_price(close_prices[today], 2)
    
    # Ordens de venda para amanhã
    orders = [
        {
            'type': 'market',  # Ordem na abertura
            'price': None,
            'quantity': order_quantity
        },
        {
            'type': 'limit',
            'price': truncate_price(base_price * 1.005, 2),  # +0.5%
            'quantity': order_quantity
        },
        {
            'type': 'limit',
            'price': truncate_price(base_price * 1.01, 2),   # +1.0%
            'quantity': order_quantity
        },
        {
            'type': 'limit',
            'price': truncate_price(base_price * 1.015, 2),  # +1.5%
            'quantity': order_quantity
        }
    ]
```

## 4. Implementação

### 4.1 Cálculo Diário
```python
def calculate_fuzzy_fajuto(today):
    """
    Calcula o score Fuzzy Fajuto para o dia atual
    """
    score = 0.0
    
    # Comparação com IBOV
    if stock_returns[today] > ibov_returns[today]:
        score += 1.0
    elif stock_returns[today] < ibov_returns[today]:
        score -= 1.0
    
    # Comparação com EMAs
    for ema in [ema_3, ema_5, ema_10, ema_15, ema_20]:
        if close_prices[today] > ema[today]:
            score += 0.25
        else:
            score -= 0.25
    
    # RSI
    if rsi_10[today] > 65:
        score += 0.25
    elif rsi_10[today] < 35:
        score -= 0.25
    
    return score
```

### 4.2 Geração de Ordens
```python
def generate_orders(today):
    """
    Gera ordens baseadas no score Fuzzy Fajuto
    """
    score = fuzzy_fajuto[today]
    orders = []
    
    if score >= 1.50:
        # Ordens de compra
        order_quantity = calculate_quantity(EXPOSURE_PER_POSITION, close_prices[today])
        base_price = truncate_price(close_prices[today], 2)
        orders = [
            {'type': 'market', 'price': None, 'quantity': order_quantity},
            {'type': 'limit', 'price': truncate_price(base_price * 0.995, 2), 'quantity': order_quantity},
            {'type': 'limit', 'price': truncate_price(base_price * 0.99, 2), 'quantity': order_quantity},
            {'type': 'limit', 'price': truncate_price(base_price * 0.985, 2), 'quantity': order_quantity}
        ]
    elif score <= -1.50:
        # Ordens de venda
        order_quantity = calculate_quantity(EXPOSURE_PER_POSITION, close_prices[today])
        base_price = truncate_price(close_prices[today], 2)
        orders = [
            {'type': 'market', 'price': None, 'quantity': order_quantity},
            {'type': 'limit', 'price': truncate_price(base_price * 1.005, 2), 'quantity': order_quantity},
            {'type': 'limit', 'price': truncate_price(base_price * 1.01, 2), 'quantity': order_quantity},
            {'type': 'limit', 'price': truncate_price(base_price * 1.015, 2), 'quantity': order_quantity}
        ]
    
    return orders
```

### 4.3 Validação de Ordens
```python
def validate_orders(orders):
    """
    Valida se todas as ordens estão em conformidade com as regras da B3
    """
    for order in orders:
        # Verifica se quantidade é múltiplo de 100
        if order['quantity'] % 100 != 0:
            raise ValueError(f"Quantidade {order['quantity']} não é múltiplo de 100")
        
        # Verifica quantidade mínima
        if order['quantity'] < 100:
            raise ValueError(f"Quantidade {order['quantity']} menor que o mínimo de 100")
        
        # Verifica preço mínimo (R$ 0,01)
        if order['type'] == 'limit' and order['price'] < 0.01:
            raise ValueError(f"Preço {order['price']} menor que o mínimo de R$ 0,01")
```

### 4.4 Exportação para Tryd Automate
```python
def export_to_tryd_automate(orders):
    """
    Exporta as ordens para o formato Tryd Automate
    """
    for order in orders:
        # Preço truncado para 2 casas decimais
        price = truncate_price(order['price'], 2) if order['price'] is not None else None
        print(f"{order['type']} {price} {order['quantity']}")
        
        # Preço Venda
        if order['type'] == 'market':
            print(f"Venda {price} {order['quantity']}")
``` 