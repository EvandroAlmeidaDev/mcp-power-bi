"""
UX Builder - Monta HTML/DAX a partir de componentes

Orquestra a geração de visuais combinando:
- Design tokens
- Componentes
- Data binding
"""

from typing import Optional
from .tokens import get_theme, list_themes, Theme
from .components.kpi_card import generate_kpi_card_dax
from .components.progress_ring import generate_progress_ring_dax
from .components.comparison_card import generate_comparison_card_dax
from .components.status_badge import generate_status_badge_dax, create_status_rules


class UXBuilder:
    """
    Builder para construção de visuais HTML/DAX.
    
    Uso:
        builder = UXBuilder(theme="dark_neon")
        dax_code = builder.kpi_card("[Total Vendas]", "[Var % MoM]")
    """
    
    COMPONENT_TYPES = [
        "kpi_card",
        "progress_ring", 
        "comparison_card",
        "status_badge"
    ]
    
    def __init__(self, theme_name: str = "dark_neon"):
        """
        Inicializa o builder.
        
        Args:
            theme_name: Nome do tema padrão
        """
        self.theme_name = theme_name
        self.theme = get_theme(theme_name)
    
    def set_theme(self, theme_name: str):
        """Altera o tema atual."""
        self.theme_name = theme_name
        self.theme = get_theme(theme_name)
    
    def list_available_themes(self) -> list[dict]:
        """Lista temas disponíveis."""
        return list_themes()
    
    def list_available_components(self) -> list[str]:
        """Lista componentes disponíveis."""
        return self.COMPONENT_TYPES.copy()
    
    def kpi_card(
        self,
        measure_name: str,
        variation_measure: Optional[str] = None,
        title: Optional[str] = None,
        format_type: str = "currency"
    ) -> str:
        """
        Gera um KPI Card.
        
        Args:
            measure_name: Medida principal (ex: "[Total Vendas]")
            variation_measure: Medida de variação (opcional)
            title: Título do card
            format_type: currency | number | percentage
            
        Returns:
            Código DAX completo
        """
        return generate_kpi_card_dax(
            measure_name=measure_name,
            variation_measure=variation_measure,
            title=title,
            theme_name=self.theme_name,
            format_type=format_type
        )
    
    def progress_ring(
        self,
        measure_name: str,
        target_measure: Optional[str] = None,
        title: Optional[str] = None,
        size: int = 120
    ) -> str:
        """
        Gera um anel de progresso.
        
        Args:
            measure_name: Medida atual
            target_measure: Medida meta (se None, assume 0-100%)
            title: Título
            size: Tamanho em pixels
            
        Returns:
            Código DAX completo
        """
        return generate_progress_ring_dax(
            measure_name=measure_name,
            target_measure=target_measure,
            title=title,
            theme_name=self.theme_name,
            size=size
        )
    
    def comparison_card(
        self,
        actual_measure: str,
        target_measure: str,
        title: Optional[str] = None,
        format_type: str = "currency"
    ) -> str:
        """
        Gera um card de comparação (Atual vs Meta).
        
        Args:
            actual_measure: Medida do valor atual
            target_measure: Medida da meta
            title: Título
            format_type: Tipo de formatação
            
        Returns:
            Código DAX completo
        """
        return generate_comparison_card_dax(
            actual_measure=actual_measure,
            target_measure=target_measure,
            title=title,
            theme_name=self.theme_name,
            format_type=format_type
        )
    
    def status_badge(
        self,
        measure_name: str,
        rules: Optional[list[dict]] = None,
        title: Optional[str] = None
    ) -> str:
        """
        Gera um badge de status.
        
        Args:
            measure_name: Medida que determina o status
            rules: Lista de regras (usa padrão se None)
            title: Título
            
        Returns:
            Código DAX completo
        """
        if rules is None:
            rules = create_status_rules()
            
        return generate_status_badge_dax(
            measure_name=measure_name,
            rules=rules,
            title=title,
            theme_name=self.theme_name
        )
    
    def generate_preview_html(
        self,
        dax_code: str,
        mock_values: dict = None
    ) -> str:
        """
        Gera HTML de preview substituindo variáveis DAX por valores mockados.
        
        Args:
            dax_code: Código DAX gerado
            mock_values: Dicionário de valores para preview
            
        Returns:
            HTML completo para visualização
        """
        if mock_values is None:
            mock_values = {
                "_Valor": "1250000",
                "_Variacao": "0.125",
                "_PercentualDisplay": "87",
                "_Atual": "850000",
                "_Meta": "1000000",
            }
        
        # Extrai o HTML do RETURN
        import re
        match = re.search(r'RETURN\s*"(.+)"', dax_code, re.DOTALL)
        if not match:
            return "<p>Erro: não foi possível extrair HTML do DAX</p>"
        
        html_content = match.group(1)
        
        # Substitui concatenações DAX por valores mockados
        # Padrão: " & FORMAT(_Valor, "...") & "
        html_content = re.sub(
            r'" & FORMAT\(([^,]+), "[^"]+"\) & "',
            lambda m: mock_values.get(m.group(1).strip(), "0"),
            html_content
        )
        
        # Padrão: " & _Variavel & "
        html_content = re.sub(
            r'" & ([^&]+) & "',
            lambda m: mock_values.get(m.group(1).strip(), ""),
            html_content
        )
        
        # Monta HTML completo
        preview_html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Power BI Visual Preview</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 40px;
        }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
"""
        return preview_html


# Instância global para uso rápido
default_builder = UXBuilder()
