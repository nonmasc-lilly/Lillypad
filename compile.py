import parse
from enum import Enum
from typing import Union
from typing import Callable

class VariableType(Enum):
    NONE  = 0;
    VAR   = 1;
    CONST = 2;

class Variable:
    def __init__(self, scope: int, const: parse.Constant = None, var: parse.Variable = None):
        self.scope: int = scope;
        self.var: parse.Variable = var;
        self.constant: parse.Constant = const;
        if self.var != None:        self.kind = VariableType.VAR;
        elif self.constant != None: self.kind = VariableType.CONST;
        else:                       self.kind = VariableType.NONE;

class STATE:
    def __init__(self):
        self.scope: int = 0;
        self.variables: list[Variable] = [];
        self.code: str = "";
    def start_scope(self): self.scope += 1;
    def end_scope(self): self.scope -= 1;
    def add_variable(self, var: parse.Variable = None, const: parse.Constant = None, location: int = 0):
        self.variables.append(Variable(self.scope, const, var));
    def get_variable_id(self, name: str) -> int:
        for i in range(self.scope,-1,-1):
            for idx, j in enumerate(self.variables):
                if j.scope != i: continue;
                if j.kind == VariableType.NONE: continue;
                if j.kind == VariableType.CONST:
                    if j.constant.iden != name: continue;
                    return idx;
                if j.kind == VariableType.VAR:
                    if j.var.name != name: continue;
                    return idx;
        return -1;
    def add_code(self,code: str, end="\n"):
        self.code += code + end;

def compile_define(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.DEFINE: return False;
    state.add_variable(None, parse.Constant(ast.children[0].value, int(ast.children[1].value)));
    return True;

#TODO: finish procedure

def compile_procedure(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.PROCEDURE: return False;
    state.start_scope();
    state.add_code(f"lbl {ast.children[0].value}:");
    for i in ast.children[1:]:
        state.add_variable(parse.Variable(state.scope, i.value, parse.ASTtoExprType(i.node_type)));
    state.end_scope();
    return False;

def compile_primary(ast: parse.AST, state: STATE) -> bool:
    primaries: Callable[[parse.AST,STATE],bool] = [
        compile_procedure, compile_define
    ];
    for i in primaries:
        tmp = i(ast, state);
        if tmp == True: return tmp;
    return False;

def compile_program(ast: parse.AST):
    state: STATE;
    state = STATE();
    for i in ast.children:
        compile_primary(i, state);