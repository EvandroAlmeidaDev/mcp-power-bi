"""
KPICard Component - Card para exibição de KPIs

Gera HTML/CSS para cards de métricas com:
- Valor principal
- Variação percentual
- Ícone de tendência
- Formatação condicional
"""

from typing import Optional
from ..tokens import Theme, get_theme


def generate_kpi_card(
    theme: Theme,
    title: str = "METRIC",
    show_variation: bool = True,
    show_icon: bool = True
) -> str:
    """
    Gera o template HTML para um KPI Card.
    
    Args:
        theme: Tema a aplicar
        title: Título do card
        show_variation: Mostrar variação percentual
        show_icon: Mostrar ícone de tendência
        
    Returns:
        Template HTML com placeholders para DAX
    """
    c = theme.colors
    
    # CSS do card
    card_style = f"""
        background: linear-gradient(135deg, {c.bg_primary} 0%, {c.bg_secondary} 100%);
        border-radius: {theme.border_radius};
        padding: 24px;
        font-family: {theme.font_family};
        box-shadow: {c.shadow};
        border: 1px solid {c.border};
        min-width: 200px;
    """
    
    if theme.backdrop_filter:
        card_style += f"backdrop-filter: {theme.backdrop_filter};"
    
    # Animação de entrada
    animation_css = """
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    """
    
    # Template HTML
    html = f"""
<style>
    {animation_css}
    .kpi-card {{
        animation: fadeInUp 0.3s ease-out;
    }}
</style>
<div class='kpi-card' style='{card_style}'>
    <p style='color: {c.text_secondary}; font-size: 11px; margin: 0; text-transform: uppercase; letter-spacing: 1px;'>
        {{TITLE}}
    </p>
    <h1 style='color: {c.text_primary}; font-size: 32px; margin: 8px 0; font-weight: 600;'>
        {{VALUE}}
    </h1>
"""
    
    if show_variation:
        html += f"""
    <span style='font-size: 14px; display: inline-flex; align-items: center; gap: 4px;'>
        <span style='color: {{VARIATION_COLOR}};'>{{VARIATION_ICON}} {{VARIATION_VALUE}}</span>
    </span>
"""
    
    html += "</div>"
    
    return html


def generate_kpi_card_dax(
    measure_name: str,
    variation_measure: Optional[str] = None,
    title: str = None,
    theme_name: str = "dark_neon",
    format_type: str = "currency"
) -> str:
    """
    Gera código DAX completo para um KPI Card.
    
    Args:
        measure_name: Nome da medida principal (ex: "[Total Vendas]")
        variation_measure: Nome da medida de variação (ex: "[Var % MoM]")
        title: Título do card (default: nome da medida)
        theme_name: Nome do tema a usar
        format_type: Tipo de formatação (currency, number, percentage)
        
    Returns:
        Código DAX completo
    """
    theme = get_theme(theme_name)
    c = theme.colors
    
    # Título padrão
    if not title:
        title = measure_name.strip("[]").upper()
    
    # Formatação do valor
    format_patterns = {
        "currency": '"R$ "#,##0',
        "number": '#,##0',
        "percentage": '0.0%'
    }
    format_pattern = format_patterns.get(format_type, '#,##0')
    
    # Escapa aspas para o DAX (IMPORTANTE: " vira "")
    dax_format = format_pattern.replace('"', '""')
    
    # Monta o DAX
    dax = f'''
{measure_name}_HTML = 
VAR _Valor = {measure_name}
'''
    
    if variation_measure:
        dax += f'''VAR _Variacao = {variation_measure}
VAR _Cor = IF(_Variacao >= 0, "{c.success}", "{c.danger}")
VAR _Seta = IF(_Variacao >= 0, "▲", "▼")
'''
    
    # CSS inline
    card_style = f'''background: linear-gradient(135deg, {c.bg_primary} 0%, {c.bg_secondary} 100%); border-radius: {theme.border_radius}; padding: 24px; font-family: {theme.font_family}; box-shadow: {c.shadow}; border: 1px solid {c.border};'''
    
    if theme.backdrop_filter:
        card_style += f" backdrop-filter: {theme.backdrop_filter};"
    
    dax += f'''
RETURN
"<div style='{card_style}'>
    <p style='color: {c.text_secondary}; font-size: 11px; margin: 0; text-transform: uppercase; letter-spacing: 1px;'>{title}</p>
    <h1 style='color: {c.text_primary}; font-size: 32px; margin: 8px 0; font-weight: 600;'>" & FORMAT(_Valor, "{dax_format}") & "</h1>
'''
    
    if variation_measure:
        dax += f'''    <span style='color: " & _Cor & "; font-size: 14px;'>" & _Seta & " " & FORMAT(_Variacao, "0.0%") & "</span>
'''
    
    dax += '"</div>"'
    
    return dax.strip()
