from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict, Union
from enum import Enum
from .tokens import Token, TokenType

class IROperation(Enum):
    # DDL Operations
    CREATE_TABLE = "create_table"
    DROP_TABLE = "drop_table"
    ALTER_TABLE = "alter_table"
    
    # DQL Operations
    SELECT = "select"
    PROJECT = "project"
    FILTER = "filter"
    JOIN = "join"
    GROUP_BY = "group_by"
    ORDER_BY = "order_by"
    AGGREGATE = "aggregate"
    
    # DML Operations
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    
    # DCL Operations
    GRANT = "grant"
    REVOKE = "revoke"
    
    # Utility Operations
    SCAN = "scan"
    LIMIT = "limit"
    DISTINCT = "distinct"

class IRNode(ABC):
    """Base class for all IR nodes"""
    
    def __init__(self, operation: IROperation):
        self.operation = operation
        self.children: List['IRNode'] = []
        self.attributes: Dict[str, Any] = {}
    
    @abstractmethod
    def accept(self, visitor):
        pass
    
    def add_child(self, child: 'IRNode'):
        self.children.append(child)
    
    def set_attribute(self, key: str, value: Any):
        self.attributes[key] = value
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        return self.attributes.get(key, default)
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.operation.value})"

class IRVisitor(ABC):
    """Visitor pattern for IR traversal"""
    
    @abstractmethod
    def visit(self, node: IRNode):
        pass

# ============ DDL IR Nodes ============

class CreateTableIR(IRNode):
    def __init__(self, table_name: str, columns: List[Dict[str, Any]]):
        super().__init__(IROperation.CREATE_TABLE)
        self.table_name = table_name
        self.columns = columns
        self.set_attribute("table_name", table_name)
        self.set_attribute("columns", columns)
    
    def accept(self, visitor):
        return visitor.visit_create_table(self)

class DropTableIR(IRNode):
    def __init__(self, table_name: str):
        super().__init__(IROperation.DROP_TABLE)
        self.table_name = table_name
        self.set_attribute("table_name", table_name)
    
    def accept(self, visitor):
        return visitor.visit_drop_table(self)

class AlterTableIR(IRNode):
    def __init__(self, table_name: str, action: str, column_def: Dict[str, Any]):
        super().__init__(IROperation.ALTER_TABLE)
        self.table_name = table_name
        self.action = action
        self.column_def = column_def
        self.set_attribute("table_name", table_name)
        self.set_attribute("action", action)
        self.set_attribute("column_def", column_def)
    
    def accept(self, visitor):
        return visitor.visit_alter_table(self)

# ============ DQL IR Nodes ============

class ScanIR(IRNode):
    def __init__(self, table_name: str):
        super().__init__(IROperation.SCAN)
        self.table_name = table_name
        self.set_attribute("table_name", table_name)
    
    def accept(self, visitor):
        return visitor.visit_scan(self)

class SelectIR(IRNode):
    def __init__(self, source: IRNode, columns: List[str]):
        super().__init__(IROperation.SELECT)
        self.source = source
        self.columns = columns
        self.add_child(source)
        self.set_attribute("columns", columns)
    
    def accept(self, visitor):
        return visitor.visit_select(self)

class ProjectIR(IRNode):
    def __init__(self, source: IRNode, projections: List[str]):
        super().__init__(IROperation.PROJECT)
        self.source = source
        self.projections = projections
        self.add_child(source)
        self.set_attribute("projections", projections)
    
    def accept(self, visitor):
        return visitor.visit_project(self)

class FilterIR(IRNode):
    def __init__(self, source: IRNode, condition: str):
        super().__init__(IROperation.FILTER)
        self.source = source
        self.condition = condition
        self.add_child(source)
        self.set_attribute("condition", condition)
    
    def accept(self, visitor):
        return visitor.visit_filter(self)

class JoinIR(IRNode):
    def __init__(self, left: IRNode, right: IRNode, condition: str, join_type: str = "inner"):
        super().__init__(IROperation.JOIN)
        self.left = left
        self.right = right
        self.condition = condition
        self.join_type = join_type
        self.add_child(left)
        self.add_child(right)
        self.set_attribute("condition", condition)
        self.set_attribute("join_type", join_type)
    
    def accept(self, visitor):
        return visitor.visit_join(self)

class GroupByIR(IRNode):
    def __init__(self, source: IRNode, group_columns: List[str]):
        super().__init__(IROperation.GROUP_BY)
        self.source = source
        self.group_columns = group_columns
        self.add_child(source)
        self.set_attribute("group_columns", group_columns)
    
    def accept(self, visitor):
        return visitor.visit_group_by(self)

class OrderByIR(IRNode):
    def __init__(self, source: IRNode, order_columns: List[Dict[str, Any]]):
        super().__init__(IROperation.ORDER_BY)
        self.source = source
        self.order_columns = order_columns
        self.add_child(source)
        self.set_attribute("order_columns", order_columns)
    
    def accept(self, visitor):
        return visitor.visit_order_by(self)

class AggregateIR(IRNode):
    def __init__(self, source: IRNode, aggregates: List[Dict[str, Any]]):
        super().__init__(IROperation.AGGREGATE)
        self.source = source
        self.aggregates = aggregates
        self.add_child(source)
        self.set_attribute("aggregates", aggregates)
    
    def accept(self, visitor):
        return visitor.visit_aggregate(self)

