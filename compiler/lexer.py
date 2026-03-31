import re
from typing import List, Iterator
from .tokens import Token, TokenType, KEYWORDS

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.text else None
    
    def error(self, message: str):
        raise SyntaxError(f"Lexer Error at line {self.line}, column {self.column}: {message}")
    
    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def peek(self, offset: int = 1) -> str:
        peek_pos = self.pos + offset
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        if self.current_char == '-':
            if self.peek() == '-':
                while self.current_char and self.current_char != '\n':
                    self.advance()
    
    def read_number(self) -> Token:
        start_line, start_col = self.line, self.column
        result = ''
        
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        
        if '.' in result:
            return Token(TokenType.NUMBER, float(result), start_line, start_col)
        else:
            return Token(TokenType.NUMBER, int(result), start_line, start_col)
    
    def read_string(self) -> Token:
        start_line, start_col = self.line, self.column
        quote_char = self.current_char
        self.advance()  # Skip opening quote
        
        result = ''
        while self.current_char and self.current_char != quote_char:
            if self.current_char == '\\':
                self.advance()
                if self.current_char:
                    result += self.current_char
                    self.advance()
            else:
                result += self.current_char
                self.advance()
        
        if self.current_char != quote_char:
            self.error(f"Unterminated string literal")
        
        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, result, start_line, start_col)
    
    def read_identifier(self) -> Token:
        start_line, start_col = self.line, self.column
        result = ''
        
        while (self.current_char and 
               (self.current_char.isalnum() or self.current_char == '_')):
            result += self.current_char
            self.advance()
        
        # Check if it's a keyword
        token_type = KEYWORDS.get(result.lower(), TokenType.IDENTIFIER)
        return Token(token_type, result, start_line, start_col)
    
    def get_next_token(self) -> Token:
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char == '-' and self.peek() == '-':
                self.skip_comment()
                continue
            
            # Numbers
            if self.current_char.isdigit():
                return self.read_number()
            
            # Strings
            if self.current_char in ['"', "'"]:
                return self.read_string()
            
            # Identifiers and Keywords
            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_identifier()
            
            # Two-character operators
            if self.current_char == '=' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.EQ, '==', self.line, self.column - 2)
            
            if self.current_char == '!' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.NEQ, '!=', self.line, self.column - 2)
            
            if self.current_char == '<' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.LTE, '<=', self.line, self.column - 2)
            
            if self.current_char == '>' and self.peek() == '=':
                self.advance()
                self.advance()
                return Token(TokenType.GTE, '>=', self.line, self.column - 2)
            
            # Single-character tokens
            single_char_tokens = {
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                ',': TokenType.COMMA,
                ';': TokenType.SEMICOLON,
                '*': TokenType.ASTERISK,
                '.': TokenType.DOT,
                '=': TokenType.ASSIGN,
                '<': TokenType.LT,
                '>': TokenType.GT,
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '/': TokenType.DIVIDE,
            }
            
            if self.current_char in single_char_tokens:
                token_type = single_char_tokens[self.current_char]
                token = Token(token_type, self.current_char, self.line, self.column)
                self.advance()
                return token
            
            self.error(f"Unexpected character: '{self.current_char}'")
        
        return Token(TokenType.EOF, None, self.line, self.column)
    
    def tokenize(self) -> List[Token]:
        tokens = []
        token = self.get_next_token()
        
        while token.type != TokenType.EOF:
            tokens.append(token)
            token = self.get_next_token()
        
        tokens.append(token)  # Add EOF token
        return tokens