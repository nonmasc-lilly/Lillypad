import typing;
import enum;
import lex;

class NodeType(enum.Enum):
    NULL            =   0;
    ROOT            =   1;
    TYPEDEF         =   2;
    STRUCT          =   3;
    LABEL           =   4;
    RESERVE         =   5;
    SET             =   6;
    STORE           =   7;
    COMMAND         =   8;
    TYPE            =   9;
    STRUCT_TYPE     =  10
    EXPRESSION      =  11;
    ACCESS          =  12;
    ADD             =  13;
    SUBTRACT        =  14;
    REFERENCE       =  15;
    DEREFERENCE     =  16;
    INTEGER         =  17;
    IDENTIFIER      =  18;

class Node:
    def __init__(self, type: NodeType, value: str = "") -> None:
        self.type: NodeType       = type;
        self.value: str           = str;
        self.children: list[Node] = [];
    def add_child(self, child) -> None:
        self.children.append(child);

def Node_NULL() -> tuple[int,Node]: return (0, Node(NodeType.NULL));

def ASSERT(cond: bool, string: str) -> None:
    if not cond:
        print(string);
        exit(1);

### STATEMENTS

def parse_typedef(lex_list: list[lex.Token], lex_idx: int) -> tuple[int, Node]:
    if lex_list[lex_idx] != lex.TokenType.TYPEDEF: return Node_NULL();
    ASSERT(lex_list[lex_idx+1].type == lex.TokenType.IDENTIFIER, f"Expected identifier at TOKEN: {lex_list[lex_idx]}");
    node: Node = Node(NodeType.TYPEDEF);
    node.add_child(Node(NodeType.IDENTIFIER, lex_list[lex_idx+1].value));
    tmp: tuple[int,Node] = parse_type(lex_list, lex_idx+2);
    ASSERT(tmp != Node_NULL(), f"Expected type at TOKEN: {lex_list[lex_idx]}");
    node.add_child(tmp[1]);
    return (2+tmp[0], node);

def parse_struct(lex_list: list[lex.Token], lex_idx: int) -> tuple[int, Node]:
    if lex_list[lex_idx] != lex.TokenType.STRUCT: return Node_NULL();
    ASSERT(lex_list[lex_idx + 1].type == lex.TokenType.IDENTIFIER, f"Expected identifier at TOKEN: {lex_list[lex_idx]}");
    # TODO FINISH THIS

def parse_statement(lex_list: list[lex.Token], lex_idx: int) -> tuple[int, Node]:
    primaries: list[typing.Callable[[list[lex.Token],int],tuple[int,Node]]] = [
        parse_typedef,  parse_struct,     parse_label,
        parse_reserve,  parse_set,        parse_store,
        parse_command,  parse_scope
    ];
    for func in primaries:
        tmp: tuple[int,Node] = func(lex_list, lex_idx);
        if tmp[1].type != NodeType.NULL: return tmp;
    return Node_NULL();

### MAIN PARSE

def parse_program(lex_list: list[lex.Token]) -> Node:
    ret: Node = Node(NodeType.ROOT);
    idx: int = 0;
    while idx < len(lex_list):
        tmp: tuple[int, Node] = parse_statement(lex_list, idx);
        idx += tmp[0];
        ret.add_child(tmp[1]);
    return ret;