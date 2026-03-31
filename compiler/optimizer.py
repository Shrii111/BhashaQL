from typing import List, Optional, Dict, Any, Set
from .ir import *
from .ast_nodes import *
from .symbol_table import SymbolTable, DataType

class OptimizationRule:
    """Base class for optimization rules"""
    
    def __init__(self, name: str):
        self.name = name
        self.applications = 0
    
    def apply(self, node: IRNode) -> Optional[IRNode]:
        """Apply optimization rule to a node"""
        raise NotImplementedError
    
    def can_apply(self, node: IRNode) -> bool:
        """Check if rule can be applied to this node"""
        raise NotImplementedError

class PredicatePushdown(OptimizationRule):
    """Push WHERE conditions down to the earliest possible point"""
    
    def __init__(self):
        super().__init__("Predicate Pushdown")
    
    def can_apply(self, node: IRNode) -> bool:
        return isinstance(node, FilterIR) and len(node.children) > 0
    
    def apply(self, node: IRNode) -> Optional[IRNode]:
        if not self.can_apply(node):
            return None
        
        filter_node = node
        source = filter_node.children[0] if filter_node.children else None
        
        if not source:
            return None
        
        # Try to push filter down through joins
        if isinstance(source, JoinIR):
            return self._push_through_join(filter_node, source)
        
        # Try to push filter down through projections
        elif isinstance(source, ProjectIR):
            return self._push_through_projection(filter_node, source)
        
        # Try to push filter down through aggregations
        elif isinstance(source, AggregateIR):
            return self._push_through_aggregation(filter_node, source)
        
        return None
    
    def _push_through_join(self, filter_node: FilterIR, join_node: JoinIR) -> IRNode:
        """Push filter through join if possible"""
        condition = filter_node.get_attribute("condition", "")
        
        # Simple heuristic: if condition refers to only one table, push it down
        if self._can_push_to_left(condition, join_node):
            # Push to left side
            left_filter = FilterIR(join_node.left, condition)
            join_node.left = left_filter
            return join_node
        elif self._can_push_to_right(condition, join_node):
            # Push to right side
            right_filter = FilterIR(join_node.right, condition)
            join_node.right = right_filter
            return join_node
        
        return filter_node
    
    def _push_through_projection(self, filter_node: FilterIR, project_node: ProjectIR) -> IRNode:
        """Push filter through projection if columns are available"""
        # Simplified: always push through projection
        new_filter = FilterIR(project_node.source, filter_node.get_attribute("condition", ""))
        project_node.source = new_filter
        return project_node
    
    def _push_through_aggregation(self, filter_node: FilterIR, aggregate_node: AggregateIR) -> IRNode:
        """Push filter through aggregation if it's a HAVING clause"""
        # For simplicity, don't push through aggregations
        return filter_node
    
    def _can_push_to_left(self, condition: str, join_node: JoinIR) -> bool:
        """Check if condition can be pushed to left side of join"""
        # Simplified implementation
        return True
    
    def _can_push_to_right(self, condition: str, join_node: JoinIR) -> bool:
        """Check if condition can be pushed to right side of join"""
        # Simplified implementation
        return False

class ProjectionElimination(OptimizationRule):
    """Eliminate unnecessary projections"""
    
    def __init__(self):
        super().__init__("Projection Elimination")
    
    def can_apply(self, node: IRNode) -> bool:
        return isinstance(node, ProjectIR)
    
    def apply(self, node: IRNode) -> Optional[IRNode]:
        if not self.can_apply(node):
            return None
        
        project_node = node
        projections = project_node.get_attribute("projections", [])
        
        # If projection is selecting all columns, eliminate it
        if len(projections) == 1 and projections[0] == "*":
            return project_node.children[0] if project_node.children else project_node
        
        return None

class ConstantFolding(OptimizationRule):
    """Fold constant expressions"""
    
    def __init__(self):
        super().__init__("Constant Folding")
    
    def can_apply(self, node: IRNode) -> bool:
        return isinstance(node, FilterIR)
    
    def apply(self, node: IRNode) -> Optional[IRNode]:
        if not self.can_apply(node):
            return None
        
        filter_node = node
        condition = filter_node.get_attribute("condition", "")
        
        # Try to evaluate constant conditions
        if self._is_constant_condition(condition):
            result = self._evaluate_condition(condition)
            if result is True:
                # Always true condition - remove filter
                return filter_node.children[0] if filter_node.children else filter_node
            elif result is False:
                # Always false condition - return empty result
                # For simplicity, keep the filter
                return filter_node
        
        return None
    
    def _is_constant_condition(self, condition: str) -> bool:
        """Check if condition contains only constants"""
        # Simplified implementation
        return any(op in condition for op in ["= true", "= false", "= 1", "= 0"])
    
    def _evaluate_condition(self, condition: str) -> Optional[bool]:
        """Evaluate constant condition"""
        if "= true" in condition or "= 1" in condition:
            return True
        elif "= false" in condition or "= 0" in condition:
            return False
        return None

