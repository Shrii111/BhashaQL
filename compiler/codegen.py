from typing import List, Optional, Dict, Any
from .ir import *
from .ast_nodes import *
from .symbol_table import SymbolTable, DataType

class SQLGenerator(IRVisitor):
    """Generates SQL code from IR nodes"""
    
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.generated_sql = ""
        self.indent_level = 0
        self.query_count = 0
    
    def visit(self, node: IRNode):
        """Generic visit method that dispatches to specific visit methods"""
        method_name = f'visit_{node.operation.value}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: IRNode):
        """Fallback visitor method"""
        return ""
    
    def generate(self, ir_program: IRProgram) -> List[str]:
        """Generate SQL statements from IR program"""
        sql_statements = []
        
        for statement in ir_program.statements:
            self.generated_sql = ""
            sql = statement.accept(self)
            if sql:
                sql_statements.append(sql)
        
        return sql_statements
    
    def visit_create_table(self, node: CreateTableIR) -> str:
        """Generate CREATE TABLE SQL"""
        table_name = node.get_attribute("table_name", "")
        columns = node.get_attribute("columns", [])
        
        column_defs = []
        for column in columns:
            col_name = column.get("name", "")
            col_type = self._convert_data_type(column.get("type", "text"))
            column_defs.append(f"{col_name} {col_type}")
        
        sql = f"CREATE TABLE {table_name} (\n    "
        sql += ",\n    ".join(column_defs)
        sql += "\n);"
        
        return sql
    
    def visit_drop_table(self, node: DropTableIR) -> str:
        """Generate DROP TABLE SQL"""
        table_name = node.get_attribute("table_name", "")
        return f"DROP TABLE {table_name};"
    
    def visit_alter_table(self, node: AlterTableIR) -> str:
        """Generate ALTER TABLE SQL"""
        table_name = node.get_attribute("table_name", "")
        action = node.get_attribute("action", "")
        column_def = node.get_attribute("column_def", {})
        
        col_name = column_def.get("name", "")
        col_type = self._convert_data_type(column_def.get("type", "text"))
        
        sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};"
        return sql
    
    def visit_scan(self, node: ScanIR) -> str:
        """Generate table scan SQL"""
        table_name = node.get_attribute("table_name", "")
        
        if node.get_attribute("use_index"):
            index_name = node.get_attribute("use_index", "")
            return f"SELECT * FROM {table_name} INDEXED BY {index_name}"
        
        return f"SELECT * FROM {table_name}"
    
    def visit_select(self, node: SelectIR) -> str:
        """Generate SELECT SQL"""
        columns = node.get_attribute("columns", [])
        source_sql = node.source.accept(self) if node.source else ""
        
        select_clause = "*"
        if columns and columns != ["*"]:
            select_clause = ", ".join(columns)
        
        sql = f"SELECT {select_clause} FROM ({source_sql})"
        return sql
    
    def visit_project(self, node: ProjectIR) -> str:
        """Generate projection SQL"""
        projections = node.get_attribute("projections", [])
        source_sql = node.source.accept(self) if node.source else ""
        
        select_clause = ", ".join(projections)
        sql = f"SELECT {select_clause} FROM ({source_sql})"
        return sql
    
    def visit_filter(self, node: FilterIR) -> str:
        """Generate WHERE clause SQL"""
        condition = node.get_attribute("condition", "")
        source_sql = node.source.accept(self) if node.source else ""
        
        sql = f"SELECT * FROM ({source_sql}) WHERE {condition}"
        return sql
    
    def visit_join(self, node: JoinIR) -> str:
        """Generate JOIN SQL"""
        left_sql = node.left.accept(self) if node.left else ""
        right_sql = node.right.accept(self) if node.right else ""
        condition = node.get_attribute("condition", "")
        join_type = node.get_attribute("join_type", "inner")
        
        join_clause = "INNER JOIN"
        if join_type == "left":
            join_clause = "LEFT JOIN"
        elif join_type == "right":
            join_clause = "RIGHT JOIN"
        elif join_type == "full":
            join_clause = "FULL OUTER JOIN"
        
        sql = f"SELECT * FROM ({left_sql}) {join_clause} ({right_sql}) ON {condition}"
        return sql
    
    def visit_group_by(self, node: GroupByIR) -> str:
        """Generate GROUP BY SQL"""
        group_columns = node.get_attribute("group_columns", [])
        source_sql = node.source.accept(self) if node.source else ""
        
        group_clause = ", ".join(group_columns)
        sql = f"SELECT * FROM ({source_sql}) GROUP BY {group_clause}"
        return sql
    
    def visit_order_by(self, node: OrderByIR) -> str:
        """Generate ORDER BY SQL"""
        order_columns = node.get_attribute("order_columns", [])
        source_sql = node.source.accept(self) if node.source else ""
        
        order_clauses = []
        for order_col in order_columns:
            column = order_col.get("column", "")
            direction = order_col.get("direction", "asc").upper()
            order_clauses.append(f"{column} {direction}")
        
        order_clause = ", ".join(order_clauses)
        sql = f"SELECT * FROM ({source_sql}) ORDER BY {order_clause}"
        return sql
    
    def visit_aggregate(self, node: AggregateIR) -> str:
        """Generate aggregate function SQL"""
        aggregates = node.get_attribute("aggregates", [])
        source_sql = node.source.accept(self) if node.source else ""
        
        agg_clauses = []
        for agg in aggregates:
            func = agg.get("function", "")
            column = agg.get("column", "")
            alias = agg.get("alias", "")
            
            if column == "*":
                agg_expr = f"{func}(*)"
            else:
                agg_expr = f"{func}({column})"
            
            if alias:
                agg_expr += f" AS {alias}"
            
            agg_clauses.append(agg_expr)
        
        select_clause = ", ".join(agg_clauses)
        sql = f"SELECT {select_clause} FROM ({source_sql})"
        return sql
    
    def visit_insert(self, node: InsertIR) -> str:
        """Generate INSERT SQL"""
        table_name = node.get_attribute("table_name", "")
        columns = node.get_attribute("columns", [])
        values = node.get_attribute("values", [])
        
        column_clause = ""
        if columns:
            column_clause = f" ({', '.join(columns)})"
        
        value_clauses = []
        for value in values:
            if isinstance(value, str):
                value_clauses.append(f"'{value}'")
            else:
                value_clauses.append(str(value))
        
        values_clause = f" ({', '.join(value_clauses)})"
        
        sql = f"INSERT INTO {table_name}{column_clause} VALUES{values_clause};"
        return sql
    
    def visit_update(self, node: UpdateIR) -> str:
        """Generate UPDATE SQL"""
        table_name = node.get_attribute("table_name", "")
        assignments = node.get_attribute("assignments", [])
        condition = node.get_attribute("condition", "")
        
        set_clauses = []
        for assignment in assignments:
            column = assignment.get("column", "")
            value = assignment.get("value", "")
            
            if isinstance(value, str):
                value = f"'{value}'"
            
            set_clauses.append(f"{column} = {value}")
        
        set_clause = ", ".join(set_clauses)
        sql = f"UPDATE {table_name} SET {set_clause}"
        
        if condition:
            sql += f" WHERE {condition}"
        
        sql += ";"
        return sql
    
    def visit_delete(self, node: DeleteIR) -> str:
        """Generate DELETE SQL"""
        table_name = node.get_attribute("table_name", "")
        condition = node.get_attribute("condition", "")
        
        sql = f"DELETE FROM {table_name}"
        
        if condition:
            sql += f" WHERE {condition}"
        
        sql += ";"
        return sql
    
    def visit_grant(self, node: GrantIR) -> str:
        """Generate GRANT SQL"""
        privileges = node.get_attribute("privileges", [])
        table_name = node.get_attribute("table_name", "")
        user = node.get_attribute("user", "")
        
        privilege_clause = ", ".join(privileges)
        sql = f"GRANT {privilege_clause} ON {table_name} TO {user};"
        return sql
    
    def visit_revoke(self, node: RevokeIR) -> str:
        """Generate REVOKE SQL"""
        privileges = node.get_attribute("privileges", [])
        table_name = node.get_attribute("table_name", "")
        user = node.get_attribute("user", "")
        
        privilege_clause = ", ".join(privileges)
        sql = f"REVOKE {privilege_clause} ON {table_name} FROM {user};"
        return sql
    
    def visit_limit(self, node: LimitIR) -> str:
        """Generate LIMIT SQL"""
        limit = node.get_attribute("limit", 10)
        source_sql = node.source.accept(self) if node.source else ""
        
        sql = f"SELECT * FROM ({source_sql}) LIMIT {limit}"
        return sql
    
    def visit_distinct(self, node: DistinctIR) -> str:
        """Generate DISTINCT SQL"""
        source_sql = node.source.accept(self) if node.source else ""
        
        sql = f"SELECT DISTINCT * FROM ({source_sql})"
        return sql
    
    def _convert_data_type(self, data_type: str) -> str:
        """Convert BhashaQL data type to SQLite data type"""
        type_mapping = {
            "number": "REAL",
            "text": "TEXT",
            "integer": "INTEGER",
            "boolean": "INTEGER",
            "date": "TEXT",
            "time": "TEXT"
        }
        
        return type_mapping.get(data_type.lower(), "TEXT")
    
    def _escape_string(self, value: str) -> str:
        """Escape string values for SQL"""
        if value is None:
            return "NULL"
        
        # Replace single quotes with two single quotes
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    
    def _format_value(self, value: Any) -> str:
        """Format value for SQL"""
        if value is None:
            return "NULL"
        elif isinstance(value, str):
            return self._escape_string(value)
        elif isinstance(value, bool):
            return "1" if value else "0"
        else:
            return str(value)

