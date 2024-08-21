import sys
import lex
import parse
from typing import TextIO

def main(argc: int, argv: list[str]) -> int:
    fp:           TextIO            = None;
    file_content: str               = None;
    lexed_tokens: list[lex.token]   = None;
    parse_tree:   parse.AST         = None;
    if argc != 2:
        print(f"Input error: usage.\nCorrect usage: {argv[0]} <input file>");
        exit(1);
    fp = open(argv[1], "r");
    file_content = fp.read();
    fp.close();
    lexed_tokens = lex.lex_string(file_content);
    for idx, i in enumerate(lexed_tokens):
        print(f"{idx}: {str(i)}");
    parse_tree = parse.parse_program(lexed_tokens);
    print(parse_tree);
    return 0;


if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv));