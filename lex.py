from enum import Enum

class TokenType(Enum):
    IDEN            =  0;
    INTEGER_CONST   =  1;
    STRING_CONST    =  2;
    OPEN_PAREN      =  3;
    CLOSE_PAREN     =  4;
    WHILE           =  5;
    CALL            =  6;
    POP             =  7;
    END             =  8;
    IF              =  9;
    ELSE            = 10;
    LET             = 11;
    HALT            = 12;
    ADD             = 13;
    SUB             = 14;
    PRC             = 15;
    INP             = 16;
    POINTER         = 17;

def optok(string: str, off: int) -> TokenType:
    match string[off]:
        case '!': return TokenType.CALL;
        case '.': return TokenType.POP;
        case '+': return TokenType.ADD;
        case '-': return TokenType.SUB;
        case '(': return TokenType.OPEN_PAREN;
        case ')': return TokenType.CLOSE_PAREN;
        case '*': return TokenType.POINTER;
        case _:   return None;
def tokfstr(string: str) -> TokenType:
    if len(string) == 0: return None;
    match string:
        case "while":   return TokenType.WHILE;
        case "end":     return TokenType.END;
        case "if":      return TokenType.IF;
        case "else":    return TokenType.ELSE;
        case "let":     return TokenType.LET;
        case "hlt":     return TokenType.HALT;
        case "prc":     return TokenType.PRC;
        case "inp":     return TokenType.INP;
        case _:
            try:
                int(string);
                return TokenType.INTEGER_CONST;
            except ValueError:
                return TokenType.IDEN;


class Token:
    def __init__(self, type: TokenType, value: str):
        self.type = type;
        self.value = value;
    def __repr__(self):
        return f"({self.type.name} , {self.value})";

def lex_string(string: str) -> list[Token]:
    tokens: list[Token] = None;
    i:      int         = None;
    buf:    str         = None;
    buf = "";
    tokens = [];
    i = 0;
    while i < len(string):
        if string[i] == '"':
            if tokfstr(buf) != None:
                tokens.append(Token(tokfstr(buf), buf));
                buf = "";
            i += 1;
            buf = "";
            while i < len(string) and string[i] != '"':
                if string[i] == '\\':
                    tmp: str = "";
                    j:   int = i;
                    while not string[j].isspace():
                        tmp += string[j];
                        j+=1;
                    try:
                        int(tmp);
                        buf += chr(int(tmp));
                    except ValueError:
                        i+=1;
                        buf += string[i];
                buf += string[i];
                i += 1;
            tokens.append(Token(TokenType.STRING_CONST, buf));
            buf = "";
            i+=1;
            continue;
        if string[i] == '/' and string[i+1] == '*':
            while not(string[i] == '*' and string[i+1] == '/'):
                i+=1;
            i+=2;
            continue;
        if string[i] == ' ' or string[i] == '\n' or string[i] == '\t' or string[i] == '\r':
            if tokfstr(buf) != None:
                tokens.append(Token(tokfstr(buf), buf));
                buf = "";
            i+=1;
            continue;
        if optok(string, i) != None:
            if tokfstr(buf) != None:
                tokens.append(Token(tokfstr(buf), buf));
                buf = "";
            tokens.append(Token(optok(string, i), None));
            i+=1;
            continue;
        buf += string[i];
        i += 1;
    return tokens;