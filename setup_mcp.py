"""
Auto-Setup para IDEs

Detecta IDEs instaladas (Cursor, VS Code, Claude Desktop, Windsurf, Antigravity, Trae)
e configura automaticamente o servidor MCP.

Uso:
    python setup_mcp.py
"""

import os
import json
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Retorna o diretório raiz do projeto."""
    return Path(__file__).parent


def get_python_path() -> str:
    """Retorna o caminho do Python no ambiente virtual."""
    venv_path = get_project_root() / ".venv" / "Scripts" / "python.exe"
    if venv_path.exists():
        return str(venv_path)
    return sys.executable


# Configuração do servidor MCP
def get_mcp_config() -> dict:
    """Retorna a configuração do servidor MCP."""
    project_root = get_project_root()
    return {
        "command": get_python_path(),
        "args": ["-X", "utf8", "-m", "src.server"],
        "cwd": str(project_root)
    }


# Caminhos conhecidos das IDEs no Windows
IDE_CONFIGS = {
    "cursor": {
        "path": Path.home() / ".cursor" / "mcp.json",
        "key": "mcpServers",
        "format": "mcp_json"
    },
    "vscode": {
        "path": Path.home() / "AppData" / "Roaming" / "Code" / "User" / "settings.json",
        "key": "mcp.servers",
        "format": "settings_json"
    },
    "claude_desktop": {
        "path": Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
        "key": "mcpServers",
        "format": "mcp_json"
    },
    "windsurf": {
        "path": Path.home() / ".windsurf" / "mcp.json",
        "key": "mcpServers",
        "format": "mcp_json"
    },
    "antigravity": {
        "path": Path.home() / ".gemini" / "antigravity" / "mcp_config.json",
        "key": "mcpServers",
        "format": "mcp_json"
    },
    "trae": {
        "path": Path.home() / ".trae" / "mcp.json",
        "key": "mcpServers",
        "format": "mcp_json"
    },
}


def read_json_file(path: Path) -> dict:
    """Lê um arquivo JSON."""
    try:
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except json.JSONDecodeError:
        print(f"   ⚠️  Arquivo corrompido: {path}")
    return {}


def write_json_file(path: Path, data: dict):
    """Escreve um arquivo JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def inject_mcp_config(ide_name: str, ide_info: dict) -> bool:
    """
    Injeta a configuração MCP em uma IDE.
    
    Returns:
        True se configurado com sucesso
    """
    path = ide_info["path"]
    key = ide_info["key"]
    mcp_config = get_mcp_config()
    
    # Lê configuração existente
    config = read_json_file(path)
    
    # Injeta servidor MCP
    if ide_info["format"] == "settings_json":
        # Para VS Code settings.json, a estrutura é diferente
        if key not in config:
            config[key] = {}
        config[key]["powerbi-ux"] = mcp_config
    else:
        # Para mcp.json (Cursor, Claude Desktop, Windsurf)
        if key not in config:
            config[key] = {}
        config[key]["powerbi-ux"] = mcp_config
    
    # Salva
    try:
        write_json_file(path, config)
        return True
    except Exception as e:
        print(f"   ❌ Erro ao salvar: {e}")
        return False


def detect_and_configure():
    """Detecta IDEs e configura automaticamente."""
    print("\n" + "=" * 50)
    print("   Power BI UX MCP - Auto Setup")
    print("=" * 50)
    print()
    print("🔍 Detectando IDEs instaladas...\n")
    
    configured = []
    not_found = []
    
    for ide_name, ide_info in IDE_CONFIGS.items():
        path = ide_info["path"]
        
        # Verifica se a IDE existe (pelo diretório pai)
        if path.parent.exists() or path.exists():
            print(f"✅ {ide_name.upper()} detectado!")
            
            if inject_mcp_config(ide_name, ide_info):
                print(f"   → Configurado em: {path}")
                configured.append(ide_name)
            else:
                print(f"   → Falha ao configurar")
        else:
            not_found.append(ide_name)
            print(f"⚪ {ide_name} não encontrado")
    
    print()
    print("=" * 50)
    
    if configured:
        print(f"✨ Configuração concluída para: {', '.join(configured)}")
        print()
        print("📌 Próximos passos:")
        print("   1. Reinicie sua IDE")
        print("   2. O MCP 'powerbi-ux' estará disponível")
        print("   3. Abra o Power BI Desktop com um modelo")
        print("   4. Use as ferramentas do MCP!")
    else:
        print("⚠️  Nenhuma IDE compatível encontrada.")
        print()
        print("IDEs suportadas:")
        for ide in IDE_CONFIGS.keys():
            print(f"   - {ide}")
    
    print("=" * 50)
    print()
    
    return configured


def create_vscode_local_config():
    """Cria configuração local do MCP para o projeto."""
    vscode_dir = get_project_root() / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    
    mcp_config = {
        "servers": {
            "powerbi-ux": get_mcp_config()
        }
    }
    
    config_path = vscode_dir / "mcp.json"
    write_json_file(config_path, mcp_config)
    print(f"📁 Configuração local criada: {config_path}")


if __name__ == "__main__":
    # Cria configuração local primeiro
    create_vscode_local_config()
    
    # Depois configura IDEs globalmente
    detect_and_configure()
    
    input("\nPressione ENTER para sair...")
