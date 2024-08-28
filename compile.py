import parse
from enum import Enum
from typing import Union
from typing import Callable

class RegisterType(Enum):
    GLOBAL=  0;
    A8    =  1;
    B8    =  2;
    C8    =  3;
    D8    =  4;
    A16   =  5;
    B16   =  6;
    C16   =  7;
    D16   =  8;
    A23   =  9;
    B32   = 10;
    C32   = 11;
    D32   = 12;
    A64   = 13;
    B64   = 14;
    C64   = 15;
    D64   = 16;
    IP    = 17;
    SP    = 18;
    BP    = 19;
    FL    = 20;

def ExprTypetoSize(t: parse.ExprType):
    match t:
        case parse.ExprType.BIGINT:   return 8;
        case parse.ExprType.SMALLINT: return 1;
        case parse.ExprType.MEDINT:   return 2;
        case parse.ExprType.POINTER:  return 8;

class String:
    def __init__(self, name: str, identifier: str) -> None:
        self.name = name;
        self.identifier = identifier;
class Constant:
    def __init__(self, name: str, value: int) -> None:
        self.name = name;
        self.value = value;
class Position:
    def __init__(self, register: RegisterType, offset: int) -> None:
        self.register: RegisterType = register;
        self.offset:   int          = offset;
class Variable:
    def __intit__(self, name: str, position: Position, size: int) -> None:
        self.name:     str      = name;
        self.position: Position = position;
        self.size:     int      = size;

class Program:
    def __init__(self) -> None:
        self.code:     str = "";
        self.data:     str = "";
        self.readonly: str = "";
    def add_code(self, code: str, end: str ='\n') -> None:
        self.code += code + end;
    def add_data_code(self, data: str, end: str='\n') -> None:
        self.data += data + end;
    def add_data_int(self, name: str, value: int) -> None:
        self.data += f"cset {name} {value}";
    def add_data_string(self, name: str, value: str) -> None:
        self.data += f"cset {name} \"{value}\"";
    def add_readonly_code(self, readonly: str, end: str='\n') -> None:
        self.readonly += readonly + end;
    def compose(self, program) -> None:
        self.code += program.code;
        self.data += program.data;
        self.readonly += program.readonly;

class Scope:
    def __init__(self, parent_scope) -> None:
        self.parent:                  Scope             = parent_scope;
        self.program:                 Program           = Program();
        self.children:                list[Scope]       = [];
        self.currently_accesed_child: Union[int | None] = None;
        self.variables:               list[Variable]    = [];
        self.constants:               list[Constant]    = [];
        self.strings:                 list[String]      = [];
        self.string_number:           list[String]      = [];
        self.stacksize:               int               = 0;
        self.label_id:                int               = 0;
    def add_variable(self, name: str, size: int, this: bool = False) -> None:
        if self.currently_accesed_child != None and not this:
            self.children[self.currently_accessed_child].add_variable(name, size);
        else:
            self.variables.append(Variable(name, Position(RegisterType.BP, self.stacksize+16), size));
            if size > 0: self.stacksize += size;
    def add_constant(self, name: str, value: int, this: bool = False) -> None:
        if self.currently_accesed_child != None and not this:
            self.children[self.currently_accessed_child].add_constant(name, value);
        else:
            self.constants.append(Constant(name, value));
    def add_string(self, name: str, value: str, this: bool = False) -> int:
        if self.currently_accesed_child != None and not this:
            self.children[self.currently_accessed_child].add_string(name, value);
        else:
            self.strings.append(String(name, f"STRING{self.string_number}"));
            self.program.add_data_string(name, value);
            self.string_number += 1;
    def get_variable(self, name: str, this: bool = False) -> Variable:
        if self.currently_accesed_child != None and not this:
            return self.children[self.currently_accessed_child].get_variable(name);
        else:
            for i in self.variables:
                if i.name == name: return name;
            else:
                if self.parent:
                    tmp: Variable = self.parent.get_variable(name, True);
                    tmp.position.offset -= self.parent.stacksize+16;
        return None;
    def get_constant_value(self, name: str) -> int:
        if self.currently_accesed_child != None:
            return self.children[self.currently_accessed_child].get_constant_value(name);
        else:
            for i in self.constants:
                return i.value;
            else:
                if self.parent: return self.parent.get_constant_value(name);
        return None;
    def get_string_id(self, name: str) -> str:
        if self.currently_accesed_child != None:
            return self.children[self.currently_accessed_child].get_string_id(name);
        else:
            for i in self.strings:
                if i.name == name: return i.identifier;
            else:
                if self.parent: return self.parent.get_string_id(name);
        return None;
    def enter_new_scope(self, which: int):
        self.currently_accessed_child = which;
    def exit_scope(self):
        self.currently_accessed_child = None;
    def create_new_child_scope(self) -> int:
        idx:   int  = 0;
        found: bool = False;
        for idx, i in enumerate(self.children):
            if i != None: continue;
            found = True;
            break;
        if found: self.children[idx] = Scope(self);
        else: self.children.append(Scope(self));
        return len(self.children)-1;
    def delete_child_scope(self, idx: int) -> int:
        self.children[idx] = None;
    def add_code(self, string: str, end: str='\n'):
        if self.currently_accesed_child != None:
            self.children[self.currently_accesed_child].add_code(string, end);
            return;
        self.program.add_code(string, end);
    def compose(self) -> Program:
        self.program.code = f"push BP\nmvr BP SP\nsub SP {self.stacksize}\n" + self.program.code;
        for i in self.children:
            self.program.compose(i.compose());
        return self.program;
    def next_label_id(self) -> int:
        if self.parent: return self.parent.next_label_id();
        else:
            self.label_id += 1;
            return self.label_id;


