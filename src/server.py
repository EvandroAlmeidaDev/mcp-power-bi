"""
Power BI UX MCP Server

Servidor MCP que conecta ao Power BI Desktop e gera visuais HTML/CSS.

Tools disponíveis:
- connect_and_scan_schema: Conecta e retorna schema do modelo
- list_style_presets: Lista temas disponíveis
- generate_html_measure: Gera medida DAX com HTML/CSS
- preview_visual_local: Gera preview HTML local
"""

import json
import logging
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

from .pbi_connector import PowerBIConnector, PowerBIConnectionError
from .ux_engine.builder import UXBuilder
from .ux_engine.tokens import list_themes
from .utils import setup_logging, save_preview_html

# Configura logging
logger = setup_logging("powerbi_mcp")

# Inicializa servidor MCP
mcp = FastMCP(
    name="Power BI UX Server",
    instructions="Conecta ao Power BI Desktop e gera visuais HTML/CSS modernos"
)

# Estado global
_connector: Optional[PowerBIConnector] = None
_builder = UXBuilder()


# ============================================
# TOOL 1: connect_and_scan_schema
# ============================================

@mcp.tool()
def connect_and_scan_schema() -> dict:
    """
    Conecta ao Power BI Desktop e retorna o schema do modelo.
    
    Esta tool detecta automaticamente o Power BI Desktop aberto,
    conecta via ADOMD.NET e retorna informações sobre:
    - Nome do modelo
    - Lista de tabelas
    - Colunas de cada tabela
    - Medidas existentes
    
    Returns:
        dict: Schema do modelo ou erro
        
    Exemplo de retorno:
        {
            "status": "connected",
            "model_name": "Vendas",
            "tables": [
                {"name": "Fato_Vendas", "columns": ["Data", "Valor"], "measures": ["Total Vendas"]}
            ]
        }
    """
    global _connector
    
    try:
        _connector = PowerBIConnector()
        _connector.connect()
        
        schema = _connector.get_schema()
        
        return {
            "status": "connected",
            "port": _connector.port,
            **schema.to_dict()
        }
        
    except PowerBIConnectionError as e:
        logger.error(f"Erro de conexão: {e}")
        return {
            "status": "error",
            "error": str(e),
            "hint": "Certifique-se de que o Power BI Desktop está aberto com um modelo carregado."
        }
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return {
            "status": "error", 
            "error": str(e)
        }


# ============================================
# TOOL 2: list_style_presets
# ============================================

@mcp.tool()
def list_style_presets() -> list[dict]:
    """
    Lista todos os temas/presets de estilo disponíveis.
    
    Cada tema define cores, tipografia e estilos visuais
    que podem ser aplicados aos visuais gerados.
    
    Returns:
        list: Lista de temas disponíveis
        
    Exemplo de retorno:
        [
            {
                "name": "dark_neon",
                "display_name": "Dark Neon", 
                "description": "Fundo escuro com acentos neon vibrantes"
            }
        ]
    """
    return list_themes()


# ============================================
# TOOL 3: generate_html_measure
# ============================================

