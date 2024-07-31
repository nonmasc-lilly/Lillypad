from lex import Token;
from lex import TokenType;
from enum import Enum;
from typing import Callable;

class ASTType(Enum):
    ROOT      = 0;
    PROCEDURE = 1;
    DEFINE    = 2;
    IDEN      = 3;
    INTEGER   = 4;
    CSTRING   = 5;
    ADD       = 6;
    SUB       = 7;
    CADD      = 6;
    CSUB      = 7;

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


class STATE:
    def __init__(self):
        self.constants: list[Constant] = [];
    def add_constant(self, name: str, value: int) -> None:
        self.constants.append(Constant(name, value));
    def get_constant(self, name: str) -> int:
        for i in self.constants:
            if i.iden == name: return i.value;
        return None;

def ASSERT(condition: bool, message: str, token: Token) -> None:
    if not condition:
        print(f"Error: {str}\n\tToken: {token}");
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

# TODO: parse procedure
def parse_procedure(lex_list: list[Token], idx: int, state: STATE) -> AST:
    return None;

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