import typing;
import sys;
import lex;

def main(argc: int, argv: list[str]) -> None:
    if argc < 3:
        print(f"Expected two arguments: {argv[0]} <infile> <outfile>");
        exit(1);
    print("LILLYPAD COMPILER 2024");
    file: typing.TextIO = open(argv[1], "r");
    file_string: str    = file.read();
    file.close();
    lexed_tokens: list[lex.Token] = lex.lex_string(file_string);
    for i in lexed_tokens:
        print(f"{i}");

if __name__ == "__main__": main(len(sys.argv), sys.argv);