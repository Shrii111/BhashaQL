from typing import Dict, List, Optional, Any
from enum import Enum
from .tokens import Token, TokenType

class DataType(Enum):
    NUMBER = "number"
    TEXT = "text"
    INTEGER = "INTEGER"
    REAL = "REAL"
    TEXT_SQL = "TEXT"

class SymbolType(Enum):
    TABLE = "table"
    COLUMN = "column"
    FUNCTION = "function"
    VARIABLE = "variable"

class Symbol:
    def __init__(self, name: str, symbol_type: SymbolType, data_type: Optional[DataType] = None):
        self.name = name
        self.symbol_type = symbol_type
        self.data_type = data_type
        self.attributes: Dict[str, Any] = {}
    
    def __repr__(self):
        return f"Symbol({self.name}, {self.symbol_type}, {self.data_type})"

class TableSymbol(Symbol):
    def __init__(self, name: str):
        super().__init__(name, SymbolType.TABLE)
        self.columns: Dict[str, 'ColumnSymbol'] = {}
    
    def add_column(self, column: 'ColumnSymbol'):
        self.columns[column.name] = column
    
    def get_column(self, name: str) -> Optional['ColumnSymbol']:
        return self.columns.get(name)
    
    def __repr__(self):
        return f"TableSymbol({self.name}, columns={list(self.columns.keys())})"

class ColumnSymbol(Symbol):
    def __init__(self, name: str, data_type: DataType, table_name: str):
        super().__init__(name, SymbolType.COLUMN, data_type)
        self.table_name = table_name
    
    def __repr__(self):
        return f"ColumnSymbol({self.name}, {self.data_type}, table={self.table_name})"

class FunctionSymbol(Symbol):
    def __init__(self, name: str, return_type: DataType, param_types: List[DataType]):
        super().__init__(name, SymbolType.FUNCTION, return_type)
        self.param_types = param_types
        self.param_count = len(param_types)
    
    def __repr__(self):
        return f"FunctionSymbol({self.name}, returns={self.data_type}, params={self.param_types})"

class Scope:
    def __init__(self, name: str, parent: Optional['Scope'] = None):
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
    
    def define(self, symbol: Symbol):
        self.symbols[symbol.name] = symbol
    
    def resolve(self, name: str) -> Optional[Symbol]:
        # Check current scope
        if name in self.symbols:
            return self.symbols[name]
        
        # Check parent scope
        if self.parent:
            return self.parent.resolve(name)
        
        return None
    
    def __repr__(self):
        return f"Scope({self.name}, symbols={list(self.symbols.keys())})"

class SymbolTable:
    def __init__(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.built_in_functions = self._initialize_builtin_functions()
        self._register_builtin_functions()
    
    def _initialize_builtin_functions(self) -> Dict[str, FunctionSymbol]:
        return {
            'count': FunctionSymbol('count', DataType.INTEGER, [DataType.TEXT]),
            'sum': FunctionSymbol('sum', DataType.REAL, [DataType.NUMBER]),
            'avg': FunctionSymbol('avg', DataType.REAL, [DataType.NUMBER]),
            'max': FunctionSymbol('max', DataType.NUMBER, [DataType.NUMBER]),
            'min': FunctionSymbol('min', DataType.NUMBER, [DataType.NUMBER]),
        }
    
    def _register_builtin_functions(self):
        for func in self.built_in_functions.values():
            self.global_scope.define(func)
    
    def push_scope(self, name: str):
        new_scope = Scope(name, self.current_scope)
        self.current_scope = new_scope
        return new_scope
    
    def pop_scope(self):
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def define_table(self, table_name: str) -> TableSymbol:
        table = TableSymbol(table_name)
        self.current_scope.define(table)
        return table
    
    def define_column(self, column_name: str, data_type: DataType, table_name: str) -> ColumnSymbol:
        column = ColumnSymbol(column_name, data_type, table_name)
        self.current_scope.define(column)
        
        # Also add to table's column list
        table = self.resolve_table(table_name)
        if table:
            table.add_column(column)
        
        return column
    
    def define_function(self, name: str, return_type: DataType, param_types: List[DataType]) -> FunctionSymbol:
        function = FunctionSymbol(name, return_type, param_types)
        self.current_scope.define(function)
        return function
    
    def resolve_symbol(self, name: str) -> Optional[Symbol]:
        return self.current_scope.resolve(name)
    
    def resolve_table(self, name: str) -> Optional[TableSymbol]:
        symbol = self.resolve_symbol(name)
        if symbol and isinstance(symbol, TableSymbol):
            return symbol
        return None
    
    def resolve_column(self, name: str) -> Optional[ColumnSymbol]:
        symbol = self.resolve_symbol(name)
        if symbol and isinstance(symbol, ColumnSymbol):
            return symbol
        return None
    
    def resolve_function(self, name: str) -> Optional[FunctionSymbol]:
        symbol = self.resolve_symbol(name)
        if symbol and isinstance(symbol, FunctionSymbol):
            return symbol
        return None
    
    def table_exists(self, name: str) -> bool:
        return self.resolve_table(name) is not None
    
    def column_exists(self, name: str, table_name: Optional[str] = None) -> bool:
        if table_name:
            table = self.resolve_table(table_name)
            if table:
                return table.get_column(name) is not None
            return False
        else:
            return self.resolve_column(name) is not None
    
    def function_exists(self, name: str) -> bool:
        return self.resolve_function(name) is not None
    
    def get_table_columns(self, table_name: str) -> List[ColumnSymbol]:
        table = self.resolve_table(table_name)
        if table:
            return list(table.columns.values())
        return []
    
    def get_column_type(self, column_name: str, table_name: Optional[str] = None) -> Optional[DataType]:
        if table_name:
            table = self.resolve_table(table_name)
            if table:
                column = table.get_column(column_name)
                return column.data_type if column else None
        else:
            column = self.resolve_column(column_name)
            return column.data_type if column else None
        return None
    
    def convert_to_sql_type(self, data_type: DataType) -> str:
        mapping = {
            DataType.NUMBER: "REAL",
            DataType.TEXT: "TEXT",
            DataType.INTEGER: "INTEGER",
            DataType.REAL: "REAL",
            DataType.TEXT_SQL: "TEXT"
        }
        return mapping.get(data_type, "TEXT")
    
    def convert_from_token_type(self, token_type: TokenType) -> DataType:
        if token_type == TokenType.NUMBER_TYPE:
            return DataType.NUMBER
        elif token_type == TokenType.TEXT_TYPE:
            return DataType.TEXT
        else:
            return DataType.TEXT
    
    def __repr__(self):
        return f"SymbolTable(current_scope={self.current_scope.name})"