class JoinReordering(OptimizationRule):
    """Reorder joins for better performance"""
    
    def __init__(self):
        super().__init__("Join Reordering")
    
    def can_apply(self, node: IRNode) -> bool:
        return isinstance(node, JoinIR)
    
    def apply(self, node: IRNode) -> Optional[IRNode]:
        if not self.can_apply(node):
            return None
        
        join_node = node
        
        # Simple heuristic: smaller tables first
        # In a real implementation, we'd use statistics
        left_size = self._estimate_table_size(join_node.left)
        right_size = self._estimate_table_size(join_node.right)
        
        if left_size > right_size:
            # Swap join order
            join_node.left, join_node.right = join_node.right, join_node.left
            return join_node
        
        return None
    
    def _estimate_table_size(self, node: IRNode) -> int:
        """Estimate table size for optimization"""
        if isinstance(node, ScanIR):
            table_name = node.get_attribute("table_name", "")
            # Simplified: use table name length as proxy for size
            return len(table_name)
        elif isinstance(node, FilterIR):
            # Filter reduces size
            return self._estimate_table_size(node.children[0]) // 2 if node.children else 1000
        else:
            return 1000  # Default size

class IndexSelection(OptimizationRule):
    """Select appropriate indexes for queries"""
    
    def __init__(self):
        super().__init__("Index Selection")
    
    def can_apply(self, node: IRNode) -> bool:
        return isinstance(node, ScanIR) or isinstance(node, FilterIR)
    
    def apply(self, node: IRNode) -> Optional[IRNode]:
        if not self.can_apply(node):
            return None
        
        # Add index hint to scan or filter operations
        if isinstance(node, ScanIR):
            table_name = node.get_attribute("table_name", "")
            if self._has_index(table_name):
                node.set_attribute("use_index", f"idx_{table_name}_primary")
        
        elif isinstance(node, FilterIR):
            condition = node.get_attribute("condition", "")
            if self._can_use_index(condition):
                node.set_attribute("use_index", True)
        
        return None
    
    def _has_index(self, table_name: str) -> bool:
        """Check if table has suitable index"""
        # Simplified: assume all tables have primary key index
        return True
    
    def _can_use_index(self, condition: str) -> bool:
        """Check if condition can use index"""
        # Simplified: check for equality on primary key
        return "id =" in condition or "pk =" in condition

class QueryOptimizer:
    """Main optimizer class that applies all optimization rules"""
    
    def __init__(self):
        self.rules: List[OptimizationRule] = [
            PredicatePushdown(),
            ProjectionElimination(),
            ConstantFolding(),
            JoinReordering(),
            IndexSelection(),
        ]
        self.optimization_stats = {
            "rules_applied": 0,
            "nodes_optimized": 0,
            "execution_time_saved": 0.0
        }
    
    def optimize(self, ir_program: IRProgram) -> IRProgram:
        """Optimize an IR program"""
        optimized_program = IRProgram()
        
        for statement in ir_program.statements:
            optimized_statement = self._optimize_node(statement)
            optimized_program.add_statement(optimized_statement)
        
        # Copy global symbols
        optimized_program.global_symbols = ir_program.global_symbols.copy()
        
        return optimized_program
    
    def _optimize_node(self, node: IRNode) -> IRNode:
        """Optimize a single IR node and its children"""
        # First optimize children
        for i, child in enumerate(node.children):
            node.children[i] = self._optimize_node(child)
        
        # Apply optimization rules
        optimized_node = node
        for rule in self.rules:
            if rule.can_apply(optimized_node):
                result = rule.apply(optimized_node)
                if result:
                    optimized_node = result
                    rule.applications += 1
                    self.optimization_stats["rules_applied"] += 1
        
        self.optimization_stats["nodes_optimized"] += 1
        return optimized_node
    
    def optimize_query(self, query_ir: IRNode) -> IRNode:
        """Optimize a single query IR node"""
        return self._optimize_node(query_ir)
    
    def add_rule(self, rule: OptimizationRule):
        """Add a custom optimization rule"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove an optimization rule by name"""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                del self.rules[i]
                return True
        return False
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        rule_stats = {}
        for rule in self.rules:
            rule_stats[rule.name] = rule.applications
        
        return {
            **self.optimization_stats,
            "rule_applications": rule_stats,
            "total_rules": len(self.rules)
        }
    
    def reset_stats(self):
        """Reset optimization statistics"""
        self.optimization_stats = {
            "rules_applied": 0,
            "nodes_optimized": 0,
            "execution_time_saved": 0.0
        }
        
        for rule in self.rules:
            rule.applications = 0
    
    def explain_optimizations(self, ir_program: IRProgram) -> List[str]:
        """Generate explanation of optimizations applied"""
        explanations = []
        
        for i, statement in enumerate(ir_program.statements):
            explanation = self._explain_node_optimizations(statement, f"Statement {i+1}")
            if explanation:
                explanations.append(explanation)
        
        return explanations
    
    def _explain_node_optimizations(self, node: IRNode, context: str) -> str:
        """Explain optimizations applied to a node"""
        optimizations = []
        
        # Check for specific optimizations
        if isinstance(node, FilterIR):
            if node.get_attribute("use_index"):
                optimizations.append("Applied index selection")
        
        elif isinstance(node, JoinIR):
            if node.get_attribute("join_type") == "inner":
                optimizations.append("Optimized join order")
        
        elif isinstance(node, ScanIR):
            if node.get_attribute("use_index"):
                optimizations.append("Using index scan")
        
        # Check children
        for child in node.children:
            child_opt = self._explain_node_optimizations(child, context)
            if child_opt:
                optimizations.append(child_opt)
        
        if optimizations:
            return f"{context}: " + ", ".join(optimizations)
        
        return ""

