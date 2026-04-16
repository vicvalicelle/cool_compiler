import ply.yacc as yacc
from lexer import tokens, lexer

precedence = (
    ('right', 'ATRIBUICAO'),
    ('left', 'NOT'),
    ('nonassoc', 'MENORIGUAL', 'MENOR', 'IGUAL'),
    ('left', 'MAIS', 'MENOS'),
    ('left', 'MULTIPLICACAO', 'DIVISAO'),
    ('left', 'ISVOID'),
    ('left', 'COMPLEMENTO'),
    ('left', 'ARROBA'),
    ('left', 'PONTO')
)

def p_program(p):
   '''program : class_list'''
   pass

def p_class_list(p):
   '''class_list : class PONTOEVIRGULA class_list
                 | class PONTOEVIRGULA'''
   pass

def p_class(p):
    '''class : CLASS TIPO ABRECHAVES feature_list FECHACHAVES
             | CLASS TIPO INHERITS TIPO ABRECHAVES feature_list FECHACHAVES'''
    pass

def p_feature_list(p):
    '''feature_list : feature PONTOEVIRGULA feature_list
                    | empty'''
    pass

def p_feature(p):
    '''feature : OBJETO ABREPARENTESES formal_list FECHAPARENTESES DOISPONTOS TIPO ABRECHAVES expr FECHACHAVES
               | OBJETO ABREPARENTESES FECHAPARENTESES DOISPONTOS TIPO ABRECHAVES expr FECHACHAVES
               | OBJETO DOISPONTOS TIPO ATRIBUICAO expr
               | OBJETO DOISPONTOS TIPO'''
    pass

def p_formal_list(p):
    '''formal_list : formal VIRGULA formal_list
                   | formal'''
    pass

def p_formal(p):
    '''formal : OBJETO DOISPONTOS TIPO'''
    pass

def p_empty(p):
    '''empty :'''
    pass

def p_expr(p):
    '''expr : OBJETO ATRIBUICAO expr
            | expr ARROBA TIPO PONTO OBJETO ABREPARENTESES expr_list FECHAPARENTESES
            | expr ARROBA TIPO PONTO OBJETO ABREPARENTESES FECHAPARENTESES
            | expr PONTO OBJETO ABREPARENTESES expr_list FECHAPARENTESES
            | expr PONTO OBJETO ABREPARENTESES FECHAPARENTESES
            | OBJETO ABREPARENTESES expr_list FECHAPARENTESES
            | OBJETO ABREPARENTESES FECHAPARENTESES
            | IF expr THEN expr ELSE expr FI
            | WHILE expr LOOP expr POOL
            | ABRECHAVES expr_list_pontoevirgula FECHACHAVES 
            | LET OBJETO DOISPONTOS TIPO ATRIBUICAO expr let_list IN expr
            | LET OBJETO DOISPONTOS TIPO let_list IN expr
            | CASE expr OF case_list ESAC
            | NEW TIPO
            | ISVOID expr
            | expr MAIS expr
            | expr MENOS expr
            | expr MULTIPLICACAO expr
            | expr DIVISAO expr
            | COMPLEMENTO expr
            | expr MENOR expr
            | expr MENORIGUAL expr
            | expr IGUAL expr
            | NOT expr
            | ABREPARENTESES expr FECHAPARENTESES
            | OBJETO
            | NUMERO
            | STRING
            | BOOL'''
    pass

def p_expr_list(p):
    '''expr_list : expr VIRGULA expr_list
                 | expr'''
    pass

def p_expr_list_pontoevirgula(p):
    '''expr_list_pontoevirgula : expr PONTOEVIRGULA expr_list_pontoevirgula
                                | expr PONTOEVIRGULA'''
    pass

def p_let_list(p):
    '''let_list : VIRGULA OBJETO DOISPONTOS TIPO ATRIBUICAO expr let_list
                | VIRGULA OBJETO DOISPONTOS TIPO let_list
                | empty'''
    pass

def p_case_list(p):
    '''case_list : OBJETO DOISPONTOS TIPO SETACASE expr PONTOEVIRGULA case_list
                 | OBJETO DOISPONTOS TIPO SETACASE expr PONTOEVIRGULA'''
    pass

def p_error(p):
    if p:
        print(f"Erro de sintaxe próximo ao token '{p.value}' na linha {p.lineno}")
    else:
        print("Erro de sintaxe no final do arquivo")

parser = yacc.yacc()

if __name__ == '__main__':
    codigo_teste = r'''
    class Main inherits IO {
        x : Int <- 10;
        
        main() : Object {
            {
                out_string("Hello, world\n");
                while x < 20 loop
                    x <- x + 1
                pool;
                
                if isvoid x then
                    out_string("Vazio")
                else
                    out_string("Cheio")
                fi;
            }
        };
    };
    '''

    print("Iniciando a análise sintática...")
    
    parser.parse(codigo_teste, lexer=lexer)
    
    print("Análise finalizada!")