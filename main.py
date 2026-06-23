from lexer import lexer
from parser import parser
from semantic import SemanticAnalyzer
from codegen import BrilGenerator 

codigo_cool = r"""
    class Main {
        main(): Int {
            let x: Int <- 10,
                y: Int <- 20,
                result: Int
            in
                if x < y then
                    result <- x + y
                else
                    result <- x - y
                fi
        };
    };
"""

ast = parser.parse(codigo_cool, lexer=lexer)

if ast:
    analisador = SemanticAnalyzer(ast)
    analisador.analyze()
    
    if analisador.errors:
        print("Erros Semânticos encontrados")
    else:
        print("Gerando código Bril...")
        gerador = BrilGenerator()
        codigo_bril = gerador.generate(ast)
        
        print("\n" + "="*40)
        print("        CÓDIGO BRIL GERADO        ")
        print("="*40)
        print(codigo_bril)
        print("="*40)
        
        with open("programa.bril", "w") as f:
            f.write(codigo_bril)
        print("\n✓ Código salvo em 'programa.bril'")