class ASTToIRGenerator:
    """Converts AST nodes to IR nodes"""
    
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
    
    def generate(self, program: Program) -> IRProgram:
        """Convert AST program to IR program"""
        ir_program = IRProgram()
        
        for statement in program.statements:
            ir_node = self._convert_statement(statement)
            if ir_node:
                ir_program.add_statement(ir_node)
        
        return ir_program
    
    def _convert_statement(self, statement: Statement) -> Optional[IRNode]:
        """Convert AST statement to IR node"""
        if isinstance(statement, CreateTableStatement):
            return self._convert_create_table(statement)
        elif isinstance(statement, DropTableStatement):
            return self._convert_drop_table(statement)
        elif isinstance(statement, AlterTableStatement):
            return self._convert_alter_table(statement)
        elif isinstance(statement, SelectStatement):
            return self._convert_select(statement)
        elif isinstance(statement, InsertStatement):
            return self._convert_insert(statement)
        elif isinstance(statement, UpdateStatement):
            return self._convert_update(statement)
        elif isinstance(statement, DeleteStatement):
            return self._convert_delete(statement)
        elif isinstance(statement, GrantStatement):
            return self._convert_grant(statement)
        elif isinstance(statement, RevokeStatement):
            return self._convert_revoke(statement)
        
        return None
    
    def _convert_create_table(self, node: CreateTableStatement) -> CreateTableIR:
        """Convert CREATE TABLE statement to IR"""
        table_name = node.table_name.value
        columns = []
        
        for column_def in node.columns:
            col_name = column_def.column_name.value
            col_type = column_def.data_type.value
            columns.append({"name": col_name, "type": col_type})
        
        return CreateTableIR(table_name, columns)
    
    def _convert_drop_table(self, node: DropTableStatement) -> DropTableIR:
        """Convert DROP TABLE statement to IR"""
        table_name = node.table_name.value
        return DropTableIR(table_name)
    
    def _convert_alter_table(self, node: AlterTableStatement) -> AlterTableIR:
        """Convert ALTER TABLE statement to IR"""
        table_name = node.table_name.value
        action = node.action.value
        column_def = {
            "name": node.column_def.column_name.value,
            "type": node.column_def.data_type.value
        }
        
        return AlterTableIR(table_name, action, column_def)
    
    def _convert_select(self, node: SelectStatement) -> SelectIR:
        """Convert SELECT statement to IR"""
        table_name = node.table_name.value
        
        # Build query tree
        scan = ScanIR(table_name)
        
        # Apply WHERE clause
        if node.where_clause:
            condition = self._expression_to_string(node.where_clause.condition)
            scan = FilterIR(scan, condition)
        
        # Apply GROUP BY
        if node.group_clause:
            group_columns = [self._expression_to_string(col) for col in node.group_clause.columns]
            scan = GroupByIR(scan, group_columns)
        
        # Apply ORDER BY
        if node.order_clause:
            order_columns = []
            for order_col in node.order_clause.columns:
                column = self._expression_to_string(order_col.column)
                direction = order_col.direction.value if order_col.direction else "asc"
                order_columns.append({"column": column, "direction": direction})
            scan = OrderByIR(scan, order_columns)
        
        # Apply SELECT list
        select_columns = []
        for expr in node.select_list:
            if isinstance(expr, AllColumns):
                select_columns.append("*")
            elif isinstance(expr, ColumnReference):
                select_columns.append(expr.column_name.value)
            elif isinstance(expr, FunctionCall):
                func_name = expr.function_name.value
                if expr.arguments:
                    arg = self._expression_to_string(expr.arguments[0])
                    select_columns.append(f"{func_name}({arg})")
                else:
                    select_columns.append(f"{func_name}(*)")
            else:
                select_columns.append(self._expression_to_string(expr))
        
        return SelectIR(scan, select_columns)
    
    def _convert_insert(self, node: InsertStatement) -> InsertIR:
        """Convert INSERT statement to IR"""
        table_name = node.table_name.value
        
        columns = []
        if node.columns:
            columns = [col.value for col in node.columns]
        
        values = []
        for value in node.values:
            values.append(self._expression_to_value(value))
        
        return InsertIR(table_name, columns, values)
    
    def _convert_update(self, node: UpdateStatement) -> UpdateIR:
        """Convert UPDATE statement to IR"""
        table_name = node.table_name.value
        
        assignments = []
        for assignment in node.assignments:
            column = assignment.column_name.value
            value = self._expression_to_value(assignment.value)
            assignments.append({"column": column, "value": value})
        
        condition = None
        if node.where_clause:
            condition = self._expression_to_string(node.where_clause.condition)
        
        return UpdateIR(table_name, assignments, condition)
    
    def _convert_delete(self, node: DeleteStatement) -> DeleteIR:
        """Convert DELETE statement to IR"""
        table_name = node.table_name.value
        
        condition = None
        if node.where_clause:
            condition = self._expression_to_string(node.where_clause.condition)
        
        return DeleteIR(table_name, condition)
    
    def _convert_grant(self, node: GrantStatement) -> GrantIR:
        """Convert GRANT statement to IR"""
        privileges = [priv.value for priv in node.privileges]
        table_name = node.on_table.value
        user = node.to_user.value
        
        return GrantIR(privileges, table_name, user)
    
    def _convert_revoke(self, node: RevokeStatement) -> RevokeIR:
        """Convert REVOKE statement to IR"""
        privileges = [priv.value for priv in node.privileges]
        table_name = node.on_table.value
        user = node.from_user.value
        
        return RevokeIR(privileges, table_name, user)
    
    def _expression_to_string(self, expr: Expression) -> str:
        """Convert expression to string representation"""
        if isinstance(expr, Literal):
            if expr.token.type == TokenType.STRING:
                return f"'{expr.value}'"
            return str(expr.value)
        elif isinstance(expr, ColumnReference):
            return expr.column_name.value
        elif isinstance(expr, BinaryExpression):
            left = self._expression_to_string(expr.left)
            right = self._expression_to_string(expr.right)
            operator = expr.operator.value
            return f"{left} {operator} {right}"
        elif isinstance(expr, UnaryExpression):
            operand = self._expression_to_string(expr.operand)
            operator = expr.operator.value
            return f"{operator}{operand}"
        else:
            return str(expr)
    
    def _expression_to_value(self, expr: Expression) -> Any:
        """Convert expression to value"""
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, ColumnReference):
            return expr.column_name.value
        else:
            return self._expression_to_string(expr)

class CodeGenerator:
    """Main code generator that orchestrates the process"""
    
    def __init__(self, symbol_table: SymbolTable):
        self.symbol_table = symbol_table
        self.ir_generator = ASTToIRGenerator(symbol_table)
        self.sql_generator = SQLGenerator(symbol_table)
    
    def generate_sql(self, program: Program) -> List[str]:
        """Generate SQL from AST program"""
        # Convert AST to IR
        ir_program = self.ir_generator.generate(program)
        
        # Generate SQL from IR
        sql_statements = self.sql_generator.generate(ir_program)
        
        return sql_statements
    
    def generate_single_sql(self, statement: Statement) -> str:
        """Generate SQL from single AST statement"""
        # Convert statement to IR
        ir_node = self.ir_generator._convert_statement(statement)
        
        if ir_node:
            # Generate SQL from IR
            sql = ir_node.accept(self.sql_generator)
            return sql
        
        return ""