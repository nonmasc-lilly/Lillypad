import enum;
import typing;
"""
We must lex the following tokens:
- typedef
- struct
- label
- let
- set
- call
- goto
- return
- syscall
- store
- add
- subtract
- reference
- dereference
- int
- :
- .
- {
- }
- identifier
- integer
"""

class TokenType(enum.Enum):
    NULL        =    0;
    TYPEDEF     =    1;
    STRUCT      =    2;
    LABEL       =    3;
    LET         =    4;
    SET         =    5;
    CALL        =    6;
    GOTO        =    7;
    RETURN      =    8;
    IF          =    9;
    SYSCALL     =   10;
    STORE       =   11;
    ADD         =   12;
    SUBTRACT    =   13;
    REFERENCE   =   14;
    DEREFERENCE =   15;
    INT         =   16;
    COLON       =   17;
    DOT         =   18;
    OPEN_CURLY  =   19;
    CLOSE_CURLY =   20;
    IDENTIFIER  =   21;
    INTEGER     =   22;

class Token:
    def __init__(self, type: TokenType, value: str, line: str) -> None:
        self.type: TokenType = type;
        self.value: str = value;
        self.line: str = line;
    def __repr__(self) -> str:
        return f"ln[{self.line}]: {self.type.name} : {self.value}"

def WHITESPACE(a: str) -> bool:
    return a == ' ' or a == '\n' or a == '\r' or a == '\t';

# TODO both token_from functions
def token_from_buf(buf: str) -> TokenType:
    match buf:
        case "": return TokenType.NULL;
        case "typedef":     return TokenType.TYPEDEF;
        case "struct":      return TokenType.STRUCT;
        case "label":       return TokenType.LABEL;
        case "let":         return TokenType.LET;
        case "set":         return TokenType.SET;
        case "call":        return TokenType.CALL;
        case "goto":        return TokenType.GOTO;
        case "if":          return TokenType.IF;
        case "syscall":     return TokenType.SYSCALL;
        case "store":       return TokenType.STORE;
        case "add":         return TokenType.ADD;
        case "subtract":    return TokenType.SUBTRACT;
        case "reference":   return TokenType.REFERENCE;
        case "dereference": return TokenType.DEREFERENCE;
        case "int":         return TokenType.INT;
        case _:
            try:
                if buf[:2] == '0x': x = int(buf[2:],16);
                else: x = int(buf,10);
                return TokenType.INTEGER;
            except ValueError:
                return TokenType.IDENTIFIER;
def token_from_char(string: str, offset: int) -> TokenType:
    match string[offset]:
        case '.':   return TokenType.DOT;
        case ':':   return TokenType.COLON;
        case '{':   return TokenType.OPEN_CURLY;
        case '}':   return TokenType.CLOSE_CURLY;
        case _:     return TokenType.NULL;
def token_has_value(type: TokenType) -> bool:
    match type:
        case TokenType.INTEGER: return True;
        case TokenType.IDENTIFIER: return True;
def lex_string(string: str) -> list[Token]:
    ret: list[Token] = [];
    buf: str = "";
    line = 0;
    for idx, i in enumerate(string):
        if i == '\n': line += 1;
        if WHITESPACE(i):
            if token_from_buf(buf) != TokenType.NULL: ret.append(Token(token_from_buf(buf), buf if token_has_value(token_from_buf(buf)) else "", line));
            buf = "";
            continue;
        if token_from_char(string, idx) != TokenType.NULL:
            if token_from_buf(buf) != TokenType.NULL: ret.append(Token(token_from_buf(buf), buf if token_has_value(token_from_buf(buf)) else "", line));
            ret.append(Token(token_from_char(string, idx), "", line));
            buf = "";
            continue;
        buf += i;
    if token_from_buf(buf) != TokenType.NULL: ret.append(Token(token_from_buf(buf), buf if token_has_value(token_from_buf(buf)) else "", line));
    buf = "";
    return ret;