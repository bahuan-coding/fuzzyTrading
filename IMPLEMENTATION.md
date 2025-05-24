# Implementação do Sistema Fuzzy Fajuto

## Estrutura de Diretórios

```
fuzzy_fajuto/
├── data/                  # Dados históricos e cache
│   ├── quotes/           # Cotações diárias
│   └── cache/            # Cache de dados
├── logs/                 # Logs do sistema
├── results/             # Resultados e relatórios
│   ├── reports/         # Relatórios de risco
│   └── backtest/        # Resultados de backtest
├── templates/           # Templates do sistema
│   └── tryd/            # Templates do Tryd
│       ├── automate_template.xlsx  # Template base do Tryd
│       └── config.json            # Configurações do template
└── src/                 # Código fonte
    ├── fuzzy_fajuto_trading.py    # Script principal
    ├── config.py                  # Configurações
    └── requirements.txt           # Dependências
```

## Armazenamento Local

### 1. Cache de Cotações
- Sistema inteligente de cache que evita downloads redundantes
- Armazenamento em `data/quotes/` com nome de arquivo baseado na data
- Verificação de existência antes de download

### 2. Logs do Sistema
- Armazenados em `logs/` com timestamp
- Níveis: DEBUG, INFO, WARNING, ERROR
- Rotação diária de logs

### 3. Resultados
- Relatórios de risco em `results/reports/`
- Resultados de backtest em `results/backtest/`
- Nomenclatura: `YYYYMMDD_HHMMSS_*`

## Integração com Tryd

### 1. Template Base
- Localização: `templates/tryd/automate_template.xlsx`
- Estrutura padrão do Tryd Automatizador
- Colunas obrigatórias:
  - Papel: Código do ativo (ex: PETR4)
  - Cód. Cliente: Código do cliente
  - Cond. Compra: Condição de compra
  - Máx. Qtd. Compra: Quantidade máxima
  - Qtd. Apar. Compra: Quantidade aparada
  - Qtd. Compra: Quantidade final
  - Preço Compra: Preço de compra
  - Preço Venda: Preço de venda
  - Qtd. Venda: Quantidade venda
  - Qtd. Apar. Venda: Quantidade aparada venda
  - Máx. Qtd. Venda: Quantidade máxima venda
  - Cond. Venda: Condição de venda
  - Observação: Comentários

### 2. Geração de Ordens
```python
def truncate_price(price, decimals=2):
    """
    Trunca o preço para o número especificado de casas decimais
    """
    factor = 10 ** decimals
    return int(price * factor) / factor

def export_to_tryd_automate(orders, output_file='automate.xlsx'):
    """
    Exporta ordens para o formato Tryd Automatizador
    """
    # Carregar template
    wb = load_workbook('templates/tryd/automate_template.xlsx')
    ws = wb.active
    
    # Preencher ordens
    for order in orders['buys']:
        # Garantir que o preço seja truncado para exatamente 2 casas decimais
        price = truncate_price(order['price'], 2) if order['price'] is not None else None
        ws.append([
            order['symbol'],           # Papel
            CONFIG['client_code'],     # Cód. Cliente
            'DIA',                     # Cond. Compra
            order['quantity'],         # Máx. Qtd. Compra
            order['quantity'],         # Qtd. Apar. Compra
            order['quantity'],         # Qtd. Compra
            price,                     # Preço Compra
            None,                      # Preço Venda
            None,                      # Qtd. Venda
            None,                      # Qtd. Apar. Venda
            None,                      # Máx. Qtd. Venda
            None,                      # Cond. Venda
            f"Score: {order['score']}" # Observação
        ])
    
    for order in orders['sells']:
        # Garantir que o preço seja truncado para exatamente 2 casas decimais
        price = truncate_price(order['price'], 2) if order['price'] is not None else None
        ws.append([
            order['symbol'],           # Papel
            CONFIG['client_code'],     # Cód. Cliente
            None,                      # Cond. Compra
            None,                      # Máx. Qtd. Compra
            None,                      # Qtd. Apar. Compra
            None,                      # Qtd. Compra
            None,                      # Preço Compra
            price,                     # Preço Venda
            order['quantity'],         # Qtd. Venda
            order['quantity'],         # Qtd. Apar. Venda
            order['quantity'],         # Máx. Qtd. Venda
            'DIA',                     # Cond. Venda
            f"Score: {order['score']}" # Observação
        ])
    
    # Salvar arquivo
    wb.save(output_file)
```

### 3. Configurações do Template
```json
{
    "version": "1.0",
    "client_code": "1234",
    "defaults": {
        "condition": "DIA",
        "min_quantity": 100,
        "quantity_multiple": 100
    },
    "columns": {
        "papel": "A",
        "cod_cliente": "B",
        "cond_compra": "C",
        "max_qtd_compra": "D",
        "qtd_apar_compra": "E",
        "qtd_compra": "F",
        "preco_compra": "G",
        "preco_venda": "H",
        "qtd_venda": "I",
        "qtd_apar_venda": "J",
        "max_qtd_venda": "K",
        "cond_venda": "L",
        "obs": "M"
    }
}
```

## Lista de Papéis

### 1. Fonte de Dados
- Lista principal em `data/stocks_list.txt`
- Atualização automática via `get_stocks_list()`
- Filtros aplicados:
  - Liquidez mínima
  - Preço mínimo
  - Volume mínimo

### 2. Processamento
```python
def get_stocks_list():
    """
    Obtém lista de papéis para análise
    """
    # Carregar lista base
    with open('data/stocks_list.txt', 'r') as f:
        symbols = f.read().splitlines()
    
    # Aplicar filtros
    filtered = [
        symbol for symbol in symbols
        if meets_liquidity_criteria(symbol)
        and meets_price_criteria(symbol)
        and meets_volume_criteria(symbol)
    ]
    
    return filtered
```

## Execução Local

### 1. Requisitos
- Python 3.7+
- Dependências em `requirements.txt`
- TA-Lib instalado
- Excel para visualização

### 2. Comandos
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar sistema
python fuzzy_fajuto_trading.py

# Gerar relatório específico
python fuzzy_fajuto_trading.py --report-only
```

### 3. Saídas
- `automate.xlsx`: Ordens para Tryd
- `risk_report_*.txt`: Relatório de risco
- Logs em `logs/`
- Cache em `data/cache/`

## Manutenção

### 1. Cache
- Limpeza automática após 30 dias
- Backup antes de limpeza
- Log de operações

### 2. Logs
- Rotação diária
- Compressão após 7 dias
- Retenção por 90 dias

### 3. Templates
- Versionamento em `templates/tryd/`
- Backup antes de atualizações
- Validação de estrutura 