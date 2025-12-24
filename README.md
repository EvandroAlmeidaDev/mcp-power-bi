# MCP Power BI

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Power BI](https://img.shields.io/badge/Power%20BI-Desktop-F2C811.svg)](https://powerbi.microsoft.com/)

> 🚀 MCP Server for Power BI Desktop - Generate stunning HTML/CSS visuals and custom Power BI visuals with AI assistance.

## ✨ Features

- **🔌 Power BI Connection**: Auto-detect and connect to running Power BI Desktop instances
- **📊 Schema Reading**: Extract tables, columns, and measures from your data model
- **✍️ Write-Back**: Create/update DAX measures programmatically via TOM
- **🎨 HTML Visuals**: Generate premium KPI cards, progress rings, and comparison charts
- **⚡ Custom Visuals**: Full TypeScript visual with working JavaScript (filters, sorting, dark mode)
- **🖥️ Multi-IDE Support**: Auto-configure for VS Code, Cursor, Claude Desktop, and Windsurf

## 📋 Requirements

- **Windows 10/11** (Power BI Desktop is Windows-only)
- **Python 3.12+**
- **Power BI Desktop** (running with a model loaded)
- **Node.js 18+** (for custom visual development)

### Optional (for Write-Back)

- [SQL Server AMO SDK](https://www.nuget.org/packages/Microsoft.AnalysisServices.retail.amd64) - Required for TOM write operations

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/mcp-power-bi.git
cd mcp-power-bi

# Run the installer
install.bat
```

Or manually:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure IDE

```bash
python setup_mcp.py
```

This auto-configures the MCP server for your installed IDEs.

### 3. Start the Server

```bash
start.bat
```

Or:

```bash
.venv\Scripts\python -m src.server
```

## 🛠️ MCP Tools

| Tool | Description |
|------|-------------|
| `connect_and_scan_schema` | Connect to Power BI and read model schema |
| `list_style_presets` | List available visual themes |
| `generate_html_measure` | Create HTML visual as DAX measure |
| `preview_visual_local` | Save HTML preview locally |
| `apply_conditional_format` | Apply conditional formatting rules |

## 🎨 Available Themes

- **Dark Neon** - Vibrant gradients on dark background
- **Glassmorphism** - Frosted glass effect
- **Corporate Clean** - Professional light theme
- **Executive Dark** - Sophisticated dark theme
- **Data Viz Pro** - Optimized for data visualization

## 📦 Custom Visual

The project includes a fully-functional **Power BI Custom Visual** with:

- ✅ Working JavaScript (not blocked like HTML Content)
- ✅ Interactive filters
- ✅ Sortable tables
- ✅ Dark/Light mode toggle
- ✅ Animated bar charts
- ✅ Auto-generated insights

### Build the Visual

```bash
cd custom-visual/DashboardPIB
npm install
pbiviz package
```

The `.pbiviz` file will be in the `dist/` folder.

## 📁 Project Structure

```
mcp-power-bi/
├── src/
│   ├── server.py           # MCP Server
│   ├── pbi_connector.py    # Power BI connection (ADOMD + TOM)
│   ├── utils.py            # Utilities
│   └── ux_engine/
│       ├── tokens.py       # Theme definitions
│       ├── builder.py      # Visual builder
│       └── components/     # HTML components
├── custom-visual/
│   └── DashboardPIB/       # Power BI Custom Visual source
├── install.bat             # One-click installer
├── setup_mcp.py            # IDE configurator
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

Copy `.env.example` to `.env` and adjust:

```env
# Optional: Custom DLL paths
ADOMD_DLL_PATH=C:\path\to\Microsoft.AnalysisServices.AdomdClient.dll
TOM_DLL_PATH=C:\path\to\Microsoft.AnalysisServices.Tabular.dll

# Log level
LOG_LEVEL=INFO
```

## 📝 Usage Examples

### Generate a KPI Card

```python
from src.ux_engine.builder import UXBuilder

builder = UXBuilder(theme="dark_neon")
result = builder.build_component(
    component_type="kpi_card",
    measure_expression="[Total Sales]",
    title="Revenue",
    animation="pulse"
)
print(result["dax_code"])
```

### Connect to Power BI

```python
from src.pbi_connector import PowerBIConnector

connector = PowerBIConnector()
connector.connect()
schema = connector.get_schema()

for table in schema.tables:
    print(f"Table: {table.name}")
    for col in table.columns:
        print(f"  - {col.name}")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastMCP](https://github.com/jlowin/fastmcp) - MCP framework
- [pythonnet](https://pythonnet.github.io/) - .NET integration
- [Power BI Visuals SDK](https://github.com/microsoft/PowerBI-visuals) - Custom visual development