@mcp.tool()
def generate_html_measure(
    component_type: str,
    measure_name: str,
    variation_measure: str = None,
    target_measure: str = None,
    title: str = None,
    theme: str = "dark_neon",
    format_type: str = "currency",
    # Novos argumentos para Write-Back
    output_measure_name: str = None,
    output_table_name: str = None,
    apply_to_model: bool = True
) -> dict:
    """
    Gera uma medida DAX contendo HTML/CSS estilizado para o Power BI.
    
    O código gerado deve ser colado como uma nova medida no Power BI
    e usado com o visual "HTML Content" do AppSource.
    
    Args:
        component_type: Tipo do componente. Opções:
            - "kpi_card": Card de KPI com valor e variação
            - "progress_ring": Anel de progresso circular
            - "comparison_card": Comparação Atual vs Meta
            - "status_badge": Badge de status colorido
            
        measure_name: Nome da medida principal do modelo (ex: "[Total Vendas]").
            Use exatamente como aparece no Power BI, com colchetes.
            
        variation_measure: (Opcional) Medida de variação percentual para KPI Card.
            Ex: "[Var % MoM]"
            
        target_measure: (Opcional) Medida de meta para comparison_card e progress_ring.
            Ex: "[Meta Vendas]"
            
        title: (Opcional) Título exibido no visual. Se não fornecido, 
            será derivado do nome da medida.
            
        theme: Nome do tema visual. Use list_style_presets() para ver opções.
            Default: "dark_neon"
            
        format_type: Tipo de formatação do valor. Opções:
            - "currency": Moeda (R$ 1.234)
            - "number": Número (#,##0)
            - "percentage": Porcentagem (0.0%)
    
    Returns:
        dict: Contendo o código DAX gerado
        
    Exemplo de uso:
        generate_html_measure(
            component_type="kpi_card",
            measure_name="[Total Vendas]",
            variation_measure="[Var % MoM]",
            theme="glassmorphism"
            theme="glassmorphism",
            apply_to_model=True
        )
    """
    global _builder, _connector
    
    # Nome da medida de saída (HTML)
    if not output_measure_name:
        # Deriva do nome da medida fonte: [Total Vendas] -> Total Vendas HTML
        clean_name = measure_name.strip("[]")
        output_measure_name = f"{clean_name} HTML"
    
    try:
        _builder.set_theme(theme)
        
        if component_type == "kpi_card":
            dax_code = _builder.kpi_card(
                measure_name=measure_name,
                variation_measure=variation_measure,
                title=title,
                format_type=format_type
            )
            
        elif component_type == "progress_ring":
            dax_code = _builder.progress_ring(
                measure_name=measure_name,
                target_measure=target_measure,
                title=title
            )
            
        elif component_type == "comparison_card":
            if not target_measure:
                return {
                    "status": "error",
                    "error": "comparison_card requer target_measure"
                }
            dax_code = _builder.comparison_card(
                actual_measure=measure_name,
                target_measure=target_measure,
                title=title,
                format_type=format_type
            )
            
        elif component_type == "status_badge":
            dax_code = _builder.status_badge(
                measure_name=measure_name,
                title=title
            )
            
        else:
            available = ", ".join(_builder.COMPONENT_TYPES)
            return {
                "status": "error",
                "error": f"Componente '{component_type}' não encontrado. Disponíveis: {available}"
            }
        

        
        # Tenta aplicar ao modelo se solicitado
        write_status = "skipped"
        write_message = "Escrita no modelo ignorada (apply_to_model=False)"
        
        if apply_to_model:
            try:
                if not _connector:
                    _connector = PowerBIConnector()
                
                # Se tabela de saída não foi especificada, tenta descobrir ou usa a primeira
                target_table = output_table_name
                if not target_table:
                    # Tenta conectar para descobrir tabelas
                    if not _connector.connection:
                        _connector.connect()
                    
                    schema = _connector.get_schema()
                    if schema.tables:
                        # Tenta achar a tabela da medida fonte se possível, senão usa a primeira
                        # Por simplicidade, usa a primeira tabela (geralmente Tabela de Medidas)
                        target_table = schema.tables[0].name
                
                if target_table:
                    _connector.add_or_update_measure(
                        table_name=target_table,
                        measure_name=output_measure_name,
                        dax_code=dax_code,
                        description=f"Visual {component_type} gerado por Power BI UX MCP"
                    )
                    write_status = "success"
                    write_message = f"Medida '{output_measure_name}' criada com sucesso na tabela '{target_table}'!"
                else:
                    write_status = "error"
                    write_message = "Nenhuma tabela encontrada para criar a medida."
                    
            except Exception as e:
                write_status = "error"
                write_message = f"Falha na escrita automática: {e}. 'Allow external tools' está ativado?"
                logger.error(write_message)

        return {
            "status": "success",
            "write_status": write_status,
            "write_message": write_message,
            "component_type": component_type,
            "theme": theme,
            "dax_code": dax_code,
            "measure_name_created": output_measure_name if write_status == "success" else None,
            "instructions": [
                f"STATUS DE ESCRITA: {write_message}",
                "---",
                "Se a escrita falhou, copie o código abaixo manualmente:",
                "1. No Power BI, crie uma nova medida", 
                 f"2. Nomeie como: {output_measure_name}",
                "3. Cole o código DAX",
                "4. Use visual 'HTML Content'"
            ]
        }
        
    except ValueError as e:
        return {
            "status": "error",
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Erro ao gerar visual: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ============================================
# TOOL 4: preview_visual_local  
# ============================================

@mcp.tool()
def preview_visual_local(
    component_type: str,
    measure_name: str,
    variation_measure: str = None,
    target_measure: str = None,
    title: str = None,
    theme: str = "dark_neon",
    format_type: str = "currency",
    mock_value: float = 1250000,
    mock_variation: float = 0.125
) -> dict:
    """
    Gera um arquivo HTML de preview para visualização local.
    
    Útil para testar o visual antes de implementar no Power BI.
    O arquivo é salvo na pasta 'previews' do projeto e pode ser
    aberto em qualquer navegador.
    
    Args:
        component_type: Tipo do componente (mesmo de generate_html_measure)
        measure_name: Nome da medida
        variation_measure: Medida de variação (opcional)
        target_measure: Medida de meta (opcional)
        title: Título do visual
        theme: Nome do tema
        format_type: Tipo de formatação
        mock_value: Valor mockado para o preview (default: 1250000)
        mock_variation: Variação mockada (default: 12.5%)
    
    Returns:
        dict: Caminho do arquivo HTML gerado
    """
    global _builder
    
    try:
        # Primeiro gera o DAX
        result = generate_html_measure(
            component_type=component_type,
            measure_name=measure_name,
            variation_measure=variation_measure,
            target_measure=target_measure,
            title=title,
            theme=theme,
            format_type=format_type
        )
        
        if result["status"] != "success":
            return result
        
        dax_code = result["dax_code"]
        
        # Valores mockados para preview
        mock_values = {
            "_Valor": str(int(mock_value)),
            "_Variacao": str(mock_variation),
            "_PercentualDisplay": str(int(mock_value / 10000)),
            "_Atual": str(int(mock_value * 0.85)),
            "_Meta": str(int(mock_value)),
            "_Cor": "#00f5d4" if mock_variation >= 0 else "#ff6b6b",
            "_Seta": "▲" if mock_variation >= 0 else "▼",
        }
        
        # Gera HTML de preview
        _builder.set_theme(theme)
        preview_html = _builder.generate_preview_html(dax_code, mock_values)
        
        # Salva arquivo
        filename = f"preview_{component_type}_{theme}.html"
        filepath = save_preview_html(preview_html, filename)
        
        return {
            "status": "success",
            "preview_file": str(filepath),
            "message": f"Preview salvo em: {filepath}",
            "instructions": [
                f"1. Abra o arquivo no navegador: {filepath}",
                "2. Visualize como o componente ficará",
                "3. Ajuste os parâmetros se necessário"
            ]
        }
        
    except Exception as e:
        logger.error(f"Erro ao gerar preview: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


# ============================================
# TOOL 5: apply_conditional_format (BÔNUS)
# ============================================

@mcp.tool()
def apply_conditional_format(
    measure_name: str,
    rules: list[dict],
    theme: str = "dark_neon"
) -> dict:
    """
    Aplica formatação condicional a uma medida existente.
    
    Gera código DAX que muda a cor/ícone baseado em regras.
    
    Args:
        measure_name: Nome da medida (ex: "[Status]")
        rules: Lista de regras no formato:
            [
                {"value": "Concluído", "color": "success", "icon": "✓"},
                {"value": "Atrasado", "color": "danger", "icon": "✗"}
            ]
            
            Cores disponíveis: success, warning, danger, accent, secondary
            
        theme: Nome do tema para cores
    
    Returns:
        dict: Código DAX com formatação condicional
    """
    global _builder
    
    try:
        _builder.set_theme(theme)
        
        dax_code = _builder.status_badge(
            measure_name=measure_name,
            rules=rules
        )
        
        return {
            "status": "success",
            "dax_code": dax_code,
            "rules_applied": len(rules)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# ============================================
# EXECUÇÃO
# ============================================

def main():
    """Ponto de entrada do servidor."""
    logger.info("Iniciando Power BI UX MCP Server...")
    mcp.run()


if __name__ == "__main__":
    main()
