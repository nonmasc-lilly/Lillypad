from lex import Token;
from lex import TokenType;
from enum import Enum;
from typing import Callable;

class ExprType(Enum):
    BIGINT    = 0;
    MEDINT    = 1;
    SMALLINT  = 2;
    POINTER   = BIGINT;

class ASTType(Enum):
    ROOT                =  0; # *(PROCEDURE / DEFINE)
    PROCEDURE           =  1; # IDEN *IDEN BLOCK
    DEFINE              =  2;
    IDEN                =  3;
    INTEGER             =  4;
    CSTRING             =  5;
    ADD                 =  6; # expr expr
    SUB                 =  7; # expr expr
    CADD                =  6; # cexpr
    CSUB                =  7; # cexpr
    BLOCK               =  8; # *statement
    POINTER             =  9; # {iden}
    R8                  = 10;
    RX                  = 11;
    WHILE               = 12;
    CONST_STRING_DEF    = 13;
    STRING              = 14;
    LET                 = 15;
    STORE               = 16;
    REFERENCE           = 17;
    CAST                = 18;
    TYPE                = 19;
    PRINT               = 20;
    CALL                = 21;
    IF                  = 22;
    INP                 = 23;
    HALT                = 24;

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
    def __init__(self, scope: int, name: str, ntype: ExprType):
        self.scope: int = scope;
        self.name = name;
        self.ntype: ExprType = ntype;
class Function:
    def __init__(self, name: str, parameters: list[Variable]):
        self.name = name;
        self.parameters = parameters;
    def compare(self, parameters: list[Variable]) -> bool:
        if len(parameters) != len(parameters): return False;
        else:
            for i in range(len(parameters)):
                if parameters[i] != self.parameters[i]: return False;
        return True;

class STATE:
    def __init__(self):
        self.constants: list[Constant] = [];
        self.variables: list[Variable] = [];
        self.functions: list[Function] = [];
        self.scope:     int            =  0;
    def add_constant(self, name: str, value: int) -> None:
        self.constants.append(Constant(name, value));
    def get_constant(self, name: str) -> int:
        for i in self.constants:
            if i.iden == name: return i.value;
        return None;
    def add_variable(self, name: str, ntype: ExprType) -> bool:
        for i in self.variables:
            if i.name == name and i.scope == self.scope: return False;
        self.variables.append(Variable(self.scope, name, ntype));
        return True;
    def get_variable_type(self, name: str) -> ExprType:
        for i in self.variables:
            if i.name == name and i.scope == self.scope: return i.ntype;
        return None;
    def add_function(self, name: str, var: list[Variable]) -> bool:
        for i in self.functions:
            if i.name == name: return False;
        self.functions.append(Function(name, var));
        return True;
    def get_function(self, name: str) -> Function:
        for i in self.functions:
            if i.name == name: return i;
        return None;
    def new_scope(self):
        self.scope+=1;
    def fall_scope(self):
        for idx, i in enumerate(self.variables):
            if i.scope == self.scope:
                self.variables.pop(idx);
        self.scope -= 1;


def ASSERT(condition: bool, message: str, token: Token) -> None:
    if not condition:
        print(f"Error: {message}\n\tToken: {token}");
        exit(0);

##############################
#    Constant Expressions    #
##############################



def parse_iden(lex_list: list[Token], idx: int, state: STATE, etype: ExprType = None) -> tuple[int, AST]:
    if lex_list[idx].node_type != TokenType.IDEN: return None;
    if etype != None: ASSERT(state.get_variable_type(lex_list[idx].value),
        f"Expected matching type {etype.name} in expression got {state.get_variable_type(lex_list[idx].value)}", lex_list[idx]);
    return (1, AST(ASTType.IDEN, lex_list[idx].value));

