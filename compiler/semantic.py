from typing import List, Optional, Any
from .ast_nodes import *
from .tokens import Token, TokenType
from .symbol_table import SymbolTable, DataType, Symbol, SymbolType, TableSymbol, ColumnSymbol, FunctionSymbol
from .errors import SemanticError

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_table: Optional[str] = None
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []
    
    def error(self, node: ASTNode, message: str):
        if hasattr(node, 'table_name'):
            token = node.table_name
        elif hasattr(node, 'column_name'):
            token = node.column_name
        elif hasattr(node, 'function_name'):
            token = node.function_name
        else:
            # Create a dummy token for error reporting
            token = Token(TokenType.IDENTIFIER, "unknown", 0, 0)
        
        error = SemanticError(token, message)
        self.errors.append(error)
        raise error
    
    def warning(self, message: str):
        self.warnings.append(message)
    
    def visit(self, node):
        """Generic visit method that dispatches to specific visit methods"""
        method_name = f'visit_{node.__class__.__name__.lower()}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        """Fallback visitor method"""
        pass
    
    def analyze(self, program: Program) -> bool:
        try:
            self.visit_program(program)
            return len(self.errors) == 0
        except SemanticError:
            return False
    
    def visit_program(self, node: Program):
        for statement in node.statements:
            self.visit(statement)
    
    def visit_create_table_statement(self, node: CreateTableStatement):
        table_name = node.table_name.value
        
        # Check if table already exists
        if self.symbol_table.table_exists(table_name):
            self.error(node, f"Table '{table_name}' already exists")
        
        # Create table symbol
        table = self.symbol_table.define_table(table_name)
        
        # Add columns
        for column_def in node.columns:
            column_name = column_def.column_name.value
            data_type = self.symbol_table.convert_from_token_type(column_def.data_type.type)
            
            # Check for duplicate column names
            if table.get_column(column_name):
                self.error(column_def, f"Column '{column_name}' already exists in table '{table_name}'")
            
            # Add column to symbol table
            self.symbol_table.define_column(column_name, data_type, table_name)
    
    def visit_drop_table_statement(self, node: DropTableStatement):
        table_name = node.table_name.value
        
        # Check if table exists
        if not self.symbol_table.table_exists(table_name):
            self.error(node, f"Table '{table_name}' does not exist")
        
        # Note: In a real implementation, we'd remove the table from symbol table
        # For now, we just validate it exists
    
    def visit_alter_table_statement(self, node: AlterTableStatement):
        table_name = node.table_name.value
        
        # Check if table exists
        if not self.symbol_table.table_exists(table_name):
            self.error(node, f"Table '{table_name}' does not exist")
        
        # Check if column already exists
        column_name = node.column_def.column_name.value
        table = self.symbol_table.resolve_table(table_name)
        if table and table.get_column(column_name):
            self.error(node.column_def, f"Column '{column_name}' already exists in table '{table_name}'")
        
        # Add new column
        data_type = self.symbol_table.convert_from_token_type(node.column_def.data_type.type)
        self.symbol_table.define_column(column_name, data_type, table_name)
    
    def visit_select_statement(self, node: SelectStatement):
        table_name = node.table_name.value
        
        # Check if table exists
        if not self.symbol_table.table_exists(table_name):
            self.error(node, f"Table '{table_name}' does not exist")
        
        # Validate select list
        for expr in node.select_list:
            self.visit_select_expression(expr, table_name)
        
        # Validate WHERE clause
        if node.where_clause:
            self.visit_where_clause(node.where_clause, table_name)
        
        # Validate GROUP BY clause
        if node.group_clause:
            self.visit_group_clause(node.group_clause, table_name)
        
        # Validate ORDER BY clause
        if node.order_clause:
            self.visit_order_clause(node.order_clause, table_name)
    
    def visit_select_expression(self, expr: Expression, table_name: str):
        if isinstance(expr, AllColumns):
            # * is always valid
            pass
        elif isinstance(expr, ColumnReference):
            column_name = expr.column_name.value
            if not self.symbol_table.column_exists(column_name, table_name):
                self.error(expr, f"Column '{column_name}' does not exist in table '{table_name}'")
        elif isinstance(expr, FunctionCall):
            self.visit_function_call(expr, table_name)
        else:
            self.visit(expr)
    
    def visit_insert_statement(self, node: InsertStatement):
        table_name = node.table_name.value
        
        # Check if table exists
        if not self.symbol_table.table_exists(table_name):
            self.error(node, f"Table '{table_name}' does not exist")
        
        # Get table columns
        table = self.symbol_table.resolve_table(table_name)
        if not table:
            return
        
        # If columns specified, validate them
        if node.columns:
            column_names = [col.value for col in node.columns]
            for col_name in column_names:
                if not table.get_column(col_name):
                    self.error(node, f"Column '{col_name}' does not exist in table '{table_name}'")
            
            # Check if number of values matches columns
            if len(node.values) != len(node.columns):
                self.error(node, f"Number of values ({len(node.values)}) does not match number of columns ({len(node.columns)})")
        else:
            # If no columns specified, values must match all table columns
            table_columns = list(table.columns.keys())
            if len(node.values) != len(table_columns):
                self.error(node, f"Number of values ({len(node.values)}) does not match number of table columns ({len(table_columns)})")
        
        # Validate value types
        for i, value in enumerate(node.values):
            self.visit_insert_value(value, table_name, node.columns, i)
    
    def visit_insert_value(self, value: Expression, table_name: str, columns: Optional[List[Token]], index: int):
        table = self.symbol_table.resolve_table(table_name)
        if not table:
            return
        
        # Determine target column
        if columns and index < len(columns):
            column_name = columns[index].value
        else:
            column_names = list(table.columns.keys())
            if index < len(column_names):
                column_name = column_names[index]
            else:
                return
        
        column = table.get_column(column_name)
        if column:
            # Type checking
            value_type = self.get_expression_type(value)
            if value_type and not self.is_compatible_type(value_type, column.data_type):
                self.warning(f"Type mismatch: column '{column_name}' expects {column.data_type}, got {value_type}")
    
    def visit_update_statement(self, node: UpdateStatement):
        table_name = node.table_name.value
        
        # Check if table exists
        if not self.symbol_table.table_exists(table_name):
            self.error(node, f"Table '{table_name}' does not exist")
        
        # Validate assignments
        table = self.symbol_table.resolve_table(table_name)
        if table:
            for assignment in node.assignments:
                column_name = assignment.column_name.value
                column = table.get_column(column_name)
                
                if not column:
                    self.error(assignment, f"Column '{column_name}' does not exist in table '{table_name}'")
                else:
                    # Type checking
                    value_type = self.get_expression_type(assignment.value)
                    if value_type and not self.is_compatible_type(value_type, column.data_type):
                        self.warning(f"Type mismatch: column '{column_name}' expects {column.data_type}, got {value_type}")
        
        # Validate WHERE clause
        if node.where_clause:
            self.visit_where_clause(node.where_clause, table_name)
    
    def visit_delete_statement(self, node: DeleteStatement):
        table_name = node.table_name.value
        
        # Check if table exists
        if not self.symbol_table.table_exists(table_name):
            self.error(node, f"Table '{table_name}' does not exist")
        
        # Validate WHERE clause
        if node.where_clause:
            self.visit_where_clause(node.where_clause, table_name)
    
    def visit_grant_statement(self, node: GrantStatement):
        table_name = node.on_table.value
        
        # Check if table exists
        if not self.symbol_table.table_exists(table_name):
            self.error(node, f"Table '{table_name}' does not exist")
        
        # Validate privileges
        valid_privileges = ['select', 'insert', 'update', 'delete', 'all']
        for privilege in node.privileges:
            priv_name = privilege.value.lower()
            if priv_name not in valid_privileges:
                self.warning(f"Unknown privilege '{priv_name}'")
    
    def visit_revoke_statement(self, node: RevokeStatement):
        table_name = node.on_table.value
        
        # Check if table exists
        if not self.symbol_table.table_exists(table_name):
            self.error(node, f"Table '{table_name}' does not exist")
        
        # Validate privileges
        valid_privileges = ['select', 'insert', 'update', 'delete', 'all']
        for privilege in node.privileges:
            priv_name = privilege.value.lower()
            if priv_name not in valid_privileges:
                self.warning(f"Unknown privilege '{priv_name}'")
    
    def visit_where_clause(self, node: WhereClause, table_name: str):
        # WHERE clause must evaluate to boolean
        condition_type = self.get_expression_type(node.condition)
        if condition_type and condition_type != DataType.TEXT:  # SQLite uses 0/1 for boolean
            self.warning(f"WHERE condition should evaluate to boolean, got {condition_type}")
    
    def visit_group_clause(self, node: GroupClause, table_name: str):
        # Validate GROUP BY columns
        for column in node.columns:
            if isinstance(column, ColumnReference):
                column_name = column.column_name.value
                if not self.symbol_table.column_exists(column_name, table_name):
                    self.error(column, f"Column '{column_name}' does not exist in table '{table_name}'")
            else:
                self.visit(column)
    
    def visit_order_clause(self, node: OrderClause, table_name: str):
        # Validate ORDER BY columns
        for order_col in node.columns:
            if isinstance(order_col.column, ColumnReference):
                column_name = order_col.column.column_name.value
                if not self.symbol_table.column_exists(column_name, table_name):
                    self.error(order_col.column, f"Column '{column_name}' does not exist in table '{table_name}'")
            else:
                self.visit(order_col.column)
    
    def visit_function_call(self, node: FunctionCall, table_name: str):
        func_name = node.function_name.value.lower()
        
        # Check if function exists
        if not self.symbol_table.function_exists(func_name):
            self.error(node, f"Function '{func_name}' does not exist")
            return
        
        function = self.symbol_table.resolve_function(func_name)
        if function:
            # Check argument count
            if len(node.arguments) != function.param_count:
                self.error(node, f"Function '{func_name}' expects {function.param_count} arguments, got {len(node.arguments)}")
            
            # Check argument types
            for i, arg in enumerate(node.arguments):
                if i < len(function.param_types):
                    arg_type = self.get_expression_type(arg)
                    expected_type = function.param_types[i]
                    if arg_type and not self.is_compatible_type(arg_type, expected_type):
                        self.warning(f"Argument {i+1} of function '{func_name}' expects {expected_type}, got {arg_type}")
    
    def visit_binary_expression(self, node: BinaryExpression):
        left_type = self.get_expression_type(node.left)
        right_type = self.get_expression_type(node.right)
        
        # Type compatibility checking
        if left_type and right_type:
            if node.operator.type in [TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE]:
                # Comparison operators - both operands should be compatible
                if not self.is_comparable_type(left_type, right_type):
                    self.warning(f"Cannot compare {left_type} with {right_type}")
            elif node.operator.type in [TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE]:
                # Arithmetic operators - both should be numeric
                if left_type != DataType.NUMBER or right_type != DataType.NUMBER:
                    self.warning(f"Arithmetic operation requires numeric types, got {left_type} and {right_type}")
    
    def visit_unary_expression(self, node: UnaryExpression):
        operand_type = self.get_expression_type(node.operand)
        
        if node.operator.type == TokenType.NAHIN:  # NOT
            # NOT should work on boolean-like values
            pass  # SQLite allows NOT on any value
        elif node.operator.type == TokenType.MINUS:
            # Unary minus should work on numeric values
            if operand_type and operand_type != DataType.NUMBER:
                self.warning(f"Unary minus expects numeric type, got {operand_type}")
    
    def visit_literal(self, node: Literal):
        # Type is determined by the token
        if node.token.type == TokenType.NUMBER:
            return DataType.NUMBER
        elif node.token.type == TokenType.STRING:
            return DataType.TEXT
        return DataType.TEXT
    
    def visit_column_reference(self, node: ColumnReference):
        # Column reference type will be determined by the symbol table
        return DataType.TEXT  # Default, will be overridden by caller
    
    def visit_assignment(self, node: Assignment):
        # Assignment is handled in visit_update_statement
        pass
    
    def get_expression_type(self, expr: Expression) -> Optional[DataType]:
        if isinstance(expr, Literal):
            if expr.token.type == TokenType.NUMBER:
                return DataType.NUMBER
            elif expr.token.type == TokenType.STRING:
                return DataType.TEXT
        elif isinstance(expr, ColumnReference):
            # This would need context from the current table
            return DataType.TEXT  # Simplified
        elif isinstance(expr, FunctionCall):
            func_name = expr.function_name.value.lower()
            function = self.symbol_table.resolve_function(func_name)
            return function.data_type if function else DataType.TEXT
        elif isinstance(expr, BinaryExpression):
            # Simplified type inference
            left_type = self.get_expression_type(expr.left)
            right_type = self.get_expression_type(expr.right)
            
            if expr.operator.type in [TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE]:
                return DataType.NUMBER if left_type == DataType.NUMBER and right_type == DataType.NUMBER else DataType.TEXT
            else:
                return DataType.TEXT  # Comparisons return boolean-like values
        
        return DataType.TEXT
    
    def is_compatible_type(self, source_type: DataType, target_type: DataType) -> bool:
        # Simplified type compatibility
        if source_type == target_type:
            return True
        
        # NUMBER can be converted to INTEGER/REAL in SQLite
        if source_type == DataType.NUMBER and target_type in [DataType.INTEGER, DataType.REAL]:
            return True
        
        # TEXT is generally compatible with TEXT_SQL
        if source_type == DataType.TEXT and target_type == DataType.TEXT_SQL:
            return True
        
        return False
    
    def is_comparable_type(self, type1: DataType, type2: DataType) -> bool:
        # Simplified comparison compatibility
        return type1 == type2 or (type1 in [DataType.NUMBER, DataType.INTEGER, DataType.REAL] and 
                                  type2 in [DataType.NUMBER, DataType.INTEGER, DataType.REAL])
    
    def get_errors(self) -> List[SemanticError]:
        return self.errors
    
    def get_warnings(self) -> List[str]:
        return self.warnings