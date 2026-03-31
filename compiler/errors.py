from typing import Optional, List
from .tokens import Token

class CompilerError(Exception):
    """Base class for all compiler errors"""
    
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(self.format_error())
    
    def format_error(self) -> str:
        return f"Error at line {self.token.line}, column {self.token.column}: {self.message}"
    
    def get_line_info(self) -> str:
        return f"Line {self.token.line}, Column {self.token.column}"

class LexerError(CompilerError):
    """Lexical analysis errors"""
    
    def __init__(self, token: Token, message: str):
        super().__init__(token, f"Lexer Error: {message}")

class ParseError(CompilerError):
    """Parsing errors"""
    
    def __init__(self, token: Token, message: str):
        super().__init__(token, f"Parse Error: {message}")

class SemanticError(CompilerError):
    """Semantic analysis errors"""
    
    def __init__(self, token: Token, message: str):
        super().__init__(token, f"Semantic Error: {message}")

class TypeError(CompilerError):
    """Type checking errors"""
    
    def __init__(self, token: Token, message: str):
        super().__init__(token, f"Type Error: {message}")

class RuntimeError(CompilerError):
    """Runtime execution errors"""
    
    def __init__(self, token: Token, message: str):
        super().__init__(token, f"Runtime Error: {message}")

class ErrorCollector:
    """Collects and manages compiler errors"""
    
    def __init__(self):
        self.errors: List[CompilerError] = []
        self.warnings: List[str] = []
    
    def add_error(self, error: CompilerError):
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        self.warnings.append(warning)
    
    def has_errors(self) -> bool:
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0
    
    def get_errors(self) -> List[CompilerError]:
        return self.errors
    
    def get_warnings(self) -> List[str]:
        return self.warnings
    
    def clear(self):
        self.errors.clear()
        self.warnings.clear()
    
    def format_all_errors(self) -> str:
        if not self.has_errors():
            return "No errors found."
        
        error_messages = []
        for error in self.errors:
            error_messages.append(str(error))
        
        return "\n".join(error_messages)
    
    def format_all_warnings(self) -> str:
        if not self.has_warnings():
            return "No warnings."
        
        warning_messages = []
        for i, warning in enumerate(self.warnings, 1):
            warning_messages.append(f"Warning {i}: {warning}")
        
        return "\n".join(warning_messages)
    
    def get_summary(self) -> str:
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        
        if error_count == 0 and warning_count == 0:
            return "Compilation successful with no errors or warnings."
        elif error_count == 0:
            return f"Compilation successful with {warning_count} warning(s)."
        else:
            return f"Compilation failed with {error_count} error(s) and {warning_count} warning(s)."
    
    def __str__(self):
        return self.get_summary()

class ErrorRecovery:
    """Error recovery strategies for the compiler"""
    
    @staticmethod
    def panic_mode_recover(parser, sync_tokens: List[type]):
        """Panic mode error recovery - skip tokens until a synchronization point"""
        while not parser.is_at_end():
            current_token = parser.peek()
            
            # Check if current token is a synchronization point
            for sync_token in sync_tokens:
                if current_token.type == sync_token:
                    return
            
            # Skip to next token
            parser.advance()
    
    @staticmethod
    def recover_from_statement_error(parser):
        """Recover from statement-level errors by finding the next semicolon or statement start"""
        while not parser.is_at_end():
            current_token = parser.peek()
            
            # Synchronization points: semicolon or statement start tokens
            if current_token.type in [
                # End of statement
                TokenType.SEMICOLON,
                # Start of new statements
                TokenType.BANAYE, TokenType.HATAYE, TokenType.BADLIYE,
                TokenType.LAYE, TokenType.DAALEN, TokenType.BADLEIN,
                TokenType.MITAYEIN, TokenType.DEEJAYE, TokenType.WAPAS,
                TokenType.JAHAN, TokenType.KRAM, TokenType.GROUP
            ]:
                return
            
            parser.advance()
    
    @staticmethod
    def recover_from_expression_error(parser):
        """Recover from expression errors by finding expression boundaries"""
        while not parser.is_at_end():
            current_token = parser.peek()
            
            # Expression boundaries
            if current_token.type in [
                TokenType.SEMICOLON, TokenType.COMMA, TokenType.RPAREN,
                TokenType.JAHAN, TokenType.KRAM, TokenType.GROUP
            ]:
                return
            
            parser.advance()

# Predefined error messages
class ErrorMessages:
    """Standardized error messages"""
    
    # Lexer errors
    UNEXPECTED_CHARACTER = "Unexpected character '{char}'"
    UNTERMINATED_STRING = "Unterminated string literal"
    INVALID_NUMBER = "Invalid number format"
    
    # Parser errors
    EXPECTED_TOKEN = "Expected '{expected}' but got '{actual}'"
    UNEXPECTED_EOF = "Unexpected end of input"
    INVALID_SYNTAX = "Invalid syntax"
    
    # Semantic errors
    TABLE_NOT_FOUND = "Table '{table_name}' does not exist"
    TABLE_ALREADY_EXISTS = "Table '{table_name}' already exists"
    COLUMN_NOT_FOUND = "Column '{column_name}' does not exist in table '{table_name}'"
    COLUMN_ALREADY_EXISTS = "Column '{column_name}' already exists in table '{table_name}'"
    FUNCTION_NOT_FOUND = "Function '{function_name}' does not exist"
    INVALID_ARGUMENT_COUNT = "Function '{function_name}' expects {expected} arguments, got {actual}"
    
    # Type errors
    TYPE_MISMATCH = "Type mismatch: expected {expected}, got {actual}"
    INCOMPATIBLE_TYPES = "Cannot compare {type1} with {type2}"
    INVALID_OPERATION = "Invalid operation: {operation} on {type}"
    
    # Runtime errors
    DATABASE_ERROR = "Database operation failed: {error}"
    EXECUTION_FAILED = "Query execution failed: {error}"

def create_lexer_error(token: Token, message: str) -> LexerError:
    """Create a lexer error with standardized formatting"""
    return LexerError(token, message)

def create_parse_error(token: Token, message: str) -> ParseError:
    """Create a parse error with standardized formatting"""
    return ParseError(token, message)

def create_semantic_error(token: Token, message: str) -> SemanticError:
    """Create a semantic error with standardized formatting"""
    return SemanticError(token, message)

def create_type_error(token: Token, message: str) -> TypeError:
    """Create a type error with standardized formatting"""
    return TypeError(token, message)

def create_runtime_error(token: Token, message: str) -> RuntimeError:
    """Create a runtime error with standardized formatting"""
    return RuntimeError(token, message)