def parse_integer(lex_list: list[Token], idx: int, state: STATE, etype: ExprType = None) -> tuple[int, AST]:
    if lex_list[idx].node_type != TokenType.INTEGER_CONST: return None;
    ASSERT(int(lex_list[idx].value) > -1, "Negative integers are non-implemented", lex_list[idx]);
    if etype != None:
        match etype:
            case ExprType.BIGINT: ASSERT(int(lex_list[idx].value) <= 0xFFFFFFFFFFFFFFFF,
                "Constant to large to be bigint", lex_list[idx]);
            case ExprType.MEDINT: ASSERT(int(lex_list[idx].value) <= 0xFFFF,
                "Constant to large to be medint", lex_list[idx]);
            case ExprType.SMALLINT: ASSERT(int(lex_list[idx].value) <= 0xFF,
                "Constant to large to be smallint", lex_list[idx]);
            case ExprType.POINTER: ASSERT(int(lex_list[idx].value) <= 0xFFFFFFFFFFFFFFFF,
                "Constant to large to be bigint", lex_list[idx]);
            case _: ASSERT(False, f"COMPILER ERROR: UNEXPECTED TYPE!!! {etype.name}", lex_list[idx]);
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

###########################
#    Parse Expressions    #
###########################

def get_type(a: TokenType) -> ExprType:
    match a:
        case TokenType.INT:     return ExprType.BIGINT;
        case TokenType.REGX:    return ExprType.MEDINT;
        case TokenType.REG8:    return ExprType.SMALLINT;
        case TokenType.POINTER: return ExprType.POINTER;
        case _: return None;

def parse_cast(lex_list: list[Token], idx: int, state: STATE, etype: ExprType) -> tuple[int, AST]:
    ret: AST;
    tmp: tuple[int, AST];
    off: int;
    if lex_list[idx].node_type != TokenType.OPEN_PAREN: return None;
    if get_type(lex_list[idx+1].node_type) == None: return None;
    if lex_list[idx+2].node_type != TokenType.CAST: return None;
    ret = AST(ASTType.CAST);
    ASSERT(get_type(lex_list[idx+1].node_type) == etype, f"Expected cast type to be expected type: {etype.name}", lex_list[idx]);
    ret.add_child(AST(ASTType.TYPE, get_type(lex_list[idx+1].node_type).name));
    ret.add_child(AST(ASTType.TYPE, get_type(lex_list[idx+3].node_type).name));
    ASSERT(lex_list[idx+4].node_type == TokenType.CLOSE_PAREN, "Expected close parenthesis in cast", lex_list[idx+4]);
    ASSERT(lex_list[idx+5].node_type == TokenType.CAST, "Expected cast arrow in cast", lex_list[idx+5]);
    off = 6;
    tmp = parse_expr(lex_list, idx+off, state, get_type(lex_list[idx+3].node_type));
    ASSERT(tmp != None, "Expected expression after cast", lex_list[idx+off]);
    off += tmp[0];
    return (off, tmp[1]);


# TODO: add
def parse_inp(lex_list: list[Token], idx: int, state: STATE, etype: ExprType) -> tuple[int, AST]:
    if lex_list[idx].node_type != TokenType.INP: return None;
    ASSERT(etype == ExprType.SMALLINT,
        f"Expected {etype.name} got INP (which is of type r8/SMALLINT)", lex_list[idx]);
    return (1, AST(ASTType.INP));
def parse_add(lex_list: list[Token], idx: int, state: STATE, etype: ExprType) -> tuple[int, AST]:
    ret: AST;
    off: int;
    tmp: tuple[int, AST];
    if lex_list[idx].node_type != TokenType.ADD: return None;
    ret = AST(ASTType.ADD);
    tmp = parse_expr(lex_list, idx+1, state, etype);
    ASSERT(tmp, "Expected first argument in add expression", lex_list[idx]);
    off = tmp[0]+1;
    ret.add_child(tmp[1]);
    tmp = parse_expr(lex_list, idx+off, state, etype);
    ASSERT(tmp, "Expected second argument in add expression", lex_list[idx]);
    off += tmp[0];
    ret.add_child(tmp[1]);
    return (off, ret);
# TODO: sub
def parse_sub(lex_list: list[Token], idx: int, state: STATE, etype: ExprType) -> tuple[int, AST]:
    ret: AST;
    off: int;
    tmp: tuple[int, AST];
    if lex_list[idx].node_type != TokenType.SUB: return None;
    ret = AST(ASTType.SUB);
    tmp = parse_expr(lex_list, idx+1, state, etype);
    ASSERT(tmp, "Expected first argument in add expression", lex_list[idx]);
    off = tmp[0]+1;
    ret.add_child(tmp[1]);
    tmp = parse_expr(lex_list, idx+off, state, etype);
    ASSERT(tmp, "Expected second argument in add expression", lex_list[idx]);
    off += tmp[0];
    ret.add_child(tmp[1]);
    return (off, ret);
