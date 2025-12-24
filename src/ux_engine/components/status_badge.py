"""
StatusBadge Component - Badges de status coloridos

Exibe indicadores de status como tags coloridas.
"""

from ..tokens import Theme, get_theme


def generate_status_badge_dax(
    measure_name: str,
    rules: list[dict],
    title: str = None,
    theme_name: str = "dark_neon"
) -> str:
    """
    Gera código DAX para badges de status.
    
    Args:
        measure_name: Medida a avaliar (ex: "[Status Projeto]")
        rules: Lista de regras [{value: "Ativo", color: "success", icon: "🟢"}]
        title: Título do badge
        theme_name: Nome do tema
        
    Returns:
        Código DAX completo
    """
    theme = get_theme(theme_name)
    c = theme.colors
    
    if not title:
        title = measure_name.strip("[]").upper()
    
    # Mapeia cores do tema
    color_map = {
        "success": c.success,
        "warning": c.warning,
        "danger": c.danger,
        "accent": c.accent,
        "secondary": c.text_secondary
    }
    
    # Monta SWITCH para cores
    switch_cases = []
    for rule in rules:
        value = rule.get("value", "")
        color = color_map.get(rule.get("color", "accent"), c.accent)
        icon = rule.get("icon", "●")
        switch_cases.append(f'_Valor = "{value}", "{icon} " & _Valor & "|{color}"')
    
    switch_expr = ",\n        ".join(switch_cases)
    
    dax = f'''
{measure_name.strip("[]")}_Badge = 
VAR _Valor = {measure_name}
VAR _Config = 
    SWITCH(
        TRUE(),
        {switch_expr},
        "● " & _Valor & "|{c.text_secondary}"
    )
VAR _Texto = LEFT(_Config, FIND("|", _Config) - 1)
VAR _Cor = MID(_Config, FIND("|", _Config) + 1, 100)

RETURN
"<span style='
    display: inline-block;
    background: " & _Cor & "22;
    color: " & _Cor & ";
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    font-family: {theme.font_family};
    border: 1px solid " & _Cor & "44;
'>" & _Texto & "</span>"
'''
    
    return dax.strip()


# Função helper para criar regras padrão
def create_status_rules():
    """Retorna regras de status padrão."""
    return [
        {"value": "Concluído", "color": "success", "icon": "✓"},
        {"value": "Em Andamento", "color": "warning", "icon": "◐"},
        {"value": "Atrasado", "color": "danger", "icon": "✗"},
        {"value": "Não Iniciado", "color": "secondary", "icon": "○"},
    ]
