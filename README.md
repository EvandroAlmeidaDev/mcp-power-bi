# Servidor MCP para Power BI

Este projeto implementa um servidor baseado no protocolo MCP (Model Context Protocol) projetado para integrar assistentes de IA diretamente ao Power BI Desktop. Ele permite a descoberta automatizada de esquemas, geração de medidas DAX e a criação de visuais avançados baseados em HTML/CSS dentro do ambiente do Power BI.

A solução é voltada para desenvolvedores e analistas de dados que desejam utilizar agentes de IA (como Claude, Cursor ou Antigravity) para auxiliar na construção e estilização de painéis com componentes de alta fidelidade que superam as limitações dos visuais padrão do Power BI.

## Funcionalidades Principais

O servidor disponibiliza um conjunto de ferramentas que permitem a um agente de IA:

*   **Descoberta de Metadados do Modelo**: Detectar automaticamente instâncias ativas do Power BI Desktop e extrair estruturas de tabelas, nomes de colunas e medidas existentes.
*   **Gerenciamento Programático de DAX**: Criar e atualizar medidas diretamente no modelo utilizando o Tabular Object Model (TOM).
*   **Geração de Visuais**: Produzir código complexo em HTML/CSS para cartões de KPI, anéis de progresso e gráficos de comparação, encapsulados em medidas DAX para uso com o visual "HTML Content".
*   **Tematização e Estilização**: Aplicar sistemas de design consistentes e regras de formatação condicional baseadas em temas profissionais predefinidos.
*   **Extensão de Visual Personalizado**: Inclui um visual dedicado desenvolvido em TypeScript, oferecendo recursos como filtragem interativa, ordenação e desempenho superior aos containers HTML padrão.

## Pré-requisitos

Para utilizar este servidor, seu ambiente deve atender aos seguintes requisitos:

*   **Sistema Operacional**: Windows 10 ou 11 (necessário para compatibilidade com o Power BI Desktop).
*   **Python**: Versão 3.12 ou superior.
*   **Power BI Desktop**: Deve estar em execução com um modelo de dados carregado para que as ferramentas de conexão funcionem.
*   **Node.js**: Versão 18 ou superior (necessário apenas se pretender compilar ou modificar o visual personalizado).
*   **Bibliotecas de Cliente Analysis Services**: O SDK SQL Server AMO é recomendado para operações avançadas de escrita via TOM.

## Instalação e Configuração

### 1. Configuração do Repositório

Clone o repositório e navegue até o diretório do projeto:

```bash
git clone https://github.com/seuusuario/mcp-power-bi.git
cd mcp-power-bi
```

### 2. Configuração do Ambiente

Você pode utilizar o instalador automatizado fornecido ou configurar o ambiente manualmente:

**Abordagem automatizada:**
Execute o arquivo `install.bat`. Este script criará um ambiente virtual e instalará todas as dependências Python necessárias.

**Abordagem manual:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Integração com IDEs

Para disponibilizar este servidor ao seu assistente de IA, execute o utilitário de configuração:

```bash
python setup_mcp.py
```

Este script detecta as IDEs suportadas (VS Code, Cursor, Claude Desktop, Windsurf, Antigravity e Trae) e adiciona a configuração necessária aos respectivos arquivos de definição.

## Operação do Servidor

O servidor pode ser iniciado através do script `start.bat` ou executando o módulo diretamente:

```bash
.venv\Scripts\python -m src.server
```

Após a inicialização, as seguintes ferramentas tornam-se disponíveis para o cliente MCP conectado:

| Ferramenta | Descrição |
| :--- | :--- |
| `connect_and_scan_schema` | Estabelece conexão com o Power BI e retorna a estrutura do modelo. |
| `list_style_presets` | Retorna os temas visuais e tokens de design disponíveis. |
| `generate_html_measure` | Gera o código DAX para um componente visual baseado em HTML. |
| `preview_visual_local` | Cria um arquivo HTML temporário para visualização em um navegador. |
| `apply_conditional_format` | Gera regras DAX para formatação dinâmica de cores e ícones. |

## Visual Personalizado do Power BI

Além do servidor MCP, este repositório contém um visual personalizado pronto para produção, localizado em `custom-visual/DashboardPIB`. Este visual oferece uma alternativa mais robusta aos visualizadores HTML padrão, suportando:

*   Filtragem e ordenação interativa de dados.
*   Temas dinâmicos com suporte a modo claro e escuro.
*   Animações nativas e gráficos de barras integrados.

### Compilando o Visual

Para empacotar o visual para uso no Power BI:

```bash
cd custom-visual/DashboardPIB
npm install
pbiviz package
```

O arquivo `.pbiviz` resultante será gerado no diretório `dist`.

## Estrutura do Projeto

*   `src/`: Código-fonte principal em Python.
    *   `server.py`: Implementação do servidor MCP e definição de ferramentas.
    *   `pbi_connector.py`: Integração com ADOMD.NET e Tabular Object Model.
    *   `ux_engine/`: Lógica para geração de componentes HTML e temas.
*   `custom-visual/`: Código-fonte do visual TypeScript para Power BI.
*   `install.bat` / `start.bat`: Utilitários para gerenciamento do ambiente.
*   `setup_mcp.py`: Ferramenta de configuração para integração com IDEs.

## Detalhes de Configuração

Configurações avançadas podem ser gerenciadas via arquivo `.env`. Consulte `.env.example` para opções disponíveis, como caminhos explícitos para DLLs do Analysis Services caso não estejam no cache global de assembléias.

## Licença

Este projeto é distribuído sob a Licença MIT. Informações detalhadas podem ser encontradas no arquivo [LICENSE](LICENSE).

## Agradecimentos

Este projeto utiliza o [FastMCP](https://github.com/jlowin/fastmcp) para a estrutura MCP, [pythonnet](https://pythonnet.github.io/) para interoperabilidade com .NET e o [SDK de Visuais do Power BI](https://github.com/microsoft/PowerBI-visuals) para o desenvolvimento de componentes personalizados.