def parse_ref(lex_list: list[Token], idx: int, state: STATE, etype: ExprType) -> tuple[int, AST]:
    ret: AST;
    if lex_list[idx].node_type != TokenType.REFERENCE: return None;
    ret = AST(ASTType.REFERENCE);
    ASSERT(lex_list[idx+1].node_type == TokenType.IDEN, "Expected first argument in reference expression", lex_list[idx]);
    ret.add_child(AST(ASTType.IDEN, lex_list[idx+1].value));
    return (2, ret);
def parse_deref(lex_list: list[Token], idx: int, state: STATE, etype: ExprType) -> tuple[int, AST]:
    ret: AST;
    off: int;
    tmp: tuple[int, AST];
    if lex_list[idx].node_type != TokenType.POINTER: return None;
    ASSERT(etype == ExprType.POINTER, f"Expected {etype.name} type got POINTER", lex_list[idx]);
    ret = AST(ASTType.POINTER);
    tmp = parse_expr(lex_list, idx+1, state, etype);
    ASSERT(tmp, "Expected first argument in dereference expression", lex_list[idx]);
    off = tmp[0]+1;
    ret.add_child(tmp[1]);
    return (off, ret);
def parse_expr(lex_list: list[Token], idx: int, state: STATE, etype: ExprType) -> tuple[int,AST]:
    ret: AST;
    off: int;
    tmp: tuple[int,AST];
    exprs: list[Callable[[list[Token],int,STATE],tuple[int,AST]]];
    exprs = [
        parse_inp, parse_cast, parse_ref, parse_deref, parse_add, parse_sub, parse_iden, parse_integer
    ];
    i: int = 0;
    while i < len(exprs):
        tmp = exprs[i](lex_list, idx, state, etype);
        if tmp != None:
            return tmp;
        i += 1;
    return None;

##########################
#    Parse Statements    #
##########################

