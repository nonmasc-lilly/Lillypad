from enum import Enum

class TokenType(Enum):
    IDEN            =  0;
    INTEGER_CONST   =  1;
    STRING_CONST    =  2;
    OPEN_PAREN      =  3;
    CLOSE_PAREN     =  4;
    WHILE           =  5;
    CALL            =  6;
    END             =  7;
    IF              =  8;
    ELSE            =  9;
    LET             = 10;
    HALT            = 11;
    ADD             = 12;
    SUB             = 13;
    PRC             = 14;
    INP             = 15;
    POINTER         = 16;
    DEFINE          = 17;
    REG8            = 18;
    REGX            = 19;
    COMMA           = 20;
    STORE           = 21;
    EQUAL           = 22;
    GREATER         = 23;
    NOT             = 24;
    AND             = 25;
    OR              = 26;
    CONST           = 27;
    REFERENCE       = 28;
    CAST            = 29;
    INT             = 30;

def optok(string: str, off: int) -> TokenType | tuple[TokenType, int]:
    match string[off]:
        case '!': return TokenType.CALL;
        case '+': return TokenType.ADD;
        case '-': return TokenType.SUB;
        case '<':
            if string[off+1] == '-': return (TokenType.CAST, 2);
            return None;
        case '(': return TokenType.OPEN_PAREN;
        case ')': return TokenType.CLOSE_PAREN;
        case '*': return TokenType.POINTER;
        case '&': return TokenType.REFERENCE;
        case '#': return TokenType.DEFINE;
        case ',': return TokenType.COMMA;
        case '=': return TokenType.STORE;
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
        case "r8":      return TokenType.REG8;
        case "rx":      return TokenType.REGX;
        case "store":   return TokenType.STORE;
        case "equ":     return TokenType.EQUAL;
        case "grt":     return TokenType.GREATER;
        case "not":     return TokenType.NOT;
        case "and":     return TokenType.AND;
        case "or":      return TokenType.OR;
        case "const":   return TokenType.CONST;
        case "int":     return TokenType.INT;
        case _:
            try:
                int(string);
                return TokenType.INTEGER_CONST;
            except ValueError:
                return TokenType.IDEN;


class Token:
    def __init__(self, type: TokenType, value: str, line: int):
        self.node_type = type;
        self.value = value;
        self.line = line;
    def __repr__(self):
        return f"({self.node_type.name} , {self.value}) on line: {self.line}";

def lex_string(string: str) -> list[Token]:
    tokens: list[Token] = None;
    i:      int         = None;
    buf:    str         = None;
    line:   int         = None;
    buf = "";
    tokens = [];
    i = 0;
    line = 0;
    while i < len(string):
        if string[i] == '\n':
            line += 1;
        if string[i] == '"':
            if tokfstr(buf) != None:
                tokens.append(Token(tokfstr(buf), buf, line));
                buf = "";
            i += 1;
            buf = "";
            while i < len(string) and string[i] != '"':
                if string[i] == '\n': line += 1;
                if string[i] == '\\':
                    tmp: str = "";
                    j:   int = i+1;
                    while not (string[j].isspace() or string[j] == '"'):
                        tmp += string[j];
                        j+=1;
                    try:
                        print(tmp)
                        int(tmp);
                        buf += chr(int(tmp));
                        i = j
                        print(string[i]);
                    except ValueError:
                        i+=1;
                        buf += string[i];
                    continue;
                buf += string[i];
                i += 1;
            tokens.append(Token(TokenType.STRING_CONST, buf, line));
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
                tokens.append(Token(tokfstr(buf), buf, line));
                buf = "";
            i+=1;
            continue;
        if optok(string, i) != None:
            if tokfstr(buf) != None:
                tokens.append(Token(tokfstr(buf), buf, line));
                buf = "";
            if type(optok(string, i)) != tuple:
                tokens.append(Token(optok(string, i), None, line));
                i += 1;
            else:
                tokens.append(Token(optok(string, i)[0], None, line));
                i += optok(string, i)[1];
            continue;
        buf += string[i];
        i += 1;
    if tokfstr(buf) != None:
        tokens.append(Token(tokfstr(buf), buf, line));
        buf = "";
    return tokens;