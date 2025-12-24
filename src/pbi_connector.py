"""
Power BI Desktop Connector via ADOMD.NET

Este módulo conecta ao Power BI Desktop localmente:
1. Detecta a porta do processo msmdsrv.exe
2. Carrega a DLL ADOMD.NET via pythonnet
3. Executa queries DAX para ler schema e dados
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

import psutil
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class TableInfo:
    """Informações de uma tabela do modelo."""
    name: str
    columns: list[str] = field(default_factory=list)
    measures: list[str] = field(default_factory=list)


@dataclass
class ModelSchema:
    """Schema completo do modelo Power BI."""
    model_name: str
    tables: list[TableInfo] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Converte para dicionário JSON-serializável."""
        return {
            "model_name": self.model_name,
            "tables": [
                {
                    "name": t.name,
                    "columns": t.columns,
                    "measures": t.measures
                }
                for t in self.tables
            ]
        }


class PowerBIConnectionError(Exception):
    """Erro de conexão com Power BI Desktop."""
    pass


class PowerBIConnector:
    """
    Conector para Power BI Desktop via ADOMD.NET.
    
    Uso:
        connector = PowerBIConnector()
        connector.connect()
        schema = connector.get_schema()
    """
    
    # Possíveis locais da DLL ADOMD.NET
    ADOMD_DLL_PATHS = [
        r"C:\Program Files\Microsoft.NET\ADOMD.NET\160\Microsoft.AnalysisServices.AdomdClient.dll",
        r"C:\Program Files\Microsoft.NET\ADOMD.NET\150\Microsoft.AnalysisServices.AdomdClient.dll",
        r"C:\Program Files (x86)\Microsoft.NET\ADOMD.NET\160\Microsoft.AnalysisServices.AdomdClient.dll",
        r"C:\Program Files (x86)\Microsoft.NET\ADOMD.NET\150\Microsoft.AnalysisServices.AdomdClient.dll",
    ]

    # DLLs do Tabular Object Model (TOM)
    TOM_DLL_NAME = "Microsoft.AnalysisServices.Tabular.dll"
    CORE_DLL_NAME = "Microsoft.AnalysisServices.Core.dll"
    
    TOM_DLL_PATHS = [
        r"C:\Program Files\Microsoft SQL Server\160\SDK\Assemblies\Microsoft.AnalysisServices.Tabular.dll",
        r"C:\Program Files\Microsoft SQL Server\150\SDK\Assemblies\Microsoft.AnalysisServices.Tabular.dll",
        r"C:\Program Files\Microsoft SQL Server\140\SDK\Assemblies\Microsoft.AnalysisServices.Tabular.dll",
        r"C:\Program Files (x86)\Microsoft SQL Server\160\SDK\Assemblies\Microsoft.AnalysisServices.Tabular.dll", 
        r"C:\Program Files (x86)\Microsoft SQL Server\150\SDK\Assemblies\Microsoft.AnalysisServices.Tabular.dll",
    ]
    
    def __init__(self, port: Optional[int] = None, dll_path: Optional[str] = None):
        """
        Inicializa o conector.
        
        Args:
            port: Porta do Power BI (None = detectar automaticamente)
            dll_path: Caminho para a DLL ADOMD.NET (None = buscar automaticamente)
        """
        self.port = port or self._get_port_from_env()
        self.dll_path = dll_path or self._find_adomd_dll()
        self.dll_path = dll_path or self._find_adomd_dll()
        self.connection = None
        self.tom_server = None
        self._adomd_loaded = False
        self._tom_loaded = False
        
    def _get_port_from_env(self) -> Optional[int]:
        """Obtém porta do .env se definida."""
        port_str = os.getenv("PBI_PORT")
        if port_str:
            try:
                return int(port_str)
            except ValueError:
                logger.warning(f"Porta inválida no .env: {port_str}")
        return None
    
    def _find_adomd_dll(self) -> Optional[str]:
        """Procura a DLL ADOMD.NET no sistema."""
        # Primeiro verifica no .env
        env_path = os.getenv("ADOMD_DLL_PATH")
        if env_path and Path(env_path).exists():
            logger.info(f"DLL encontrada via .env: {env_path}")
            return env_path
        
        # Busca nos caminhos conhecidos
        for path in self.ADOMD_DLL_PATHS:
            if Path(path).exists():
                logger.info(f"DLL encontrada: {path}")
                return path
        
        logger.warning("DLL ADOMD.NET não encontrada. Defina ADOMD_DLL_PATH no .env")
        return None
    
    def find_powerbi_port(self) -> tuple[int, Optional[str]]:
        """
        Detecta a porta e o caminho do executável do Power BI Desktop.
        
        Returns:
            Tupla (porta, caminho_do_executavel)
            
        Raises:
            PowerBIConnectionError: Se Power BI não estiver aberto
        """
        logger.info("Procurando processo do Power BI Desktop...")
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['name'] and 'msmdsrv.exe' in proc.info['name'].lower():
                    # Encontrou o processo
                    exe_path = proc.info.get('exe')
                    port = 0
                    
                    # Tenta achar a porta nas conexões
                    connections = proc.net_connections()
                    for conn in connections:
                        if conn.status == 'LISTEN' and conn.laddr:
                            # Geralmente porta alta (> 1024) e localhost
                            if conn.laddr.ip == '127.0.0.1':
                                port = conn.laddr.port
                                logger.info(f"Power BI encontrado na porta {port} (PID: {proc.info['pid']})")
                                return port, exe_path
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        raise PowerBIConnectionError(
            "Power BI Desktop não encontrado. "
            "Certifique-se de que o Power BI está aberto com um modelo carregado."
        )

    def _find_adomd_dll(self, search_path: Optional[str] = None) -> Optional[str]:
        """Procura a DLL ADOMD.NET no sistema."""
        # 1. Verifica no .env
        env_path = os.getenv("ADOMD_DLL_PATH")
        if env_path and Path(env_path).exists():
            logger.info(f"DLL encontrada via .env: {env_path}")
            return env_path
        
        # 2. Busca nos caminhos padrão
        for path in self.ADOMD_DLL_PATHS:
            if Path(path).exists():
                logger.info(f"DLL encontrada: {path}")
                return path
                
        # 3. Se temos o caminho do Power BI, busca lá
        if search_path:
            logger.info(f"Buscando DLL perto de: {search_path}")
            bin_dir = Path(search_path).parent
            # Tenta recursivo na pasta bin
            try:
                # Busca rápida níveis rasos
                found = list(bin_dir.rglob("Microsoft.AnalysisServices.AdomdClient.dll"))
                if found:
                    dll = str(found[0])
                    logger.info(f"DLL encontrada na pasta do PBI: {dll}")
                    return dll
            except Exception as e:
                logger.warning(f"Erro ao buscar na pasta bin: {e}")

        logger.warning("DLL ADOMD.NET não encontrada. Defina ADOMD_DLL_PATH no .env")
        return None
    
    def _load_adomd(self):
        """Carrega a biblioteca ADOMD.NET via pythonnet."""
        if self._adomd_loaded:
            return
            
        try:
            import clr
            # Tenta carregar pelo caminho se definido
            if self.dll_path:
                clr.AddReference(self.dll_path)
                self._adomd_loaded = True
                logger.info(f"ADOMD.NET carregado de: {self.dll_path}")
                return

            # Tenta carregar do GAC/Assembly (versão padrão do sistema)
            try:
                clr.AddReference("Microsoft.AnalysisServices.AdomdClient")
                self._adomd_loaded = True
                logger.info("ADOMD.NET carregado do GAC/Assembly")
                return
            except Exception:
                pass
                
            raise PowerBIConnectionError(
                "DLL ADOMD.NET não encontrada. "
                "Defina ADOMD_DLL_PATH no .env com o caminho completo."
            )
        except Exception as e:
            raise PowerBIConnectionError(f"Erro ao carregar ADOMD.NET: {e}")

    def _load_tom(self):
        """
        Carrega as bibliotecas do Tabular Object Model (TOM).
        Geralmente estão na mesma pasta do ADOMD ou do Power BI.
        """
        if self._tom_loaded:
            return

        # Tenta carregar do GAC primeiro
        try:
            import clr
            clr.AddReference("Microsoft.AnalysisServices.Tabular")
            clr.AddReference("Microsoft.AnalysisServices.Core")
            self._tom_loaded = True
            logger.info("TOM Libraries carregadas do GAC")
            return
        except:
            pass
            
        # Tenta encontrar na pasta do Power BI carregada
        exe_path = None
        if not self.port:
            try:
                _, exe_path = self.find_powerbi_port()
            except:
                pass
                
        dll_paths = []
        if exe_path:
            bin_dir = Path(exe_path).parent
            dll_paths.append(bin_dir / self.TOM_DLL_NAME)
        
        # Adiciona caminhos padrão do SDK
        for p in self.TOM_DLL_PATHS:
            dll_paths.append(Path(p))

        # Se temos o path do ADOMD, tente lá também
        if self.dll_path:
            adomd_dir = Path(self.dll_path).parent
            dll_paths.append(adomd_dir / self.TOM_DLL_NAME)
            
        found_tom = False
        for path in dll_paths:
            if path.exists():
                try:
                    import clr
                    # Carrega Core primeiro se existir
                    core_path = path.parent / self.CORE_DLL_NAME
                    if core_path.exists():
                        clr.AddReference(str(core_path))
                    
                    clr.AddReference(str(path))
                    self._tom_loaded = True
                    logger.info(f"TOM Libraries carregadas de: {path}")
                    found_tom = True
                    break
                except Exception as e:
                    logger.warning(f"Erro ao carregar TOM de {path}: {e}")
        
        if not found_tom:
            logger.warning("Bibliotecas TOM não encontradas. Funcionalidade de escrita indisponível.")

    def connect_tom(self):
        """
        Conecta ao servidor Tabular via TOM para escrita.
        Requer 'Allow external tools to modify the model' ativado no PBI.
        """
        if not self.port:
            self.connect() # Garante que temos a porta
            
        self._load_tom()
        
        if not self._tom_loaded:
            raise PowerBIConnectionError("Bibliotecas TOM não carregadas.")
            
        try:
            from Microsoft.AnalysisServices.Tabular import Server
            
            server = Server()
            connection_string = f"DataSource=localhost:{self.port}"
            server.Connect(connection_string)
            self.tom_server = server
            logger.info(f"Conectado via TOM na porta {self.port}")
            return server
            
        except Exception as e:
            raise PowerBIConnectionError(f"Erro ao conectar via TOM: {e}")

    def add_or_update_measure(self, table_name: str, measure_name: str, dax_code: str, description: str = "") -> bool:
        """
        Cria ou atualiza uma medida no modelo.
        
        Args:
            table_name: Nome da tabela onde criar a medida
            measure_name: Nome da medida
            dax_code: Código DAX da medida
            description: Descrição da medida (opcional)
            
        Returns:
            True se sucesso
        """
        if not self.tom_server:
            self.connect_tom()
            
        # Limpa o código DAX para remover a definição "Nome = " se existir
        # O TOM espera apenas a expressão (lado direito do igual)
        dax_expression = dax_code.strip()
        
        # Heurística simples: se a primeira linha tem = e não começa com VAR/RETURN
        first_line = dax_expression.split('\n')[0].strip()
        if '=' in first_line and not first_line.upper().startswith('VAR') and not first_line.upper().startswith('RETURN'):
            # Remove tudo até o primeiro =
            parts = dax_expression.split('=', 1)
            if len(parts) > 1:
                dax_expression = parts[1].strip()
            
        try:
            # Pega o banco de dados (geralmente só tem 1 no PBI Desktop)
            database = self.tom_server.Databases[0]
            model = database.Model
            
            # Encontra a tabela
            # TOM usa nomes internos, às vezes precisamos iterar para achar pelo nome visível
            target_table = None
            for table in model.Tables:
                if table.Name == table_name:
                    target_table = table
                    break
            
            if not target_table:
                # Tenta buscar pelo nome da tabela sem aspas, caso venha do schema
                clean_table_name = table_name.strip("[]")
                for table in model.Tables:
                    if table.Name == clean_table_name:
                        target_table = table
                        break
            
            if not target_table:
                raise ValueError(f"Tabela '{table_name}' não encontrada no modelo.")
                
            # Verifica se medida já existe
            from Microsoft.AnalysisServices.Tabular import Measure
            
            existing_measure = None
            for m in target_table.Measures:
                if m.Name == measure_name:
                    existing_measure = m
                    break
            
            if existing_measure:
                logger.info(f"Atualizando medida existente: {measure_name}")
                existing_measure.Expression = dax_expression
                if description:
                    existing_measure.Description = description
            else:
                logger.info(f"Criando nova medida: {measure_name}")
                new_measure = Measure()
                new_measure.Name = measure_name
                new_measure.Expression = dax_expression
                if description:
                    new_measure.Description = description
                target_table.Measures.Add(new_measure)
                
            # Salva alterações
            model.SaveChanges()
            logger.info("Modelo salvo com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao escrever medida: {e}")
            raise
    
    def connect(self) -> bool:
        """Estabelece conexão com o Power BI Desktop."""
        # Detecta porta e path se necessário
        exe_path = None
        if not self.port:
            self.port, exe_path = self.find_powerbi_port()
            
        # Tenta achar a DLL agora que temos o caminho do executável
        if not self.dll_path:
            self.dll_path = self._find_adomd_dll(exe_path)
        
        # Carrega ADOMD.NET
        self._load_adomd()
        
        try:
            from Microsoft.AnalysisServices.AdomdClient import AdomdConnection
            
            connection_string = f"Data Source=localhost:{self.port}"
            self.connection = AdomdConnection(connection_string)
            self.connection.Open()
            
            logger.info(f"Conectado ao Power BI na porta {self.port}")
            return True
            
        except Exception as e:
            raise PowerBIConnectionError(f"Falha ao conectar: {e}")
    
    def disconnect(self):
        """Fecha a conexão com Power BI."""
        if self.connection:
            try:
                self.connection.Close()
                self.connection = None
                logger.info("Conexão ADOMD fechada")
            except Exception as e:
                logger.warning(f"Erro ao fechar conexão ADOMD: {e}")
                
        if self.tom_server:
            try:
                self.tom_server.Disconnect()
                self.tom_server = None
                logger.info("Conexão TOM fechada")
            except Exception as e:
                logger.warning(f"Erro ao fechar conexão TOM: {e}")
    
    def execute_dax(self, query: str) -> list[dict]:
        """
        Executa uma query DAX e retorna os resultados.
        
        Args:
            query: Query DAX a executar
            
        Returns:
            Lista de dicionários com os resultados
        """
        if not self.connection:
            raise PowerBIConnectionError("Não conectado. Chame connect() primeiro.")
        
        try:
            from Microsoft.AnalysisServices.AdomdClient import AdomdCommand
            
            cmd = AdomdCommand(query, self.connection)
            reader = cmd.ExecuteReader()
            
            results = []
            columns = [reader.GetName(i) for i in range(reader.FieldCount)]
            
            while reader.Read():
                row = {}
                for i, col in enumerate(columns):
                    value = reader.GetValue(i)
                    # Converte tipos .NET para Python
                    if hasattr(value, 'ToString'):
                        row[col] = str(value)
                    else:
                        row[col] = value
                results.append(row)
            
            reader.Close()
            return results
            
        except Exception as e:
            logger.error(f"Erro na query DAX: {e}")
            raise
    
    def get_model_name(self) -> str:
        """Retorna o nome do modelo/catálogo atual."""
        if not self.connection:
            raise PowerBIConnectionError("Não conectado.")
        
        # O nome do banco está nos metadados da conexão
        try:
            query = "SELECT [CATALOG_NAME] FROM $SYSTEM.DBSCHEMA_CATALOGS"
            results = self.execute_dax(query)
            if results:
                return results[0].get('CATALOG_NAME', 'Unknown')
        except Exception:
            pass
        
        return "Unknown"
    
    def get_schema(self) -> ModelSchema:
        """
        Obtém o schema completo do modelo Power BI.
        
        Returns:
            ModelSchema com tabelas, colunas e medidas
        """
        if not self.connection:
            raise PowerBIConnectionError("Não conectado.")
        
        model_name = self.get_model_name()
        schema = ModelSchema(model_name=model_name)
        
        # Query para obter tabelas
        tables_query = """
        SELECT 
            [DIMENSION_UNIQUE_NAME] as TableName
        FROM $SYSTEM.MDSCHEMA_DIMENSIONS
        WHERE [DIMENSION_TYPE] = 3
        """
        
        try:
            tables_result = self.execute_dax(tables_query)
            table_names = [r['TableName'].strip('[]') for r in tables_result]
        except Exception as e:
            logger.warning(f"Erro ao obter tabelas: {e}")
            table_names = []
        
        # Para cada tabela, obtém colunas e medidas
        for table_name in table_names:
            table_info = TableInfo(name=table_name)
            
            # Colunas
            cols_query = f"""
            SELECT 
                [HIERARCHY_UNIQUE_NAME] as ColumnName
            FROM $SYSTEM.MDSCHEMA_HIERARCHIES
            WHERE [DIMENSION_UNIQUE_NAME] = '[{table_name}]'
            """
            
            try:
                cols_result = self.execute_dax(cols_query)
                for r in cols_result:
                    col_name = r['ColumnName']
                    # Extrai apenas o nome da coluna
                    match = re.search(r'\[([^\]]+)\]$', col_name)
                    if match:
                        table_info.columns.append(match.group(1))
            except Exception as e:
                logger.warning(f"Erro ao obter colunas de {table_name}: {e}")
            
            schema.tables.append(table_info)
        
        # Medidas (estão em uma estrutura diferente)
        measures_query = """
        SELECT 
            [MEASUREGROUP_NAME] as TableName,
            [MEASURE_NAME] as MeasureName
        FROM $SYSTEM.MDSCHEMA_MEASURES
        WHERE [MEASURE_IS_VISIBLE]
        """
        
        try:
            measures_result = self.execute_dax(measures_query)
            for r in measures_result:
                table_name = r.get('TableName', '')
                measure_name = r.get('MeasureName', '')
                
                # Adiciona medida à tabela correspondente
                for table in schema.tables:
                    if table.name == table_name:
                        table.measures.append(measure_name)
                        break
        except Exception as e:
            logger.warning(f"Erro ao obter medidas: {e}")
        
        return schema
    
    def test_connection(self) -> dict:
        """
        Testa a conexão e retorna informações básicas.
        
        Returns:
            Dicionário com status e informações do modelo
        """
        try:
            was_connected = self.connection is not None
            
            if not was_connected:
                self.connect()
            
            model_name = self.get_model_name()
            schema = self.get_schema()
            
            result = {
                "status": "connected",
                "port": self.port,
                "model_name": model_name,
                "tables_count": len(schema.tables),
                "tables": [t.name for t in schema.tables]
            }
            
            if not was_connected:
                self.disconnect()
            
            return result
            
        except PowerBIConnectionError as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Função helper para uso direto
def get_powerbi_connection() -> PowerBIConnector:
    """Cria e retorna um conector Power BI."""
    return PowerBIConnector()


if __name__ == "__main__":
    # Teste rápido do conector
    logging.basicConfig(level=logging.INFO)
    
    connector = PowerBIConnector()
    result = connector.test_connection()
    
    print("\n=== Teste de Conexão Power BI ===")
    for key, value in result.items():
        print(f"{key}: {value}")
