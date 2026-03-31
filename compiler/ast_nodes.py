from abc import ABC, abstractmethod
from typing import List, Optional, Any, Union
from .tokens import Token

class ASTNode(ABC):
    """Base class for all AST nodes"""
    
    @abstractmethod
    def accept(self, visitor):
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"

class Statement(ASTNode):
    """Base class for all statements"""
    pass

class Expression(ASTNode):
    """Base class for all expressions"""
    pass

# ============ STATEMENTS ============

class CreateTableStatement(Statement):
    def __init__(self, table_name: Token, columns: List['ColumnDefinition']):
        self.table_name = table_name
        self.columns = columns
    
    def accept(self, visitor):
        return visitor.visit_create_table_statement(self)
    
    def __repr__(self):
        return f"CreateTableStatement({self.table_name.value}, {self.columns})"

class DropTableStatement(Statement):
    def __init__(self, table_name: Token):
        self.table_name = table_name
    
    def accept(self, visitor):
        return visitor.visit_drop_table_statement(self)
    
    def __repr__(self):
        return f"DropTableStatement({self.table_name.value})"

class AlterTableStatement(Statement):
    def __init__(self, table_name: Token, action: Token, column_def: 'ColumnDefinition'):
        self.table_name = table_name
        self.action = action
        self.column_def = column_def
    
    def accept(self, visitor):
        return visitor.visit_alter_table_statement(self)
    
    def __repr__(self):
        return f"AlterTableStatement({self.table_name.value}, {self.action.value}, {self.column_def})"

class SelectStatement(Statement):
    def __init__(self, select_list: List[Expression], table_name: Token, 
                 where_clause: Optional['WhereClause'] = None,
                 group_clause: Optional['GroupClause'] = None,
                 order_clause: Optional['OrderClause'] = None):
        self.select_list = select_list
        self.table_name = table_name
        self.where_clause = where_clause
        self.group_clause = group_clause
        self.order_clause = order_clause
    
    def accept(self, visitor):
        return visitor.visit_select_statement(self)
    
    def __repr__(self):
        return f"SelectStatement({self.select_list}, {self.table_name.value})"

class InsertStatement(Statement):
    def __init__(self, table_name: Token, columns: Optional[List[Token]], 
                 values: List[Expression]):
        self.table_name = table_name
        self.columns = columns
        self.values = values
    
    def accept(self, visitor):
        return visitor.visit_insert_statement(self)
    
    def __repr__(self):
        return f"InsertStatement({self.table_name.value}, {self.columns}, {self.values})"

class UpdateStatement(Statement):
    def __init__(self, table_name: Token, assignments: List['Assignment'],
                 where_clause: Optional['WhereClause'] = None):
        self.table_name = table_name
        self.assignments = assignments
        self.where_clause = where_clause
    
    def accept(self, visitor):
        return visitor.visit_update_statement(self)
    
    def __repr__(self):
        return f"UpdateStatement({self.table_name.value}, {self.assignments})"

class DeleteStatement(Statement):
    def __init__(self, table_name: Token, where_clause: Optional['WhereClause'] = None):
        self.table_name = table_name
        self.where_clause = where_clause
    
    def accept(self, visitor):
        return visitor.visit_delete_statement(self)
    
    def __repr__(self):
        return f"DeleteStatement({self.table_name.value})"

class GrantStatement(Statement):
    def __init__(self, privileges: List[Token], on_table: Token, to_user: Token):
        self.privileges = privileges
        self.on_table = on_table
        self.to_user = to_user
    
    def accept(self, visitor):
        return visitor.visit_grant_statement(self)
    
    def __repr__(self):
        return f"GrantStatement({[p.value for p in self.privileges]}, {self.on_table.value}, {self.to_user.value})"

class RevokeStatement(Statement):
    def __init__(self, privileges: List[Token], on_table: Token, from_user: Token):
        self.privileges = privileges
        self.on_table = on_table
        self.from_user = from_user
    
    def accept(self, visitor):
        return visitor.visit_revoke_statement(self)
    
    def __repr__(self):
        return f"RevokeStatement({[p.value for p in self.privileges]}, {self.on_table.value}, {self.from_user.value})"

# ============ EXPRESSIONS ============

class ColumnDefinition(Expression):
    def __init__(self, column_name: Token, data_type: Token):
        self.column_name = column_name
        self.data_type = data_type
    
    def accept(self, visitor):
        return visitor.visit_column_definition(self)
    
    def __repr__(self):
        return f"ColumnDefinition({self.column_name.value}, {self.data_type.value})"

class Assignment(Expression):
    def __init__(self, column_name: Token, value: Expression):
        self.column_name = column_name
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_assignment(self)
    
    def __repr__(self):
        return f"Assignment({self.column_name.value}, {self.value})"

class WhereClause(Expression):
    def __init__(self, condition: Expression):
        self.condition = condition
    
    def accept(self, visitor):
        return visitor.visit_where_clause(self)
    
    def __repr__(self):
        return f"WhereClause({self.condition})"

class GroupClause(Expression):
    def __init__(self, columns: List[Expression]):
        self.columns = columns
    
    def accept(self, visitor):
        return visitor.visit_group_clause(self)
    
    def __repr__(self):
        return f"GroupClause({self.columns})"

class OrderClause(Expression):
    def __init__(self, columns: List['OrderColumn']):
        self.columns = columns
    
    def accept(self, visitor):
        return visitor.visit_order_clause(self)
    
    def __repr__(self):
        return f"OrderClause({self.columns})"

class OrderColumn(Expression):
    def __init__(self, column: Expression, direction: Optional[Token] = None):
        self.column = column
        self.direction = direction  # ASC or DESC
    
    def accept(self, visitor):
        return visitor.visit_order_column(self)
    
    def __repr__(self):
        dir_str = f" {self.direction.value}" if self.direction else ""
        return f"OrderColumn({self.column}{dir_str})"

class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: Token, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_binary_expression(self)
    
    def __repr__(self):
        return f"BinaryExpression({self.left} {self.operator.value} {self.right})"

class UnaryExpression(Expression):
    def __init__(self, operator: Token, operand: Expression):
        self.operator = operator
        self.operand = operand
    
    def accept(self, visitor):
        return visitor.visit_unary_expression(self)
    
    def __repr__(self):
        return f"UnaryExpression({self.operator.value}{self.operand})"

class FunctionCall(Expression):
    def __init__(self, function_name: Token, arguments: List[Expression]):
        self.function_name = function_name
        self.arguments = arguments
    
    def accept(self, visitor):
        return visitor.visit_function_call(self)
    
    def __repr__(self):
        return f"FunctionCall({self.function_name.value}({self.arguments}))"

class ColumnReference(Expression):
    def __init__(self, column_name: Token):
        self.column_name = column_name
    
    def accept(self, visitor):
        return visitor.visit_column_reference(self)
    
    def __repr__(self):
        return f"ColumnReference({self.column_name.value})"

class Literal(Expression):
    def __init__(self, token: Token):
        self.token = token
        self.value = token.value
    
    def accept(self, visitor):
        return visitor.visit_literal(self)
    
    def __repr__(self):
        return f"Literal({self.value})"

class AllColumns(Expression):
    def __init__(self, token: Token):
        self.token = token
    
    def accept(self, visitor):
        return visitor.visit_all_columns(self)
    
    def __repr__(self):
        return "AllColumns(*)"

# ============ PROGRAM ROOT ============

class Program(ASTNode):
    def __init__(self, statements: List[Statement]):
        self.statements = statements
    
    def accept(self, visitor):
        return visitor.visit_program(self)
    
    def __repr__(self):
        return f"Program({self.statements})"