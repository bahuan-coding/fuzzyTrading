import os
import json
from datetime import datetime

# Diretórios do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
BACKTEST_DIR = os.path.join(RESULTS_DIR, "backtest")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Arquivo de configuração
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

# Configurações globais
CONFIG = {
    # Configurações do modelo
    "model": {
        # Máximo de posições por lado (compra/venda)
        "max_position_per_side": 15,
        
        # Exposição financeira total (R$)
        "exposicao_financeira_total": 100000,
        
        # Dias de histórico para análise
        "lookback_days": 60,
        
        # Máximo de ordens por ativo (limitado/mercado)
        "max_orders_per_stock": 2,
        
        # Exposição máxima por ativo (% do total por lado)
        "max_exposure_per_stock": 0.08,  # 8%
        
        # Tamanho mínimo de posição em R$
        "min_position_size": 1000,
        
        # Usar componentes do IBRA
        "use_ibra_components": True,
        
        # Opções de agressividade (quanto maior, mais agressivo)
        "agressividade": {
            "ordem_execucao": 0.75,  # 0.0 a 1.0
            "tamanho_posicao": 0.5   # 0.0 a 1.0
        }
    },
    
    # Configurações de mercado
    "market": {
        # Símbolo do índice de referência
        "ibov_symbol": "^BVSP",
        
        # Número de ações do IBRA a considerar
        "num_ibra_stocks": 100,
        
        # Atualização automática da lista de ativos
        "auto_update_assets": True,
        
        # Intervalo de atualização em horas
        "update_interval_hours": 24
    },
    
    # Configurações de indicadores
    "indicators": {
        # Períodos das EMAs
        "ema_periods": [3, 5, 10, 15, 20],
        
        # Período do RSI
        "rsi_period": 10,
        
        # Limiar de sobrecompra
        "overbought_threshold": 70,
        
        # Limiar de sobrevenda
        "oversold_threshold": 30
    },
    
    # Configurações de execução
    "execution": {
        # Gerar ordens a mercado
        "include_market_orders": True,
        
        # Gerar ordens limitadas
        "include_limit_orders": False,
        
        # Ajuste para ordens de compra a mercado (%) para garantir execução
        "market_buy_adjustment": 0.05,  # 5% acima do preço base
        
        # Ajuste para ordens de venda a mercado (%) para garantir execução
        "market_sell_adjustment": -0.05,  # 5% abaixo do preço base
        
        # Variação de preço para ordens limitadas (%)
        "price_increments": 0.02,  # 2%
        
        # Tamanho de lote padrão para ações caras (>R$50)
        "lot_size_expensive": 10,
        
        # Tamanho de lote padrão para ações normais
        "lot_size_normal": 100
    },
    
    # Configurações de dados
    "data": {
        # Fonte de dados
        "source": "yfinance",
        
        # Índice de referência
        "benchmark": "^BVSP",
        
        # Lista de ações - modo automático (IBRA = top 100 da B3 em liquidez)
        "stocks_mode": "IBRA",
        
        # Número máximo de ações no modo automático
        "stocks_limit": 100,
        
        # Lista manual de ações (usado se stocks_mode = MANUAL)
        "stocks_list": [
            "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA",
            "B3SA3.SA", "ABEV3.SA", "WEGE3.SA", "RENT3.SA"
        ]
    },
    
    # Configurações de logs
    "logs": {
        # Nível de detalhamento (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        "level": "INFO",
        
        # Diretório de logs
        "dir": "./logs/",
        
        # Formato do log
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    
    # Configurações de saída
    "output": {
        # Diretório de resultados
        "dir": "./results/",
        
        # Diretório de relatórios
        "reports_dir": "./results/reports/",
        
        # Arquivo Excel para Tryd Automate
        "tryd_automate_file": "automate.xlsx"
    },
    
    # Configurações de backtest
    "backtest": {
        # Período padrão em dias
        "default_period_days": 365,
        
        # Taxa de corretagem
        "commission_rate": 0.001,
        
        # Plotar resultados
        "plot_results": True,
        
        # Salvar resultados
        "save_results": True,
        
        # Frequência de rebalanceamento (dias)
        "rebalance_frequency": 1
    }
}

# Configuração padrão em caso de erro
DEFAULT_CONFIG = CONFIG.copy()

# Variável global para armazenar a configuração atual
CONFIG = {}

def ensure_directories():
    """Garante que todos os diretórios necessários existam"""
    for directory in [DATA_DIR, RESULTS_DIR, BACKTEST_DIR, LOG_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)

def save_config():
    """Salva o dicionário de configuração em um arquivo JSON"""
    ensure_directories()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(CONFIG, f, ensure_ascii=False, indent=4)
    print(f"Configuração salva em: {CONFIG_FILE}")

def load_config():
    """Carrega a configuração do arquivo JSON, ou usa a padrão se não existir"""
    global CONFIG
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                CONFIG = json.load(f)
            print(f"Configuração carregada de: {CONFIG_FILE}")
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            print("Usando configuração padrão")
            CONFIG = DEFAULT_CONFIG.copy()
            save_config()
    else:
        print("Arquivo de configuração não encontrado. Usando configuração padrão.")
        CONFIG = DEFAULT_CONFIG.copy()
        save_config()
    
    return CONFIG

def get_config():
    """Retorna a configuração atual"""
    if not CONFIG:
        load_config()
    return CONFIG

def update_config(category, param, value):
    """
    Atualiza um parâmetro específico na configuração
    
    Args:
        category (str): Categoria do parâmetro (ex: 'model', 'market')
        param (str): Nome do parâmetro
        value: Novo valor
    """
    if not CONFIG:
        load_config()
        
    if category in CONFIG and param in CONFIG[category]:
        CONFIG[category][param] = value
        save_config()
        print(f"Configuração atualizada: {category}.{param} = {value}")
    else:
        print(f"Erro: parâmetro '{category}.{param}' não encontrado na configuração")

# Inicializar configuração ao importar o módulo
load_config() 