class STATE:
    def __init__(self) -> None:
        self.global_scope = Scope(None);
        self.while_num = 0;
    def compile_self(self) -> str:
        program: Program = self.global_scope.compose();
        ret = (f"segment executable\n{program.code}\n" +
               f"segment writable\n{program.data}\n"   +
               f"segment executable\n{program.readonly}\n");
        return ret;

def compile_define(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.DEFINE: return False;
    state.global_scope.add_constant(ast.children[0].value, ast.children[1].value);
    return True;

def compile_block(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.BLOCK: return False;
    for i in ast.children:
        compile_statement(i, state);
    return True;

def compile_while(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.WHILE: return False;
    while_id: int = state.global_scope.next_label_id();
    compile_expr(ast.children[0], state);
    state.global_scope.add_code(f"lbl .sw_{while_id}:");
    state.global_scope.add_code(f"jzr .ew_{while_id}");
    compile_block(ast.children[1], state);
    state.global_scope.add_code(f"jun .sw_{while_id}");
    state.global_scope.add_code(f"lbl .ew_{while_id}:");
    return True;

def compile_if(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.IF: return False;
    if_id: int = state.global_scope.next_label_id();
    compile_expr(ast.children[0], state);
    if len(ast.children) == 3:
        state.global_scope.add_code(f"jzr .ie_{if_id}");
    else: 
        state.global_scope.add_code(f"jzr .i_{if_id}");
    compile_block(ast.children[1], state);
    if len(ast.children) == 3:
        state.global_scope.add_code(f"jun .i_{if_id}");
        state.global_scope.add_code(f"lbl .ie_{if_id}:");
        compile_block(ast.children[2], state);
    state.global_scope.add_code(f"lbl .i_{if_id}");
    return True;

def compile_let(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.IF: return False;
    state.global_scope.add_variable(ast.children[0].value, ExprTypetoSize(parse.ASTtoExprType(ast.children[0].node_type)));
    return True;

def compile_hlt(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.HALT: return False;
    compile_expr(ast.children[0], state);
    state.global_scope.add_code("sfn exit");
    return True;

def compile_print(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.PRINT: return False;
    compile_expr(ast.children[0], state);
    state.global_scope.add_code("sub [SP] 1");
    state.global_scope.add_code("stb [SP] a8");
    state.global_scope.add_code("ldr b64 [SP]");
    state.global_scope.add_code("ldr a64 stdout");
    state.global_scope.add_code("ldr c64 1");
    state.global_scope.add_code("sfn write");


def compile_print(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.PRINT: return False;
    compile_expr(ast.children[0], state);
    state.global_scope.add_code("sub [SP] 1");
    state.global_scope.add_code("stb [SP] a8");
    state.global_scope.add_code("ldr b64 [SP]");
    state.global_scope.add_code("ldr a64 stdout");
    state.global_scope.add_code("ldr c64 1");
    state.global_scope.add_code("sfn write");
    return True;

def compile_input(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.PRINT: return False;
    state.global_scope.add_code("sub [SP] 1");
    state.global_scope.add_code("ldr b64 [SP]");
    state.global_scope.add_code("ldr a64 stdin");
    state.global_scope.add_code("ldr c64 1");
    state.global_scope.add_code("sfn read");
    return True;

def compile_call(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.CALL: return False;
    
    state.global_scope.add_code(f"call {ast.children[0].value}");
    return True;

def compile_statement(ast: parse.AST, state: STATE) -> bool:
    statements: list[Callable[[parse.AST,STATE],bool]] = [
        compile_while, compile_if,    compile_let,
        compile_hlt,   compile_print, compile_input,
        compile_call,  compile_store, compile_const_str
    ];
    for i in statements:
        if i(ast,state): return True;
    return False;

def compile_block(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.BLOCK: return False;
    for i in ast.children:
        compile_statement(i, state);
    return True;

def compile_procedure(ast: parse.AST, state: STATE) -> bool:
    if ast.node_type != parse.ASTType.PROCEDURE:
        return True;
    scope_id: int;
    state.global_scope.add_code(f"lbl {ast.children[0].value}:");
    scope_id = state.global_scope.create_new_child_scope();
    state.global_scope.enter_new_scope(scope_id);
    stack_unpack: int = 0;
    for i in ast.children[1:-1]:
        state.global_scope.add_variable(i.value, ExprTypetoSize(parse.ASTtoExprType(i.node_type)), False);
        state.global_scope.add_code(f"mvr a64 BP");
        state.global_scope.add_code(f"mvr b64 BP");
        state.global_scope.add_code(f"add a64 {16+stack_unpack}");
        state.global_scope.add_code(f"sub b64 {stack_unpack}");
        state.global_scope.add_code(f"stx b64 a64");
    compile_block(ast.children[-1], state);
    state.global_scope.exit_scope();
    state.global_scope.delete_child_scope(scope_id);
    return True;

def compile_primary(ast: parse.AST, state: STATE) -> bool:
    primaries: list[Callable[[parse.AST,STATE],bool]] = [
        compile_procedure, compile_define
    ];
    for i in primaries:
        tmp: bool = i(ast,state);
        if tmp: return True;
    return False;

def compile_program(ast: parse.AST) -> str:
    state: STATE = STATE();
    for idx, i in enumerate(ast.children):
        compile_primary(ast, state);
    return state.compile_self();