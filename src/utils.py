"""
Utilitários gerais do projeto.

Inclui:
- Configuração de logging
- Helpers para arquivos
- Formatação de dados
"""

import os
import logging
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


def setup_logging(name: str = "powerbi_mcp") -> logging.Logger:
    """
    Configura e retorna um logger.
    
    Args:
        name: Nome do logger
        
    Returns:
        Logger configurado
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def get_project_root() -> Path:
    """Retorna o diretório raiz do projeto."""
    return Path(__file__).parent.parent


def save_preview_html(html_content: str, filename: str = None) -> Path:
    """
    Salva conteúdo HTML como arquivo de preview.
    
    Args:
        html_content: Conteúdo HTML a salvar
        filename: Nome do arquivo (opcional)
        
    Returns:
        Path do arquivo salvo
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"preview_{timestamp}.html"
    
    preview_dir = get_project_root() / "previews"
    preview_dir.mkdir(exist_ok=True)
    
    filepath = preview_dir / filename
    filepath.write_text(html_content, encoding="utf-8")
    
    return filepath


def format_currency(value: float, currency: str = "BRL") -> str:
    """
    Formata valor como moeda.
    
    Args:
        value: Valor numérico
        currency: Código da moeda (BRL, USD, EUR)
        
    Returns:
        String formatada
    """
    symbols = {
        "BRL": "R$",
        "USD": "$",
        "EUR": "€"
    }
    symbol = symbols.get(currency, "$")
    
    if abs(value) >= 1_000_000:
        return f"{symbol} {value/1_000_000:,.1f}M"
    elif abs(value) >= 1_000:
        return f"{symbol} {value/1_000:,.1f}K"
    else:
        return f"{symbol} {value:,.2f}"


def format_percentage(value: float) -> str:
    """Formata valor como porcentagem."""
    return f"{value:+.1%}" if value != 0 else "0%"


def escape_dax_string(text: str) -> str:
    """
    Escapa caracteres especiais para uso em strings DAX.
    
    Args:
        text: Texto a escapar
        
    Returns:
        Texto escapado
    """
    # Em DAX, aspas duplas são escapadas dobrando-as
    return text.replace('"', '""')