class CostBasedOptimizer(QueryOptimizer):
    """Cost-based optimizer using statistics"""
    
    def __init__(self):
        super().__init__()
        self.table_stats: Dict[str, Dict[str, Any]] = {}
        self.index_stats: Dict[str, Dict[str, Any]] = {}
    
    def set_table_statistics(self, table_name: str, row_count: int, avg_row_size: int):
        """Set table statistics for cost estimation"""
        self.table_stats[table_name] = {
            "row_count": row_count,
            "avg_row_size": avg_row_size,
            "estimated_size": row_count * avg_row_size
        }
    
    def set_index_statistics(self, index_name: str, cardinality: int, levels: int):
        """Set index statistics for cost estimation"""
        self.index_stats[index_name] = {
            "cardinality": cardinality,
            "levels": levels,
            "estimated_cost": levels * 10  # Simplified cost model
        }
    
    def estimate_cost(self, node: IRNode) -> float:
        """Estimate execution cost for a node"""
        if isinstance(node, ScanIR):
            return self._estimate_scan_cost(node)
        elif isinstance(node, FilterIR):
            return self._estimate_filter_cost(node)
        elif isinstance(node, JoinIR):
            return self._estimate_join_cost(node)
        elif isinstance(node, AggregateIR):
            return self._estimate_aggregate_cost(node)
        else:
            return 1.0  # Default cost
    
    def _estimate_scan_cost(self, node: ScanIR) -> float:
        """Estimate cost of table scan"""
        table_name = node.get_attribute("table_name", "")
        stats = self.table_stats.get(table_name, {"row_count": 1000, "estimated_size": 10000})
        
        if node.get_attribute("use_index"):
            # Index scan is cheaper
            return stats["row_count"] * 0.1
        
        # Full table scan
        return stats["row_count"]
    
    def _estimate_filter_cost(self, node: FilterIR) -> float:
        """Estimate cost of filter operation"""
        base_cost = self.estimate_cost(node.children[0]) if node.children else 1.0
        
        # Filter reduces result set
        selectivity = self._estimate_selectivity(node.get_attribute("condition", ""))
        return base_cost * selectivity
    
    def _estimate_join_cost(self, node: JoinIR) -> float:
        """Estimate cost of join operation"""
        left_cost = self.estimate_cost(node.left)
        right_cost = self.estimate_cost(node.right)
        
        # Nested loop join cost
        return left_cost * right_cost * 0.1  # Simplified
    
    def _estimate_aggregate_cost(self, node: AggregateIR) -> float:
        """Estimate cost of aggregation"""
        base_cost = self.estimate_cost(node.children[0]) if node.children else 1.0
        return base_cost * 1.5  # Aggregation adds overhead
    
    def _estimate_selectivity(self, condition: str) -> float:
        """Estimate selectivity of a condition"""
        # Simplified selectivity estimation
        if "=" in condition:
            return 0.1  # Equality is very selective
        elif ">" in condition or "<" in condition:
            return 0.3  # Range is moderately selective
        else:
            return 0.5  # Default selectivity