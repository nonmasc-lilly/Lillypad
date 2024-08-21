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
        self.constants:               list[Constant]    = {};
        self.strings:                 list[String]      = [];
        self.string_number:           list[String]      = [];
        self.stacksize:               int               = 0;
    def add_variable(self, name: str, size: int, this: bool = False) -> None:
        if self.currently_accesed_child != None and not this:
            self.children[self.currently_accessed_child].add_variable(name, size);
        else:
            self.variables.append(Variable(name, Position(RegisterType.BP, self.stacksize+16), size));
            self.stacksize += size;
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
                if self.parent: return self.parent.get_variable(name, True);
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
        self.children.append(Scope(self));
        return len(self.children)-1;
    def compose(self) -> Program:
        self.program.code = f"push BP\nmvr BP SP\nsub SP {self.stacksize}\n" + self.program.code;
        for i in self.children:
            self.program.compose(i.compose());
        return self.program;


class STATE:
    def __init__(self) -> None:
        self.global_scope = Scope(None);
    def compile_self(self) -> str:
        program: Program = self.global_scope.compose();
        ret = (f"segment executable\n{program.code}\n" +
               f"segment writable\n{program.data}\n"   +
               f"segment executable\n{program.readonly}\n");
        return ret;

def compile_program(ast: parse.AST) -> str:
    state: STATE = STATE();
    return state.compile_self();