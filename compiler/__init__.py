"""
BhashaQL Compiler Package
A complete compiler implementation for Hinglish SQL language
"""

__version__ = "1.0.0"
__author__ = "BhashaQL Team"
__description__ = "A Hinglish SQL Compiler with complete pipeline"

from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer
from .optimizer import QueryOptimizer
from .codegen import CodeGenerator
from .errors import *
from .tokens import *
from .ast_nodes import *
from .symbol_table import *
from .ir import *

__all__ = [
    'Lexer', 'Parser', 'SemanticAnalyzer', 'QueryOptimizer', 'CodeGenerator',
    'Token', 'TokenType', 'KEYWORDS',
    'ASTNode', 'Statement', 'Expression',
    'SymbolTable', 'DataType', 'SymbolType',
    'IRNode', 'IRProgram', 'IROperation',
    'CompilerError', 'LexerError', 'ParseError', 'SemanticError'
]