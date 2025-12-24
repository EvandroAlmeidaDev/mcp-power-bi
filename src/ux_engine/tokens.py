"""
Design Tokens - Sistema de design para visuais Power BI

Define cores, tipografia, sombras e outros tokens
que são usados para gerar CSS consistente.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ThemeColors:
    """Cores de um tema."""
    bg_primary: str
    bg_secondary: str
    accent: str
    accent_secondary: str
    text_primary: str
    text_secondary: str
    success: str
    warning: str
    danger: str
    border: str
    shadow: str


@dataclass
class Theme:
    """Tema completo para visuais."""
    name: str
    display_name: str
    description: str
    colors: ThemeColors
    font_family: str = "'Inter', 'Segoe UI', sans-serif"
    border_radius: str = "12px"
    backdrop_filter: Optional[str] = None


# ============================================
# TEMAS DISPONÍVEIS
# ============================================

THEMES: dict[str, Theme] = {
    "dark_neon": Theme(
        name="dark_neon",
        display_name="Dark Neon",
        description="Fundo escuro com acentos neon vibrantes e efeito glow",
        colors=ThemeColors(
            bg_primary="#0d0d0d",
            bg_secondary="#1a1a2e",
            accent="#00f5d4",
            accent_secondary="#7b2cbf",
            text_primary="#ffffff",
            text_secondary="#a0a0a0",
            success="#00f5d4",
            warning="#ffd60a",
            danger="#ff6b6b",
            border="rgba(0, 245, 212, 0.3)",
            shadow="0 0 20px rgba(0, 245, 212, 0.3)"
        ),
        border_radius="16px"
    ),
    
    "glassmorphism": Theme(
        name="glassmorphism",
        display_name="Glassmorphism",
        description="Efeito de vidro translúcido com blur",
        colors=ThemeColors(
            bg_primary="rgba(255, 255, 255, 0.1)",
            bg_secondary="rgba(255, 255, 255, 0.05)",
            accent="#667eea",
            accent_secondary="#764ba2",
            text_primary="#ffffff",
            text_secondary="rgba(255, 255, 255, 0.7)",
            success="#4ade80",
            warning="#fbbf24",
            danger="#f87171",
            border="rgba(255, 255, 255, 0.2)",
            shadow="0 8px 32px rgba(0, 0, 0, 0.3)"
        ),
        backdrop_filter="blur(10px)",
        border_radius="20px"
    ),
    
    "corporate_clean": Theme(
        name="corporate_clean",
        display_name="Corporate Clean",
        description="Estilo corporativo limpo e profissional",
        colors=ThemeColors(
            bg_primary="#ffffff",
            bg_secondary="#f8fafc",
            accent="#2563eb",
            accent_secondary="#3b82f6",
            text_primary="#1e293b",
            text_secondary="#64748b",
            success="#22c55e",
            warning="#eab308",
            danger="#ef4444",
            border="#e2e8f0",
            shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1)"
        ),
        font_family="'Segoe UI', 'Roboto', sans-serif",
        border_radius="8px"
    ),
    
    "executive_dark": Theme(
        name="executive_dark",
        display_name="Executive Dark",
        description="Elegante e minimalista com tons escuros",
        colors=ThemeColors(
            bg_primary="#0f172a",
            bg_secondary="#1e293b",
            accent="#38bdf8",
            accent_secondary="#0ea5e9",
            text_primary="#f1f5f9",
            text_secondary="#94a3b8",
            success="#34d399",
            warning="#fbbf24",
            danger="#f87171",
            border="rgba(148, 163, 184, 0.2)",
            shadow="0 10px 40px rgba(0, 0, 0, 0.5)"
        ),
        border_radius="12px"
    ),
    
    "data_viz_pro": Theme(
        name="data_viz_pro",
        display_name="Data Viz Pro",
        description="Otimizado para dashboards com alta densidade de dados",
        colors=ThemeColors(
            bg_primary="#1a1b26",
            bg_secondary="#24283b",
            accent="#7aa2f7",
            accent_secondary="#bb9af7",
            text_primary="#c0caf5",
            text_secondary="#565f89",
            success="#9ece6a",
            warning="#e0af68",
            danger="#f7768e",
            border="rgba(122, 162, 247, 0.2)",
            shadow="0 4px 12px rgba(0, 0, 0, 0.4)"
        ),
        font_family="'JetBrains Mono', 'Consolas', monospace",
        border_radius="8px"
    ),
}


def get_theme(name: str) -> Theme:
    """
    Retorna um tema pelo nome.
    
    Args:
        name: Nome do tema
        
    Returns:
        Theme object
        
    Raises:
        ValueError: Se tema não existir
    """
    if name not in THEMES:
        available = ", ".join(THEMES.keys())
        raise ValueError(f"Tema '{name}' não encontrado. Disponíveis: {available}")
    return THEMES[name]


def list_themes() -> list[dict]:
    """
    Lista todos os temas disponíveis.
    
    Returns:
        Lista de dicionários com info dos temas
    """
    return [
        {
            "name": theme.name,
            "display_name": theme.display_name,
            "description": theme.description
        }
        for theme in THEMES.values()
    ]
