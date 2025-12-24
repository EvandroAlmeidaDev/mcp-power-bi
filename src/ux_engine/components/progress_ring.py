"""
ProgressRing Component - Anel de progresso circular

Gera SVG/CSS para indicadores de progresso com:
- Valor percentual
- Cor condicional
- Animação de preenchimento
"""

from ..tokens import Theme, get_theme


def generate_progress_ring_dax(
    measure_name: str,
    target_measure: str = None,
    title: str = None,
    theme_name: str = "dark_neon",
    size: int = 120
) -> str:
    """
    Gera código DAX para um anel de progresso.
    
    Args:
        measure_name: Medida atual (ex: "[Realizado]")
        target_measure: Medida meta (ex: "[Meta]") - se None, assume 100%
        title: Título do componente
        theme_name: Nome do tema
        size: Tamanho do anel em pixels
        
    Returns:
        Código DAX completo
    """
    theme = get_theme(theme_name)
    c = theme.colors
    
    if not title:
        title = measure_name.strip("[]").upper()
    
    # Cálculos do SVG
    stroke_width = 8
    radius = (size - stroke_width) / 2
    circumference = 2 * 3.14159 * radius
    
    dax = f'''
{measure_name}_ProgressRing = 
VAR _Valor = {measure_name}
'''
    
    if target_measure:
        dax += f'''VAR _Meta = {target_measure}
VAR _Percentual = DIVIDE(_Valor, _Meta, 0)
'''
    else:
        dax += '''VAR _Percentual = _Valor
'''
    
    dax += f'''VAR _PercentualDisplay = _Percentual * 100
VAR _Circumference = {circumference:.2f}
VAR _Offset = _Circumference * (1 - MIN(_Percentual, 1))
VAR _Cor = 
    SWITCH(
        TRUE(),
        _Percentual >= 1, "{c.success}",
        _Percentual >= 0.7, "{c.warning}",
        "{c.danger}"
    )

RETURN
"<div style='text-align: center; font-family: {theme.font_family};'>
    <svg width='{size}' height='{size}' viewBox='0 0 {size} {size}'>
        <circle 
            cx='{size/2}' cy='{size/2}' r='{radius:.1f}'
            fill='none' 
            stroke='{c.bg_secondary}' 
            stroke-width='{stroke_width}'
        />
        <circle 
            cx='{size/2}' cy='{size/2}' r='{radius:.1f}'
            fill='none' 
            stroke='" & _Cor & "' 
            stroke-width='{stroke_width}'
            stroke-linecap='round'
            stroke-dasharray='{circumference:.2f}'
            stroke-dashoffset='" & _Offset & "'
            transform='rotate(-90 {size/2} {size/2})'
            style='transition: stroke-dashoffset 0.5s ease;'
        />
        <text x='50%' y='50%' text-anchor='middle' dy='0.3em' 
              style='font-size: 24px; font-weight: 600; fill: {c.text_primary};'>
            " & FORMAT(_PercentualDisplay, "0") & "%
        </text>
    </svg>
    <p style='color: {c.text_secondary}; font-size: 12px; margin-top: 8px;'>{title}</p>
</div>"
'''
    
    return dax.strip()
