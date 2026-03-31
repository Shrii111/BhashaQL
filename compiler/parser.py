from typing import List, Optional
from .tokens import Token, TokenType
from .ast_nodes import *

class ParseError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(f"Parse Error at line {token.line}, column {token.column}: {message}")

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def error(self, token: Token, message: str):
        raise ParseError(token, message)
    
    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF
    
    def peek(self) -> Token:
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1]
    
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type
    
    def match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        
        token = self.peek() if self.current < len(self.tokens) else self.tokens[-1]
        self.error(token, message)
    
    def skip_semicolon(self):
        while self.match(TokenType.SEMICOLON):
            pass
    
    def parse(self) -> Program:
        statements = []
        
        while not self.is_at_end():
            statements.append(self.statement())
            self.skip_semicolon()
        
        return Program(statements)
    
    def statement(self) -> Statement:
        if self.match(TokenType.BANAYE):
            return self.create_table_statement()
        elif self.match(TokenType.HATAYE):
            return self.drop_table_statement()
        elif self.match(TokenType.BADLIYE):
            return self.alter_table_statement()
        elif self.match(TokenType.LAYE):
            return self.select_statement()
        elif self.match(TokenType.DAALEN):
            return self.insert_statement()
        elif self.match(TokenType.BADLEIN):
            return self.update_statement()
        elif self.match(TokenType.MITAYEIN):
            return self.delete_statement()
        elif self.match(TokenType.DEEJAYE):
            return self.grant_statement()
        elif self.match(TokenType.WAPAS):
            return self.revoke_statement()
        else:
            token = self.peek()
            self.error(token, f"Expected statement, got '{token.value}'")
    
    def create_table_statement(self) -> CreateTableStatement:
        self.consume(TokenType.TABLE, "Expected 'table' after 'banaye'")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name")
        self.consume(TokenType.LPAREN, "Expected '(' after table name")
        
        columns = []
        while not self.check(TokenType.RPAREN) and not self.is_at_end():
            columns.append(self.column_definition())
            if not self.match(TokenType.COMMA):
                break
        
        self.consume(TokenType.RPAREN, "Expected ')' after column definitions")
        return CreateTableStatement(table_name, columns)
    
    def drop_table_statement(self) -> DropTableStatement:
        self.consume(TokenType.TABLE, "Expected 'table' after 'hataye'")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name")
        return DropTableStatement(table_name)
    
    def alter_table_statement(self) -> AlterTableStatement:
        self.consume(TokenType.TABLE, "Expected 'table' after 'badliye'")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name")
        action = self.consume(TokenType.ADD, "Expected 'add' after table name")
        column_def = self.column_definition()
        return AlterTableStatement(table_name, action, column_def)
    
    def select_statement(self) -> SelectStatement:
        select_list = self.select_list()
        self.consume(TokenType.SE, "Expected 'se' after select list")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name")
        
        where_clause = None
        if self.match(TokenType.JAHAN):
            where_clause = WhereClause(self.expression())
        
        group_clause = None
        if self.match(TokenType.GROUP):
            self.consume(TokenType.DWARA, "Expected 'dwara' after 'group'")
            group_columns = []
            while not self.is_at_end() and not self.check(TokenType.KRAM) and not self.check(TokenType.SEMICOLON):
                group_columns.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
            group_clause = GroupClause(group_columns)
        
        order_clause = None
        if self.match(TokenType.KRAM):
            self.consume(TokenType.DWARA, "Expected 'dwara' after 'kram'")
            order_columns = []
            while not self.is_at_end() and not self.check(TokenType.SEMICOLON):
                column = self.expression()
                direction = None
                if self.match(TokenType.DESC) or self.match(TokenType.ASC):
                    direction = self.previous()
                order_columns.append(OrderColumn(column, direction))
                if not self.match(TokenType.COMMA):
                    break
            order_clause = OrderClause(order_columns)
        
        return SelectStatement(select_list, table_name, where_clause, group_clause, order_clause)
    
    def insert_statement(self) -> InsertStatement:
        self.consume(TokenType.MEIN, "Expected 'mein' after 'daalen'")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name")
        
        columns = None
        if self.match(TokenType.LPAREN):
            columns = []
            while not self.check(TokenType.RPAREN) and not self.is_at_end():
                columns.append(self.consume(TokenType.IDENTIFIER, "Expected column name"))
                if not self.match(TokenType.COMMA):
                    break
            self.consume(TokenType.RPAREN, "Expected ')' after column list")
        
        self.consume(TokenType.VALUES, "Expected 'values'")
        self.consume(TokenType.LPAREN, "Expected '(' before values")
        
        values = []
        while not self.check(TokenType.RPAREN) and not self.is_at_end():
            values.append(self.expression())
            if not self.match(TokenType.COMMA):
                break
        
        self.consume(TokenType.RPAREN, "Expected ')' after values")
        return InsertStatement(table_name, columns, values)
    
    def update_statement(self) -> UpdateStatement:
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name")
        self.consume(TokenType.SET, "Expected 'set'")
        self.consume(TokenType.KAREIN, "Expected 'karein'")
        
        assignments = []
        while not self.is_at_end() and not self.check(TokenType.JAHAN) and not self.check(TokenType.SEMICOLON):
            column = self.consume(TokenType.IDENTIFIER, "Expected column name")
            self.consume(TokenType.ASSIGN, "Expected '='")
            value = self.expression()
            assignments.append(Assignment(column, value))
            if not self.match(TokenType.COMMA):
                break
        
        where_clause = None
        if self.match(TokenType.JAHAN):
            where_clause = WhereClause(self.expression())
        
        return UpdateStatement(table_name, assignments, where_clause)
    
    def delete_statement(self) -> DeleteStatement:
        self.consume(TokenType.SE, "Expected 'se' after 'mitayein'")
        table_name = self.consume(TokenType.IDENTIFIER, "Expected table name")
        
        where_clause = None
        if self.match(TokenType.JAHAN):
            where_clause = WhereClause(self.expression())
        
        return DeleteStatement(table_name, where_clause)
    
    def grant_statement(self) -> GrantStatement:
        privileges = []
        while not self.check(TokenType.ON) and not self.is_at_end():
            privileges.append(self.consume(TokenType.IDENTIFIER, "Expected privilege"))
            if not self.match(TokenType.COMMA):
                break
        
        self.consume(TokenType.ON, "Expected 'on'")
        on_table = self.consume(TokenType.IDENTIFIER, "Expected table name")
        self.consume(TokenType.TO, "Expected 'to'")
        to_user = self.consume(TokenType.IDENTIFIER, "Expected user name")
        
        return GrantStatement(privileges, on_table, to_user)
    
    def revoke_statement(self) -> RevokeStatement:
        privileges = []
        while not self.check(TokenType.ON) and not self.is_at_end():
            privileges.append(self.consume(TokenType.IDENTIFIER, "Expected privilege"))
            if not self.match(TokenType.COMMA):
                break
        
        self.consume(TokenType.ON, "Expected 'on'")
        on_table = self.consume(TokenType.IDENTIFIER, "Expected table name")
        self.consume(TokenType.FROM, "Expected 'from'")
        from_user = self.consume(TokenType.IDENTIFIER, "Expected user name")
        
        return RevokeStatement(privileges, on_table, from_user)
    
    def select_list(self) -> List[Expression]:
        select_list = []
        
        if self.match(TokenType.ASTERISK):
            select_list.append(AllColumns(self.previous()))
        else:
            select_list.append(self.expression())
            while self.match(TokenType.COMMA):
                select_list.append(self.expression())
        
        return select_list
    
    def column_definition(self) -> ColumnDefinition:
        column_name = self.consume(TokenType.IDENTIFIER, "Expected column name")
        if self.match(TokenType.NUMBER_TYPE, TokenType.TEXT_TYPE):
            data_type = self.previous()
        else:
            token = self.peek()
            self.error(token, "Expected data type (number or text)")
        return ColumnDefinition(column_name, data_type)
    
    def expression(self) -> Expression:
        return self.logical_or()
    
    def logical_or(self) -> Expression:
        expr = self.logical_and()
        
        while self.match(TokenType.YA):
            operator = self.previous()
            right = self.logical_and()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def logical_and(self) -> Expression:
        expr = self.equality()
        
        while self.match(TokenType.AUR):
            operator = self.previous()
            right = self.equality()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def equality(self) -> Expression:
        expr = self.comparison()
        
        while self.match(TokenType.EQ, TokenType.NEQ):
            operator = self.previous()
            right = self.comparison()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def comparison(self) -> Expression:
        expr = self.term()
        
        while self.match(TokenType.GT, TokenType.GTE, TokenType.LT, TokenType.LTE):
            operator = self.previous()
            right = self.term()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def term(self) -> Expression:
        expr = self.factor()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def factor(self) -> Expression:
        expr = self.unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE):
            operator = self.previous()
            right = self.unary()
            expr = BinaryExpression(expr, operator, right)
        
        return expr
    
    def unary(self) -> Expression:
        if self.match(TokenType.NAHIN, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return UnaryExpression(operator, right)
        
        return self.primary()
    
    def primary(self) -> Expression:
        # Literals
        if self.match(TokenType.NUMBER):
            return Literal(self.previous())
        
        if self.match(TokenType.STRING):
            return Literal(self.previous())
        
        # Identifiers and Column References
        if self.match(TokenType.IDENTIFIER):
            token = self.previous()
            # Check if it's a function call
            if self.match(TokenType.LPAREN):
                args = []
                while not self.check(TokenType.RPAREN) and not self.is_at_end():
                    args.append(self.expression())
                    if not self.match(TokenType.COMMA):
                        break
                self.consume(TokenType.RPAREN, "Expected ')' after function arguments")
                return FunctionCall(token, args)
            else:
                return ColumnReference(token)
        
        # Parenthesized expressions
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        
        # Aggregate functions
        if self.match(TokenType.COUNT, TokenType.SUM, TokenType.AVG, TokenType.MAX, TokenType.MIN):
            function_name = self.previous()
            self.consume(TokenType.LPAREN, "Expected '(' after function name")
            
            args = []
            if self.match(TokenType.ASTERISK):
                args.append(AllColumns(self.previous()))
            else:
                args.append(self.expression())
            
            self.consume(TokenType.RPAREN, "Expected ')' after function arguments")
            return FunctionCall(function_name, args)
        
        token = self.peek()
        self.error(token, f"Expected expression, got '{token.value}'")