def parse_while(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    ret: AST;
    off: int;
    tmp: tuple[int, AST];
    if lex_list[idx].node_type != TokenType.WHILE: return None;
    ASSERT(lex_list[idx+1].node_type == TokenType.OPEN_PAREN,
        "Expected open parenthesis for while loop", lex_list[idx+1]);
    off = 2;
    ret = AST(ASTType.WHILE);
    tmp = parse_expr(lex_list, idx+off, state, ExprType.BIGINT);
    ASSERT(tmp != None, "Expected expression in while loop", lex_list[idx+off]);
    ret.add_child(tmp[1]);
    off += tmp[0];
    ASSERT(lex_list[idx+off].node_type == TokenType.CLOSE_PAREN,
        "Expected close parenthesis in while loop",
        lex_list[idx+off]);
    off += 1;
    tmp = parse_block(lex_list, idx+off, state);
    ASSERT(tmp != None, "Expected statements in while loop", lex_list[idx+off]);
    ret.add_child(tmp[1]);
    off += tmp[0];
    return (off, ret);

def parse_if(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    ret: AST;
    off: int;
    tmp: tuple[int, AST];
    if lex_list[idx].node_type != TokenType.IF: return None;
    ASSERT(lex_list[idx+1].node_type == TokenType.OPEN_PAREN,
        "Expected open parenthesis for if", lex_list[idx+1]);
    off = 2;
    ret = AST(ASTType.IF);
    tmp = parse_expr(lex_list, idx+off, state, ExprType.BIGINT);
    ASSERT(tmp != None, "Expected expression in if", lex_list[idx+off]);
    ret.add_child(tmp[1]);
    off += tmp[0];
    ASSERT(lex_list[idx+off], "Expected close parenthesis for if", lex_list[idx+off]);
    off += 1;
    tmp = parse_block(lex_list, idx+off, state);
    ASSERT(tmp != None, "Expected statements in if", lex_list[idx+off]);
    ret.add_child(tmp[1]);
    off += tmp[0];
    if lex_list[idx+off].node_type == TokenType.ELSE:
        off += 1;
        tmp = parse_block(lex_list, idx+off, state);
        ASSERT(tmp != None, "Expected statements in else", lex_list[idx+off]);
        ret.add_child(tmp[1]);
        off += tmp[0]
    return (off, ret);

def parse_let(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    tmp: tuple[int, AST];
    ret: AST;
    off: int;
    ttype: ExprType;
    if lex_list[idx].node_type != TokenType.LET: return None;
    tmp = parse_typed_iden(lex_list, idx+1, state);
    ASSERT(tmp != None, "Expected typed identifier for let", lex_list[idx+1]);
    off = tmp[0] + 1;
    ret = AST(ASTType.LET);
    ret.add_child(tmp[1]);
    match tmp[1].node_type:
        case ASTType.POINTER: ttype = ExprType.POINTER;
        case ASTType.R8:      ttype = ExprType.SMALLINT;
        case ASTType.RX:      ttype = ExprType.MEDINT;
        case ASTType.IDEN:    ttype = ExprType.BIGINT;
    state.add_variable(tmp[1].value, ttype);
    return (off, ret);

def parse_hlt(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    tmp: tuple[int, AST];
    ret: AST;
    off: int;
    if lex_list[idx].node_type != TokenType.HALT: return None;
    tmp = parse_expr(lex_list, idx+1, state, ExprType.SMALLINT);
    ASSERT(tmp != None, "Expected expression in halt", lex_list[idx]);
    off = tmp[0] + 1;
    ret = AST(ASTType.HALT);
    ret.add_child(tmp[1]);
    return (off, ret);

def parse_print(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    tmp: tuple[int, AST];
    ret: AST;
    off: int;
    if lex_list[idx].node_type != TokenType.PRC: return None;
    off = 1;
    tmp = parse_expr(lex_list, idx+1, state, ExprType.SMALLINT);
    ASSERT(tmp != None, "Expected expression in print", lex_list[idx+off]);
    off = tmp[0] + 1;
    ret = AST(ASTType.PRINT);
    ret.add_child(tmp[1]);
    return (off, ret);

def parse_input(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    ret: AST;
    if lex_list[idx].node_type != TokenType.INP: return None;
    ret = AST(ASTType.INPUT);
    return (1, ret);

def parse_call(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    off: int;
    ret: AST;
    var: list[Variable];
    tmp: tuple[int, AST];
    if lex_list[idx].node_type != TokenType.CALL: return None;
    var = [];
    ret = AST(ASTType.CALL);
    ASSERT(lex_list[idx+1].node_type == TokenType.IDEN,
        "Expected identifier in call statement", lex_list[idx+1]);
    ASSERT(lex_list[idx+2].node_type == TokenType.OPEN_PAREN,
        "Expected open parenthesis in call statement",
        lex_list[idx+2]);
    ret.add_child(AST(ASTType.IDEN, lex_list[idx+1].value));
    off = 3
    while lex_list[idx+off].node_type != TokenType.CLOSE_PAREN:
        tmp = parse_typed_iden(lex_list, idx+off, state);
        ASSERT(tmp != None, "Expected typed identifier in function parameters", lex_list[idx+off]);
        off += tmp[0];
        ret.add_child(tmp[1]);
        match tmp[1].node_type:
            case ASTType.IDEN:    var.append(Variable(state.scope, str(len(var)), ExprType.BIGINT));
            case ASTType.R8:      var.append(Variable(state.scope, str(len(var)), ExprType.MEDINT));
            case ASTType.RX:      var.append(Variable(state.scope, str(len(var)), ExprType.SMALLINT));
            case ASTType.POINTER: var.append(Variable(state.scope, str(len(var)), ExprType.POINTER));
            case _: ASTSERT(False, "COMPILER ERROR: INVALID TYPE FOUND", lex_list[idx+off]);
        if lex_list[idx+off].node_type == TokenType.COMMA: off += 1;
        else: ASSERT(lex_list[idx+off].node_type == TokenType.CLOSE_PAREN,
                "Expected comma or close parenthesis in funciton parameters",
                lex_list[idx+off]
            );
    state.get_function(ret.children[0].value).compare(var);
    return (off+1, ret);

def parse_store(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    off: int;
    ret: AST;
    tmp: tuple[int, AST];
    ttype: ExprType;
    if lex_list[idx].node_type != TokenType.STORE and (not (lex_list[idx].node_type == TokenType.IDEN and lex_list[idx+1].node_type == TokenType.STORE)):
        return None;
    ret = AST(ASTType.STORE);
    if lex_list[idx].node_type == TokenType.STORE: ret.add_child(AST(ASTType.IDEN, lex_list[idx+1].value));
    else: ret.add_child(AST(ASTType.IDEN, lex_list[idx].value));
    off = 2;
    ttype = state.get_variable_type(ret.children[0].value);
    ASSERT(ttype != None, "Expected variable in store to exist", lex_list[idx]);
    tmp = parse_expr(lex_list, idx+off, state, ttype);
    ASSERT(tmp != None, "Expected expression in store statement", lex_list[idx]);
    ret.add_child(tmp[1]);
    off += tmp[0];
    print("HI");
    print(f"{ret}")
    return (off, ret);

def parse_const_str(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    ret: AST;
    if lex_list[idx].node_type != TokenType.CONST: return None;
    ASSERT(lex_list[idx+1].node_type == TokenType.IDEN,
        "Expected identifier in constant string definition",
        lex_list[idx+1]);
    ASSERT(lex_list[idx+2].node_type == TokenType.STRING_CONST,
        "Expected string constant in constant string definition",
        lex_list[idx+2]);
    ret = AST(ASTType.CONST_STRING_DEF);
    ret.add_child(AST(ASTType.IDEN, lex_list[idx+1].value));
    state.add_variable(lex_list[idx+1].value, ExprType.POINTER);
    ret.add_child(AST(ASTType.STRING, lex_list[idx+2].value));
    return (3, ret);

def parse_statement(lex_list: list[Token], idx: int, state: STATE) -> tuple[int, AST]:
    prim_statements: list[Callable[[list[Token],int,STATE],tuple[int,AST]]];
    prim_statements = [
        parse_while, parse_if,    parse_let,
        parse_hlt,   parse_print, parse_input,
        parse_call,  parse_store, parse_const_str
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
        tmp = parse_statement(lex_list, idx+off, state);
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
            print(f"{lex_list[idx]} :: {lex_list[idx+1]}")
            return (2, AST(ASTType.POINTER, lex_list[idx+1].value));

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


def parse_procedure(lex_list: list[Token], idx: int, state: STATE) -> tuple[int,AST]:
    if not (lex_list[idx].node_type == TokenType.IDEN and lex_list[idx+1].node_type == TokenType.OPEN_PAREN): return None;
    ret: AST;
    off: int;
    tmp: tuple[int, AST];
    var: list[Variable];
    ret = AST(ASTType.PROCEDURE);
    off = 2;
    var = [];
    ret.add_child(AST(ASTType.IDEN, lex_list[idx].value));
    state.new_scope();
    while lex_list[idx+off].node_type != TokenType.CLOSE_PAREN:
        tmp = parse_typed_iden(lex_list, idx+off, state);
        ASSERT(tmp != None, "Expected typed identifier in function parameters", lex_list[idx+off]);
        off += tmp[0];
        ret.add_child(tmp[1]);
        match tmp[1].node_type:
            case ASTType.IDEN:    var.append(Variable(state.scope, tmp[1].value, ExprType.BIGINT));
            case ASTType.R8:    var.append(Variable(state.scope, tmp[1].value, ExprType.MEDINT));
            case ASTType.RX:    var.append(Variable(state.scope, tmp[1].value, ExprType.SMALLINT));
            case ASTType.POINTER: var.append(Variable(state.scope, tmp[1].value, ExprType.POINTER));
            case _: ASSERT(False, f"COMPILER ERROR: INVALID TYPE FOUND {tmp[1].node_type}", lex_list[idx+off-tmp[0]]);
        if lex_list[idx+off].node_type == TokenType.COMMA: off += 1;
        else: ASSERT(lex_list[idx+off].node_type == TokenType.CLOSE_PAREN,
                "Expected comma or close parenthesis in funciton parameters",
                lex_list[idx+off]
            );
    for i in var:
        state.add_variable(i.name, i.ntype);
    state.add_function(ret.children[0].value, var);
    off += 1;
    tmp = parse_block(lex_list, idx+off, state);
    state.fall_scope();
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
