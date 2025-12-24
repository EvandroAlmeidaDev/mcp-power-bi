"""
ComparisonCard Component - Card de comparação Atual vs Meta

Exibe dois valores lado a lado com indicador visual de performance.
"""

from ..tokens import Theme, get_theme


def generate_comparison_card_dax(
    actual_measure: str,
    target_measure: str,
    title: str = None,
    theme_name: str = "dark_neon",
    format_type: str = "currency"
) -> str:
    """
    Gera código DAX para um card de comparação.
    
    Args:
        actual_measure: Medida do valor atual (ex: "[Vendas Realizadas]")
        target_measure: Medida da meta (ex: "[Meta Vendas]")
        title: Título do card
        theme_name: Nome do tema
        format_type: Tipo de formatação
        
    Returns:
        Código DAX completo
    """
    theme = get_theme(theme_name)
    c = theme.colors
    
    if not title:
        title = "REALIZADO VS META"
    
    format_patterns = {
        "currency": '"R$ "#,##0',
        "number": '#,##0',
        "percentage": '0.0%'
    }
    format_pattern = format_patterns.get(format_type, '#,##0')
    dax_format = format_pattern.replace('"', '""')
    
    card_style = f'''background: linear-gradient(135deg, {c.bg_primary} 0%, {c.bg_secondary} 100%); border-radius: {theme.border_radius}; padding: 24px; font-family: {theme.font_family}; box-shadow: {c.shadow}; border: 1px solid {c.border};'''
    
    dax = f'''
{actual_measure.strip("[]")}_vs_Meta_HTML = 
VAR _Atual = {actual_measure}
VAR _Meta = {target_measure}
VAR _Diferenca = _Atual - _Meta
VAR _Percentual = DIVIDE(_Atual, _Meta, 0) - 1
VAR _Status = IF(_Atual >= _Meta, "✓", "✗")
VAR _CorStatus = IF(_Atual >= _Meta, "{c.success}", "{c.danger}")
VAR _BarraWidth = MIN(DIVIDE(_Atual, _Meta, 0) * 100, 100)

RETURN
"<div style='{card_style}'>
    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;'>
        <p style='color: {c.text_secondary}; font-size: 11px; margin: 0; text-transform: uppercase; letter-spacing: 1px;'>{title}</p>
        <span style='color: " & _CorStatus & "; font-size: 20px;'>" & _Status & "</span>
    </div>
    
    <div style='display: flex; justify-content: space-between; margin-bottom: 12px;'>
        <div>
            <p style='color: {c.text_secondary}; font-size: 10px; margin: 0;'>REALIZADO</p>
            <p style='color: {c.text_primary}; font-size: 24px; margin: 4px 0; font-weight: 600;'>" & FORMAT(_Atual, "{dax_format}") & "</p>
        </div>
        <div style='text-align: right;'>
            <p style='color: {c.text_secondary}; font-size: 10px; margin: 0;'>META</p>
            <p style='color: {c.text_secondary}; font-size: 24px; margin: 4px 0; font-weight: 400;'>" & FORMAT(_Meta, "{dax_format}") & "</p>
        </div>
    </div>
    
    <div style='background: {c.bg_secondary}; border-radius: 4px; height: 8px; overflow: hidden;'>
        <div style='background: " & _CorStatus & "; width: " & _BarraWidth & "%; height: 100%; border-radius: 4px; transition: width 0.5s ease;'></div>
    </div>
    
    <p style='color: " & _CorStatus & "; font-size: 12px; margin-top: 8px; text-align: center;'>
        " & IF(_Diferenca >= 0, "+", "") & FORMAT(_Diferenca, "{dax_format}") & " (" & FORMAT(_Percentual, "+0.0%;-0.0%") & ")
    </p>
</div>"
'''
    
    return dax.strip()
