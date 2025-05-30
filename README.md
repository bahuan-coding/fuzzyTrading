# 🎯 Fuzzy Fajuto Trading System

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Um sistema de trading neutro para ações brasileiras (B3) que utiliza uma combinação de indicadores técnicos para selecionar ações para posições compradas e vendidas.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Configuração](#-configuração)
- [Funcionalidades](#-funcionalidades)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Aviso Legal](#-aviso-legal)
- [Manutenção](#-manutenção)

## 🎯 Visão Geral

O sistema Fuzzy Fajuto utiliza um mecanismo de pontuação baseado em três componentes:

1. **Componente 1 (Retorno vs Benchmark)**
   - Compara o retorno diário da ação com o retorno do benchmark (Ibovespa)

2. **Componente 2 (EMAs)**
   - Compara o preço de fechamento com múltiplas EMAs (3, 5, 10, 15, 20)

3. **Componente 3 (RSI)**
   - Avalia se a ação está sobrecomprada ou sobrevendida baseado no RSI(10)

O sistema gera uma pontuação entre -2.75 e +2.75 para cada ação. As pontuações mais positivas são consideradas para posições compradas, e as mais negativas para posições vendidas.

## 📦 Requisitos

- Python 3.7+
- TA-Lib
- yfinance
- pandas
- numpy
- openpyxl

## 🚀 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/bahuan-coding/fuzzyTrading.git
   cd fuzzyTrading
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

> **Nota**: Você precisará instalar o TA-Lib separadamente. Veja as [Instruções de Instalação do TA-Lib](https://github.com/mrjbq7/ta-lib).

## 💻 Uso

Execute o script principal:
```bash
python fuzzy_fajuto_trading.py
```

O sistema irá:
1. Baixar dados de mercado para uma lista predefinida de ações
2. Calcular indicadores técnicos
3. Gerar scores Fuzzy Fajuto
4. Selecionar ações para posições compradas e vendidas
5. Gerar ordens no formato Tryd Automate (exportado para `automate.xlsx`)

## ⚙️ Configuração

Edite o dicionário `CONFIG` no arquivo `config.py` para personalizar:
- `model.max_position_per_side`: Número máximo de posições por lado (compra/venda)
- `model.exposicao_financeira_total`: Exposição financeira total (R$)
- `indicators`: Parâmetros para os indicadores técnicos
- `execution`: Configurações de execução de ordens

## 🛠️ Funcionalidades

### 1. Coleta de Dados
- Download automático de dados históricos via Yahoo Finance
- Sistema de cache inteligente
- Suporte para múltiplos ativos simultâneos
- Tratamento de dados faltantes

### 2. Análise Técnica
- Cálculo de EMAs (3, 5, 10, 15, 20 períodos)
- Cálculo de RSI (10 períodos)
- Comparação com benchmark (Ibovespa)
- Cálculo de retornos diários

### 3. Sistema de Pontuação
- Score composto por três componentes
- Normalização de scores
- Filtros de qualidade para seleção de ativos

### 4. Geração de Ordens
- Exportação para formato Tryd Automate
- Cálculo automático de quantidades
- Ajuste de exposição financeira
- Geração de relatórios de risco

### 5. Logging e Monitoramento
- Sistema de logs detalhado
- Registro de erros e exceções
- Monitoramento de performance

### 6. Balanceamento de Posições
- Sistema de balanceamento automático
- Algoritmo de otimização para minimizar exposição líquida
- Priorização de pares de operações
- Ajuste dinâmico de quantidades

## 📁 Estrutura do Projeto

```
fuzzyTrading/
├── fuzzy_fajuto_trading.py    # Script principal
├── config.py                  # Configurações
├── requirements.txt           # Dependências
├── logs/                      # Arquivos de log
├── results/                   # Resultados e relatórios
├── data/                      # Dados históricos e cache
├── templates/                 # Templates para geração de ordens
└── README.md                  # Este arquivo
```

## ⚠️ Aviso Legal

Este sistema de trading é fornecido apenas para fins educacionais. Sempre realize sua própria análise e avaliação de risco antes de operar. Resultados passados não garantem resultados futuros.

## 🔄 Manutenção

O sistema é mantido e atualizado regularmente. Para reportar bugs ou sugerir melhorias, por favor abra uma issue no repositório.

Para detalhes técnicos adicionais sobre a implementação, consulte o arquivo `IMPLEMENTATION.md`.

# Tryd Automatizador

## Colunas do Template
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

## Uso
1. Copie automate_template.xlsx
2. Preencha as ordens
3. Salve como automate.xlsx

## Regras
- Quantidade: Múltipla de 100
- Preço: Preço atual
- Condição: DIA/GTC

# tryd_automate.py

from openpyxl import load_workbook

def generate_orders(portfolio):
    """Gera ordens no formato Tryd"""
    template = load_workbook('templates/tryd/automate_template.xlsx')
    ws = template.active
    
    # Preenche ordens
    for i, order in enumerate(portfolio, start=2):
        ws.cell(row=i, column=1, value=order['Papel'])
        ws.cell(row=i, column=6, value=order['Qtd. Compra'])
        ws.cell(row=i, column=7, value=order['Preço Compra'])
        ws.cell(row=i, column=8, value=order['Preço Venda'])
        ws.cell(row=i, column=9, value=order['Qtd. Venda'])
    
    template.save('automate.xlsx')