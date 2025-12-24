
"""
Wrapper robusto para iniciar o servidor MCP.
Garante que o diretório do projeto esteja no sys.path e define o CWD correto,
independentemente de como o processo foi iniciado.
"""
import sys
import os
from pathlib import Path

# 1. Configura caminhos
current_file = Path(__file__).resolve()
project_root = current_file.parent

# 2. Adiciona raiz ao sys.path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 3. Força CWD para a raiz do projeto (para templates/arquivos funcionarem)
try:
    os.chdir(project_root)
except Exception as e:
    print(f"Erro ao definir CWD: {e}", file=sys.stderr)

# 4. Inicia o servidor
try:
    from src import server
    server.main()
except ImportError as e:
    print(f"Erro de importação crítico: {e}", file=sys.stderr)
    print(f"Sys.path: {sys.path}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"Erro fatal: {e}", file=sys.stderr)
    sys.exit(1)