# ============ DML IR Nodes ============

class InsertIR(IRNode):
    def __init__(self, table_name: str, columns: List[str], values: List[Any]):
        super().__init__(IROperation.INSERT)
        self.table_name = table_name
        self.columns = columns
        self.values = values
        self.set_attribute("table_name", table_name)
        self.set_attribute("columns", columns)
        self.set_attribute("values", values)
    
    def accept(self, visitor):
        return visitor.visit_insert(self)

class UpdateIR(IRNode):
    def __init__(self, table_name: str, assignments: List[Dict[str, Any]], condition: Optional[str] = None):
        super().__init__(IROperation.UPDATE)
        self.table_name = table_name
        self.assignments = assignments
        self.condition = condition
        self.set_attribute("table_name", table_name)
        self.set_attribute("assignments", assignments)
        if condition:
            self.set_attribute("condition", condition)
    
    def accept(self, visitor):
        return visitor.visit_update(self)

class DeleteIR(IRNode):
    def __init__(self, table_name: str, condition: Optional[str] = None):
        super().__init__(IROperation.DELETE)
        self.table_name = table_name
        self.condition = condition
        self.set_attribute("table_name", table_name)
        if condition:
            self.set_attribute("condition", condition)
    
    def accept(self, visitor):
        return visitor.visit_delete(self)

# ============ DCL IR Nodes ============

class GrantIR(IRNode):
    def __init__(self, privileges: List[str], table_name: str, user: str):
        super().__init__(IROperation.GRANT)
        self.privileges = privileges
        self.table_name = table_name
        self.user = user
        self.set_attribute("privileges", privileges)
        self.set_attribute("table_name", table_name)
        self.set_attribute("user", user)
    
    def accept(self, visitor):
        return visitor.visit_grant(self)

class RevokeIR(IRNode):
    def __init__(self, privileges: List[str], table_name: str, user: str):
        super().__init__(IROperation.REVOKE)
        self.privileges = privileges
        self.table_name = table_name
        self.user = user
        self.set_attribute("privileges", privileges)
        self.set_attribute("table_name", table_name)
        self.set_attribute("user", user)
    
    def accept(self, visitor):
        return visitor.visit_revoke(self)

# ============ Utility IR Nodes ============

class LimitIR(IRNode):
    def __init__(self, source: IRNode, limit: int):
        super().__init__(IROperation.LIMIT)
        self.source = source
        self.limit = limit
        self.add_child(source)
        self.set_attribute("limit", limit)
    
    def accept(self, visitor):
        return visitor.visit_limit(self)

class DistinctIR(IRNode):
    def __init__(self, source: IRNode):
        super().__init__(IROperation.DISTINCT)
        self.source = source
        self.add_child(source)
    
    def accept(self, visitor):
        return visitor.visit_distinct(self)

# ============ IR Program ============

class IRProgram:
    """Container for a complete IR program"""
    
    def __init__(self):
        self.statements: List[IRNode] = []
        self.global_symbols: Dict[str, Any] = {}
    
    def add_statement(self, statement: IRNode):
        self.statements.append(statement)
    
    def set_global_symbol(self, name: str, value: Any):
        self.global_symbols[name] = value
    
    def get_global_symbol(self, name: str, default: Any = None) -> Any:
        return self.global_symbols.get(name, default)
    
    def accept(self, visitor):
        results = []
        for statement in self.statements:
            results.append(statement.accept(visitor))
        return results
    
    def __repr__(self):
        return f"IRProgram({len(self.statements)} statements)"

# ============ IR Builder ============

class IRBuilder:
    """Helper class to build IR nodes"""
    
    @staticmethod
    def create_table(table_name: str, columns: List[Dict[str, Any]]) -> CreateTableIR:
        return CreateTableIR(table_name, columns)
    
    @staticmethod
    def drop_table(table_name: str) -> DropTableIR:
        return DropTableIR(table_name)
    
    @staticmethod
    def scan_table(table_name: str) -> ScanIR:
        return ScanIR(table_name)
    
    @staticmethod
    def select_columns(source: IRNode, columns: List[str]) -> SelectIR:
        return SelectIR(source, columns)
    
    @staticmethod
    def filter_rows(source: IRNode, condition: str) -> FilterIR:
        return FilterIR(source, condition)
    
    @staticmethod
    def insert_data(table_name: str, columns: List[str], values: List[Any]) -> InsertIR:
        return InsertIR(table_name, columns, values)
    
    @staticmethod
    def update_data(table_name: str, assignments: List[Dict[str, Any]], condition: Optional[str] = None) -> UpdateIR:
        return UpdateIR(table_name, assignments, condition)
    
    @staticmethod
    def delete_data(table_name: str, condition: Optional[str] = None) -> DeleteIR:
        return DeleteIR(table_name, condition)
    
    @staticmethod
    def order_results(source: IRNode, order_columns: List[Dict[str, Any]]) -> OrderByIR:
        return OrderByIR(source, order_columns)
    
    @staticmethod
    def group_results(source: IRNode, group_columns: List[str]) -> GroupByIR:
        return GroupByIR(source, group_columns)
    
    @staticmethod
    def aggregate_results(source: IRNode, aggregates: List[Dict[str, Any]]) -> AggregateIR:
        return AggregateIR(source, aggregates)