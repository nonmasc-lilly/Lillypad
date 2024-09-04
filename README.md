
# LILLYPAD

Lillypad is a simple programming language consisting of the following concepts:

- integers
- pointers
- structures
- types
- expressions
- variables
- conditionals
- labels
- gotos

## I. Integers & Pointers

Integers and pointers are both 32 bit constructs, integers are signed, while pointers are unsigned. We may add and subtract integers, we may also reference a variable (Sect. V) and dereference and expression (Sect. IV)
we may also add and subtract pointers. These are the "basic" datatype of LILLYPAD.

## II. Structures

A Structure is simply a series of integers and pointers which may be considered one object, for example a list in which each object has an integer and a pointer to the next node is a structure.

## III. 

```
program     =   *(typedef / struct / label / reserve / set / store / command / "{" / "}")
typedef     =   "typedef" identifier type
struct      =   "struct" identifier [type *("." type)]
label       =   "label" identifier
reserve     =   "let" identifier ":" type
set         =   "set" identifier expression
store       =   "store" (dereference / identifier) expression
command     =   "syscall" identifier *(expression)
type        =   "int" / identifier
struct_type =   "struct" identifier
expression  =   integer / identifier / access / add / subtract / reference / dereference
access      =   identifier "." integer
add         =   "add" expression expression
subtract    =   "subtract" expression expression
reference   =   "reference" expression
dereference =   "dereference" expression
integer     =   *DIGIT / "0x" *HEXDIG
identifier  =   ALPHA *VCHAR

```