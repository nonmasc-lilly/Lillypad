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
    DEFINE          = 18;
    DUPLICATE       = 19;
    REG8            = 20;
    REGX            = 30;

def optok(string: str, off: int) -> TokenType:
    match string[off]:
        case '!': return TokenType.CALL;
        case '.': return TokenType.POP;
        case '+': return TokenType.ADD;
        case '-': return TokenType.SUB;
        case '(': return TokenType.OPEN_PAREN;
        case ')': return TokenType.CLOSE_PAREN;
        case '*': return TokenType.POINTER;
        case '#': return TokenType.DEFINE;
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
        case "dup":     return TokenType.DUPLICATE;
        case "r8":      return TokenType.REG8;
        case "rx":      return TokenType.REGX;
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
            tokens.append(Token(optok(string, i), None, line));
            i+=1;
            continue;
        buf += string[i];
        i += 1;
    if tokfstr(buf) != None:
        tokens.append(Token(tokfstr(buf), buf, line));
        buf = "";
    return tokens;