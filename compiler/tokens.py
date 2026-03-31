from enum import Enum, auto
from typing import Dict

class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()
    
    # DDL Keywords
    BANAYE = auto()      # CREATE
    HATAYE = auto()      # DROP
    BADLIYE = auto()     # ALTER
    TABLE = auto()
    COLUMN = auto()
    ADD = auto()
    
    # DQL Keywords
    LAYE = auto()        # SELECT
    SE = auto()          # FROM
    JAHAN = auto()       # WHERE
    KRAM = auto()        # ORDER
    DWARA = auto()       # BY
    GROUP = auto()
    COUNT = auto()
    SUM = auto()
    AVG = auto()
    MAX = auto()
    MIN = auto()
    
    # DML Keywords
    DAALEN = auto()      # INSERT
    MEIN = auto()        # INTO
    VALUES = auto()
    BADLEIN = auto()     # UPDATE
    SET = auto()
    KAREIN = auto()
    MITAYEIN = auto()    # ERASE
    
    # DCL Keywords
    DEEJAYE = auto()     # GRANT
    WAPAS = auto()       # REVOKE
    LIJIYE = auto()
    TO = auto()
    ON = auto()
    FROM = auto()
    
    # Data Types
    NUMBER_TYPE = auto()  # number
    TEXT_TYPE = auto()     # text
    
    # Operators
    ASSIGN = auto()       # =
    EQ = auto()           # ==
    NEQ = auto()          # !=
    LT = auto()           # <
    GT = auto()           # >
    LTE = auto()          # <=
    GTE = auto()          # >=
    PLUS = auto()         # +
    MINUS = auto()        # -
    MULTIPLY = auto()     # *
    DIVIDE = auto()       # /
    
    # Logical Operators
    AUR = auto()          # AND
    YA = auto()           # OR
    NAHIN = auto()        # NOT
    
    # Special Symbols
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    COMMA = auto()        # ,
    SEMICOLON = auto()    # ;
    ASTERISK = auto()     # *
    DOT = auto()          # .
    
    # Special
    EOF = auto()
    NEWLINE = auto()

# Hinglish Keyword Mapping
KEYWORDS: Dict[str, TokenType] = {
    # DDL
    'banaye': TokenType.BANAYE,
    'hataye': TokenType.HATAYE,
    'badliye': TokenType.BADLIYE,
    'table': TokenType.TABLE,
    'column': TokenType.COLUMN,
    'add': TokenType.ADD,
    
    # DQL
    'laye': TokenType.LAYE,
    'se': TokenType.SE,
    'jahan': TokenType.JAHAN,
    'kram': TokenType.KRAM,
    'dwara': TokenType.DWARA,
    'group': TokenType.GROUP,
    'count': TokenType.COUNT,
    'sum': TokenType.SUM,
    'avg': TokenType.AVG,
    'max': TokenType.MAX,
    'min': TokenType.MIN,
    
    # DML
    'daalen': TokenType.DAALEN,
    'mein': TokenType.MEIN,
    'values': TokenType.VALUES,
    'badlein': TokenType.BADLEIN,
    'set': TokenType.SET,
    'karein': TokenType.KAREIN,
    'mitayein': TokenType.MITAYEIN,
    
    # DCL
    'deejaye': TokenType.DEEJAYE,
    'wapas': TokenType.WAPAS,
    'lijiye': TokenType.LIJIYE,
    'to': TokenType.TO,
    'on': TokenType.ON,
    'from': TokenType.FROM,
    
    # Data Types
    'number': TokenType.NUMBER_TYPE,
    'text': TokenType.TEXT_TYPE,
    
    # Logical
    'aur': TokenType.AUR,
    'ya': TokenType.YA,
    'nahin': TokenType.NAHIN,
}

class Token:
    def __init__(self, type: TokenType, value: str = None, line: int = 1, column: int = 1):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        if self.value:
            return f'Token({self.type}, {self.value}, line={self.line}, col={self.column})'
        return f'Token({self.type}, line={self.line}, col={self.column})'
    
    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return self.type == other.type and self.value == other.value