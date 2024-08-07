from lex import Token;
from lex import TokenType;
from enum import Enum;
from typing import Callable;

class ASTType(Enum):
    ROOT      =  0; # *(PROCEDURE / DEFINE)
    PROCEDURE =  1; # IDEN *IDEN BLOCK
    DEFINE    =  2;
    IDEN      =  3;
    INTEGER   =  4;
    CSTRING   =  5;
    ADD       =  6; # expr expr
    SUB       =  7; # expr expr
    CADD      =  6; # cexpr
    CSUB      =  7; # cexpr
    BLOCK     =  8; # *statement
    POINTER   =  9; # {iden}
    R8        = 10;
    RX        = 11;
    WHILE     = 12;

class AST:
    def __init__(self, node_type: ASTType, value: str = "") -> None:
        self.node_type:  ASTType = node_type;
        self.value:          str =     value;
        self.children: list[AST] =        [];
    def add_child(self, new_child) -> None:
        self.children.append(new_child);
    def __repr__(self, i: int = 0):
        _ = i * ">" + f"{self.node_type.name} {self.value}";
        for k in self.children:
            _ += f"\n{k.__repr__(i+1)}";
        return _;

class Constant:
    def __init__(self, name: str, value: int):
        self.iden:  str =  name;
        self.value: int = value;
class Variable:
    def __init__(self, name: str, ntype: str):
        self.name = name;
        self.ntype = ntype;

class STATE:
    def __init__(self):
        self.constants: list[Constant] = [];
        self.variables: list[Variable] = [];
    def add_constant(self, name: str, value: int) -> None:
        self.constants.append(Constant(name, value));
    def get_constant(self, name: str) -> int:
        for i in self.constants:
            if i.iden == name: return i.value;
        return None;
    def add_variable(self, name: str, ntype: str) -> bool:
        for i in self.variables:
            if i.name == name: return False;
        self.variables.append(Variable(name, ntype));
        return True;
    def get_variable_type(self, name: str) -> str:
        for i in self.variables:
            if i.name == name: return i.ntype;
        return None;


def ASSERT(condition: bool, message: str, token: Token) -> None:
    if not condition:
        print(f"Error: {message}\n\tToken: {token}");
        exit(0);

#####################
#    Expressions    #
#####################



