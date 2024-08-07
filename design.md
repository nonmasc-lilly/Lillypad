# Lillypad programming language

Lillypad is a programming language designed to be completed over ten
weeks in a freeform projects in computing class.

Backus Naur Form:

```
<program>     ::= <definition> | <procedure>
<definition>  ::= "#" <iden> <cexpr>
<cexpr>       ::= <cadd> | <csub> | <iden> | <iconst>
<cadd>        ::= "+" <cexpr> <cexpr>
<csub>        ::= "-" <cexpr> <cexpr>
<iconst>      ::= <digz> | <dignz> <iconst>
<digz>        ::= "0" | dignz
<dignz>       ::= "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
<iden>        ::= <char> <iden> | <iden> <iconst> | <iden> <iden>
<procedure>   ::= <iden> "("")" <block> | <iden> "(" <paren> ")" <block>
<paren>       ::= <typed iden> | <paren> "," <paren>
<typed iden>  ::= <iden> | "r8" <iden> | "rx" <iden> | "*" <iden>
<block>       ::= "end" | <statement> "end" | <mstatement> "end"
<mstatement>  ::= statement | <mstatement> statement
<statement>   ::= <while> | <if> | <let> | <hlt> | <print> | <input> |
    <call> | <store> | <conststr>
<conststr>    ::= "const" <iden> <strconst>
<while>       ::= "while" "(" <expr> ")" <block>
<if>          ::= "if" "(" <expr> ")" <block> | "if" "(" <expr> ")"
    <block> "else" <block>
<let>         ::= "let" <typed iden>
<hlt>         ::= "hlt" <expr>
<print>       ::= "prc" <expr>
<input>       ::= "inp"
<call>        ::= "!" <iden> "(" cparen ")"
<cparen>      ::= <expr> | <cparen> "," <cparen>
<store>       ::= <iden> "=" <expr> | "store" <iden> <expr>
<expr>        ::= <iconst> | <iden> | <add> | <sub> | <equ> | <grt> |
    <not> | <and> | <or> | <reference> | <dereference> | <cast>
<add>         ::= "+" <expr> <expr>
<sub>         ::= "-" <expr> <expr>
<equ>         ::= "equ" <expr> <expr>
<grt>         ::= "grt" <expr> <expr>
<not>         ::= "not" <expr> <expr>
<and>         ::= "and" <expr> <expr>
<or>          ::= "or"  <expr> <expr>
<type>        ::= "*" | "r8" | "rx" | "int"
<cast>        ::= "(" <type> "<-" <type> ")" "<-" <expr>
<reference>   ::= "&"  <expr> <expr>
<dereference> ::= "*"  <expr> <expr>
<strconst>    ::= '"' <ALPHA> '"'
```

Where `ALPHA` is defined as any printable character as well as " "

[comment]: <> (TODO add documentation for language in a more fine grained sense)
