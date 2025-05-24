import os
import sys
import subprocess
import platform

def print_header(message):
    """Imprime um cabeçalho formatado"""
    line = "=" * 70
    print(f"\n{line}\n{message.center(70)}\n{line}")

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print_header("Verificando versão do Python")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("⚠️  AVISO: Este sistema funciona melhor com Python 3.8 ou superior")
        print(f"   Versão atual: {version.major}.{version.minor}.{version.micro}")
        
        if input("Deseja continuar mesmo assim? (s/n): ").lower() != 's':
            sys.exit(1)
    else:
        print(f"✅ Versão do Python compatível: {version.major}.{version.minor}.{version.micro}")

def run_command(command):
    """Executa um comando no terminal e retorna o resultado"""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, 
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def install_talib():
    """Instala a biblioteca TA-Lib com instruções específicas por plataforma"""
    print_header("Instalando TA-Lib")
    
    system = platform.system().lower()
    
    if system == 'windows':
        print("Para Windows, é necessário instalar o TA-Lib manualmente:")
        print("1. Baixe o instalador em: https://ta-lib.org/hdr_dw.html")
        print("2. Instale a versão compatível com sua arquitetura (32 ou 64 bits)")
        print("3. Após instalação, execute: pip install TA-Lib")
        
        if input("Você já instalou o TA-Lib manualmente? (s/n): ").lower() == 's':
            success, output = run_command("pip install TA-Lib")
            if success:
                print("✅ TA-Lib instalado com sucesso!")
            else:
                print("❌ Erro ao instalar TA-Lib:")
                print(output)
                return False
        else:
            print("⚠️  A instalação do TA-Lib é obrigatória para o funcionamento do sistema")
            return False
            
    elif system == 'linux':
        print("Instalando TA-Lib no Linux...")
        
        # Instalar dependências
        print("Instalando dependências...")
        run_command("sudo apt-get update")
        run_command("sudo apt-get install -y build-essential")
        
        # Baixar e compilar TA-Lib
        print("Baixando e instalando TA-Lib...")
        commands = [
            "wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz",
            "tar -xvzf ta-lib-0.4.0-src.tar.gz",
            "cd ta-lib && ./configure && make && sudo make install",
            "pip install TA-Lib"
        ]
        
        for cmd in commands:
            success, output = run_command(cmd)
            if not success:
                print(f"❌ Erro ao executar: {cmd}")
                print(output)
                return False
        
        print("✅ TA-Lib instalado com sucesso!")
        
    elif system == 'darwin':  # macOS
        print("Instalando TA-Lib no macOS...")
        
        # Verificar se o Homebrew está instalado
        success, _ = run_command("which brew")
        if not success:
            print("❌ Homebrew não está instalado. Instalando...")
            run_command('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
        
        # Instalar TA-Lib
        print("Instalando TA-Lib via Homebrew...")
        success, output = run_command("brew install ta-lib")
        if not success:
            print("❌ Erro ao instalar TA-Lib:")
            print(output)
            return False
            
        # Instalar pacote Python
        success, output = run_command("pip install TA-Lib")
        if not success:
            print("❌ Erro ao instalar pacote Python TA-Lib:")
            print(output)
            return False
            
        print("✅ TA-Lib instalado com sucesso!")
        
    else:
        print(f"❌ Sistema operacional não suportado: {system}")
        return False
        
    return True

def install_dependencies():
    """Instala todas as dependências necessárias"""
    print_header("Instalando dependências")
    
    # Atualizar pip
    print("Atualizando pip...")
    run_command("python -m pip install --upgrade pip")
    
    # Instalar dependências do requirements.txt
    print("Instalando pacotes do requirements.txt...")
    success, output = run_command("pip install -r requirements.txt")
    
    if not success:
        print("❌ Erro ao instalar dependências:")
        print(output)
        print("Tentando instalar manualmente...")
        
        # Instalar pacotes individualmente se o requirements.txt falhar
        packages = [
            "pandas>=1.3.0",
            "numpy>=1.20.0",
            "yfinance>=0.1.70",
            "matplotlib>=3.4.0",
            "requests>=2.27.1",
            "beautifulsoup4>=4.9.0",
            "openpyxl>=3.0.0",
            "backtrader>=1.9.0",
            "pandas-datareader>=0.10.0",
            "investpy>=1.0.8"
        ]
        
        for package in packages:
            print(f"Instalando {package}...")
            run_command(f"pip install {package}")
    else:
        print("✅ Dependências principais instaladas com sucesso!")
    
    # Instalar TA-Lib
    talib_installed = install_talib()
    
    if talib_installed:
        print_header("Instalação concluída com sucesso!")
        print("Todas as dependências foram instaladas.")
        print("\nVocê pode começar a usar o sistema FuzzyFajuto:")
        print("  1. Para atualizar a lista de ativos: python b3_scraper.py")
        print("  2. Para executar o sistema: python fuzzy_fajuto_trading.py")
        print("  3. Para executar backtests: python backtest.py")
    else:
        print_header("⚠️ Instalação parcial")
        print("Algumas dependências não foram instaladas corretamente.")
        print("TA-Lib é necessário para o funcionamento do sistema.")
        print("Por favor, instale manualmente seguindo as instruções.")

def create_data_directories():
    """Cria os diretórios necessários para o sistema"""
    dirs = ["data", "results", "results/backtest", "logs"]
    for directory in dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Diretório criado: {directory}")

if __name__ == "__main__":
    print_header("Instalação do Sistema FuzzyFajuto Trading")
    print("Este script irá instalar todas as dependências necessárias para o sistema.")
    
    # Verificar versão do Python
    check_python_version()
    
    # Criar diretórios
    create_data_directories()
    
    # Instalar dependências
    install_dependencies() 