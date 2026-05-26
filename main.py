from lexer import lexer
from parser import parser
from semantic import SemanticAnalyzer






codigo_cool = r"""
    class Main inherits IO {
        main(): Object {
            let hello: String <- "Hello, ",
                name: String <- "",
                ending: String <- "!\n"
            in {
                out_string("Please enter your name:\n");
                name <- in_string();
                out_string(hello.concat(name.concat(ending)));
            }
        };
    };
"""

ast = parser.parse(codigo_cool, lexer=lexer)

if ast:
    analisador = SemanticAnalyzer(ast)
    analisador.analyze()