def parse_iden(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    if lex_list[idx].node_type != TokenType.IDEN: return None;
    return (1, AST(ASTType.IDEN, lex_list[idx].value));

def parse_integer(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    if lex_list[idx].node_type != TokenType.INTEGER_CONST: return None;
    return (1, AST(ASTType.INTEGER, lex_list[idx].value));

def parse_cadd(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    ret: tuple[int,AST];
    tmp: tuple[int,AST];
    if lex_list[idx].node_type != TokenType.ADD: return None;
    ret = (1, AST(ASTType.CADD));
    tmp = parse_constexpr(lex_list, idx+ret[0], state);
    ASSERT(tmp != None, "Expected constexpression after constant add", lex_list[idx]);
    ret[1].add_child(tmp[1]);
    ret = (ret[0]+tmp[0], ret[1]);
    tmp = parse_constexpr(lex_list, idx+ret[0], state);
    ASSERT(tmp != None, "Expected second constexpression after constant add", lex_list[idx]);
    ret[1].add_child(tmp[1]);
    ret = (ret[0]+tmp[0], ret[1]);
    return ret;

def parse_csub(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    ret: tuple[int,AST];
    tmp: tuple[int,AST];
    if lex_list[idx].node_type != TokenType.SUB: return None;
    ret = (1, AST(ASTType.CSUB));
    tmp = parse_constexpr(lex_list, idx+ret[0], state);
    ASSERT(tmp != None, "Expected constexpression after constant add", lex_list[idx]);
    ret[1].add_child(tmp[1]);
    ret = (ret[0]+tmp[0], ret[1]);
    tmp = parse_constexpr(lex_list, idx+ret[0], state);
    ASSERT(tmp != None, "Expected second constexpression after constant add", lex_list[idx]);
    ret[1].add_child(tmp[1]);
    ret = (ret[0]+tmp[0], ret[1]);
    return ret;

def eval_constexpr(constexpr: AST, state: STATE, when: Token) -> int:
    match constexpr.node_type:
        case ASTType.IDEN:
            _a = state.get_constant(constexpr.value);
            ASSERT(_a != None, f"Identifier {constexpr.value} does not correspond to a defined constant", when);
            return _a;
        case ASTType.INTEGER:
            try: return int(constexpr.value);
            except ValueError: ASSERT(False, "COMPILER ERROR: Integer has no value", when);
        case ASTType.ADD:
            return eval_constexpr(constexpr.children[0], state, when) + eval_constexpr(constexpr.children[1], state, when);
        case ASTType.SUB:
            return eval_constexpr(constexpr.children[0], state, when) - eval_constexpr(constexpr.children[1], state, when);
        case _: ASSERT(False, "COMPILER ERROR: Expected constexpr for evaluation", when);

def parse_constexpr(lex_list: list[Token], idx: int, state: STATE) -> tuple[int,AST]:
    const_exprs: list[Callable[[list[Token], int, STATE], tuple[int,AST]]] = [
        parse_iden, parse_integer, parse_cadd, parse_csub
    ];
    for i in range(len(const_exprs)):
        ret = const_exprs[i](lex_list, idx, state);
        if ret: return (ret[0], AST(ASTType.INTEGER, eval_constexpr(ret[1], state, lex_list[idx])));
    return None;

############################
#    Primary Statements    #
############################

# TODO: FIX COMMENTS
# TODO: ADD expected parse types
# TODO: finish statement parsing
# TODO: define statements

def parse_define(lex_list: list[Token], idx: int, state: STATE) -> tuple[int,AST]:
    ret: tuple[int,AST];
    tmp: tuple[int,AST];
    if lex_list[idx].node_type != TokenType.DEFINE: return None;
    ret = (1, AST(ASTType.DEFINE));
    tmp = parse_iden(lex_list, idx+ret[0], state);
    ASSERT(tmp != None, "Expected identifier after constant define", lex_list[idx]);\
    ASSERT(state.get_constant(tmp[1].value) == None, f"Redefined constant {tmp[1].value}", lex_list[idx]);
    ret = (ret[0]+tmp[0], ret[1]);
    ret[1].add_child(tmp[1]);
    tmp = parse_constexpr(lex_list, idx+ret[0], state);
    ASSERT(tmp != None, "Expected constexpr after constant define", lex_list[idx]);
    state.add_constant(ret[1].children[0].value, tmp[1].value)
    ret = (ret[0]+tmp[0], ret[1]);
    ret[1].add_child(tmp[1]);
    return ret;

# TODO: while
def parse_while(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    ret: AST;
    off: int;
    tmp: tuple[int, AST];
    if lex_list[idx].node_type != TokenType.WHILE: return None;
    ASSERT(lex_list[idx+1].node_type == TokenType.OPEN_PAREN,
        "Expected open parenthesis for while loop", lex_list[idx+1]);
    off = 2;
    ret = AST(ASTType.WHILE);
    tmp = parse_expr(lex_list, idx, state);
    ASSERT(tmp != None, "Expected expression in while loop", lex_list[idx+off]);
    ret.add_child(tmp[1]);
    off += tmp[0];
    tmp = parse_block(lex_list, idx+off, state);
    ASSERT(tmp != None, "Expected statements in while loop", lex_list[idx+off]);
    ret.add_child(tmp[1]);
    off += tmp[0];
    return (off, ret);
# TODO: if
def parse_if(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    ret: AST;
    off: int;
    tmp: tuple[int, AST];
    if lex_list[idx].node_type != TokenType.WHILE: return None;
    ASSERT(lex_list[idx+1].node_type == TokenType.OPEN_PAREN,
        "Expected open parenthesis for while loop", lex_list[idx+1]);
    off = 2;
    ret = AST(ASTType.WHILE);
    tmp = parse_expr(lex_list, idx, state);
    ASSERT(tmp != None, "Expected expression in while loop", lex_list[idx+off]);
    ret.add_child(tmp[1]);
    off += tmp[0];
    tmp = parse_block(lex_list, idx+off, state);
    ASSERT(tmp != None, "Expected statements in while loop", lex_list[idx+off]);
    ret.add_child(tmp[1]);
    off += tmp[0];
    if lex_list[idx+off].node_type == TokenType.ELSE:
        off += 1;
        tmp = parse_block(lex_list, idx+off, state);
        ASSERT(tmp != None, "Expected statements in while loop", lex_list[idx+off]);
        ret.add_child(tmp[1]);
        off += tmp[0]
    return (off, ret);
# TODO: let
def parse_let(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    tmp: tuple[int, AST];
    ret: AST;
    off: int;
    if lex_list[idx].node_type != TokenType.LET: return None;
    tmp = parse_typed_iden(lex_list, idx+1, state);
    ASSERT(tmp != None, "Expected typed identifier for let", lex_list[idx+off]);
    off = tmp[0] + 1;
    ret = AST(ASTType.LET);
    ret.add_child(tmp);
    return (off, ret);
# TODO: hlt
def parse_hlt(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    tmp: tuple[int, AST];
    ret: AST;
    off: int;
    if lex_list[idx].node_type != TokenType.HALT: return None;
    tmp = parse_expr(lex_list, idx+1, state);
    ASSERT(tmp != None, "Expected expression in halt", lex_list[idx+off]);
    off = tmp[0] + 1;
    ret = AST(ASTType.HALT);
    ret.add_child(tmp);
    return (off, ret);
# TODO: print
def parse_print(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    tmp: tuple[int, AST];
    ret: AST;
    off: int;
    if lex_list[idx].node_type != TokenType.PRC: return None;
    tmp = parse_expr(lex_list, idx+1, state);
    ASSERT(tmp != None, "Expected expression in print", lex_list[idx+off]);
    off = tmp[0] + 1;
    ret = AST(ASTType.PRINT);
    ret.add_child(tmp);
    return (off, ret);
# TODO: input
def parse_input(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    ret: AST;
    if lex_list[idx].node_type != TokenType.INP: return None;
    ret = AST(ASTType.INPUT);
    return (1, ret);
# TODO: call
def parse_call(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    off: int;
    ret: AST;
    tmp: tuple[int, AST];
    if lex_list[idx].node_type != TokenType.CALL: return None;
    ret = AST(ASTType.CALL);
    ASSERT(lex_list[idx+1].node_type == TokenType.IDEN,
        "Expected identifier in call statement", lex_list[idx+1]);
    while lex_list[idx+off].node_type != TokenType.CLOSE_PAREN:
        tmp = parse_typed_iden(lex_list, idx+off, state);
        ASSERT(tmp != None, "Expected typed identifier in function parameters", lex_list[idx+off]);
        off += tmp[0];
        ret.add_child(tmp[1]);
        if lex_list[idx+off].node_type == TokenType.COMMA: off += 1;
        else: ASSERT(lex_list[idx+off].node_type == TokenType.CLOSE_PAREN,
                "Expected comma or close parenthesis in funciton parameters",
                lex_list[idx+off]
            );

# TODO: store
def parse_store(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    return None;
def parse_statement(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    prim_statements: list[Callable[[list[Token],int,STATE],tuple[int,AST]]];
    prim_statements = [
        parse_while, parse_if,    parse_let,
        parse_hlt,   parse_print, parse_input,
        parse_call,  parse_store
    ];
    ret: tuple[int,AST];
    for i in range(len(prim_statements)):
        ret = prim_statements[i](lex_list, idx, state);
        if ret != None: return ret;
    return None

def parse_block(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    ret: AST;
    off: int;
    tmp: tuple[int, AST];
    ret = AST(ASTType.BLOCK);
    off = 0;
    while lex_list[idx+off].node_type != TokenType.END:
        tmp = parse_statement(lex_list, idx+off);
        ASSERT(tmp != None, "Expected statement in block", lex_list[idx+off]);
        ret.add_child(tmp[1]);
        off += tmp[0];
    return (off+1, ret);

# pointer = "*" iden
# procedure = iden "(" [(iden / pointer) *("," (iden / pointer))] ")" *statement "end"
# procedure -> iden *iden block

def parse_typed_iden(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    match lex_list[idx].node_type:
        case TokenType.IDEN: return (1, AST(ASTType.IDEN, lex_list[idx].value));
        case TokenType.REG8:
            ASSERT(lex_list[idx+1].node_type == TokenType.IDEN,
                "Expected identifier after reg8", lex_list[idx]);
            return (2, AST(ASTType.R8, lex_list[idx+1].value));
        case TokenType.REGX:
            ASSERT(lex_list[idx+1].node_type == TokenType.IDEN,
                "Expected identifier after regx", lex_list[idx]);
            return (2, AST(ASTType.RX, lex_list[idx+1].value));
        case TokenType.POINTER:
            ASSERT(lex_list[idx+1].node_type == TokenType.IDEN,
                "Expected identifier after reg8", lex_list[idx]);
            return (2, AST(ASTType.POINTER, lex_list[idx+1].value));

def parse_procedure(lex_list: list[Token], idx: int, state: STATE) -> tuple[int,AST]:
    if not (lex_list[idx].node_type == TokenType.IDEN and lex_list[idx+1].node_type == TokenType.OPEN_PAREN): return None;
    ret: AST;
    off: int;
    tmp: tuple[int, AST];
    ret = AST(ASTType.PROCEDURE);
    off = 2;
    ret.add_child(AST(ASTType.IDEN, lex_list[idx].value));
    while lex_list[idx+off].node_type != TokenType.CLOSE_PAREN:
        tmp = parse_typed_iden(lex_list, idx+off, state);
        ASSERT(tmp != None, "Expected typed identifier in function parameters", lex_list[idx+off]);
        off += tmp[0];
        ret.add_child(tmp[1]);
        if lex_list[idx+off].node_type == TokenType.COMMA: off += 1;
        else: ASSERT(lex_list[idx+off].node_type == TokenType.CLOSE_PAREN,
                "Expected comma or close parenthesis in funciton parameters",
                lex_list[idx+off]
            );
    off += 1;
    tmp = parse_block(lex_list, idx+off, state);
    ASSERT(tmp != None, "Expected block after procedure definition", lex_list[off]);
    ret.add_child(tmp[1]);
    off += tmp[0];
    return (off, ret);

#########################
#    Program parsing    #
#########################

def parse_prim_statement(lex_list: list[Token], idx: int, state: STATE) -> tuple[int,AST]:
    prim_statements: list[Callable[[list[Token],int,STATE],tuple[int,AST]]];
    prim_statements = [
        parse_procedure, parse_define
    ];
    ret: tuple[int,AST];
    for i in range(len(prim_statements)):
        ret = prim_statements[i](lex_list, idx, state);
        if ret != None: return ret;
    return None;

def parse_program(lex_list: list[Token]) -> AST:
    root:           AST;
    i:              int;
    tmp: tuple[AST,int];
    state: STATE;
    root = AST(ASTType.ROOT);
    state = STATE();
    i = 0;
    while i < len(lex_list):
        tmp = parse_prim_statement(lex_list, i, state);
        ASSERT(tmp != None, "Expected primary statement", lex_list[i]);
        root.add_child(tmp[1])
        i += tmp[0];
    return root;