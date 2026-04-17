import ply.yacc as yacc
from lexer import tokens, lexer
import pprint

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
    p[0] = {'node': 'program', 'classes': p[1]}

def p_class_list(p):
    '''class_list : class_list class PONTOEVIRGULA
                  | class PONTOEVIRGULA'''
    if len(p) == 4:
        p[1].append(p[2])
        p[0] = p[1]
    else:
        p[0] = [p[1]]

def p_feature_list(p):
    '''feature_list : feature_list feature PONTOEVIRGULA
                    | empty'''
    if len(p) == 4:
        lista = p[1] if p[1] is not None else []
        lista.append(p[2])
        p[0] = lista
    else:        
        p[0] = []

def p_formal_list(p):
    '''formal_list : formal_list VIRGULA formal
                   | formal'''
    if len(p) == 4:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [p[1]]

def p_expr_list(p):
    '''expr_list : expr_list VIRGULA expr
                 | expr'''
    if len(p) == 4:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [p[1]]

def p_expr_list_pontoevirgula(p):
    '''expr_list_pontoevirgula : expr_list_pontoevirgula expr PONTOEVIRGULA
                               | expr PONTOEVIRGULA'''
    if len(p) == 4:
        p[1].append(p[2])
        p[0] = p[1]
    else:
        p[0] = [p[1]]

def p_let_list(p):
    '''let_list : let_list VIRGULA OBJETO DOISPONTOS TIPO ATRIBUICAO expr
                | let_list VIRGULA OBJETO DOISPONTOS TIPO
                | empty'''
    if len(p) == 8:
        novo_binding = {'id': p[3], 'type': p[5], 'value': p[7]}
        lista = p[1] if p[1] is not None else []
        lista.append(novo_binding)
        p[0] = lista
    elif len(p) == 6:
        novo_binding = {'id': p[3], 'type': p[5], 'value': None}
        lista = p[1] if p[1] is not None else []
        lista.append(novo_binding)
        p[0] = lista
    else:
        p[0] = []

def p_case_list(p):
    '''case_list : case_list OBJETO DOISPONTOS TIPO SETACASE expr PONTOEVIRGULA
                 | OBJETO DOISPONTOS TIPO SETACASE expr PONTOEVIRGULA'''
    if len(p) == 8:
        novo_case = {'id': p[2], 'type': p[4], 'expr': p[6]}
        p[1].append(novo_case)
        p[0] = p[1]
    else:
        novo_case = {'id': p[1], 'type': p[3], 'expr': p[5]}
        p[0] = [novo_case]

def p_class(p):
    '''class : CLASS TIPO ABRECHAVES feature_list FECHACHAVES
             | CLASS TIPO INHERITS TIPO ABRECHAVES feature_list FECHACHAVES'''
    if len(p) == 6:
        p[0] = {'node': 'class', 'name': p[2], 'inherits': 'Object', 'features': p[4]}
    else:
        p[0] = {'node': 'class', 'name': p[2], 'features': p[6], 'inherits': p[4]}

def p_feature_method(p):
    '''feature : OBJETO ABREPARENTESES formal_list FECHAPARENTESES DOISPONTOS TIPO ABRECHAVES expr FECHACHAVES
               | OBJETO ABREPARENTESES FECHAPARENTESES DOISPONTOS TIPO ABRECHAVES expr FECHACHAVES'''
    if len(p) == 10:
        p[0] = {'node': 'method', 'name': p[1], 'formals': p[3], 'type': p[6], 'body': p[8]}
    else:
        p[0] = {'node': 'method', 'name': p[1], 'formals': [], 'type': p[5], 'body': p[7]}

def p_feature_attribute(p):
    '''feature : OBJETO DOISPONTOS TIPO ATRIBUICAO expr
               | OBJETO DOISPONTOS TIPO'''
    if len(p) == 6:
        p[0] = {'node': 'attribute', 'name': p[1], 'type': p[3], 'init': p[5]}
    else:
        p[0] = {'node': 'attribute', 'name': p[1], 'type': p[3], 'init': None}

def p_formal(p):
    '''formal : OBJETO DOISPONTOS TIPO'''
    p[0] = {'node': 'formal', 'name': p[1], 'type': p[3]}

def p_empty(p):
    '''empty :'''
    pass

def p_expr_assign(p):
    '''expr : OBJETO ATRIBUICAO expr'''
    p[0] = {'node': 'assign', 'id': p[1], 'expr': p[3]}

def p_expr_static_dispatch(p):
    '''expr : expr ARROBA TIPO PONTO OBJETO ABREPARENTESES expr_list FECHAPARENTESES
            | expr ARROBA TIPO PONTO OBJETO ABREPARENTESES FECHAPARENTESES'''
    if len(p) == 9:
        p[0] = {'node': 'static_dispatch', 'expr': p[1], 'type': p[3], 'id': p[5], 'args': p[7]}
    else:
        p[0] = {'node': 'static_dispatch', 'expr': p[1], 'type': p[3], 'id': p[5], 'args': []}

def p_expr_dispatch(p):
    '''expr : expr PONTO OBJETO ABREPARENTESES expr_list FECHAPARENTESES
            | expr PONTO OBJETO ABREPARENTESES FECHAPARENTESES'''
    if len(p) == 7:
        p[0] = {'node': 'dispatch', 'expr': p[1], 'id': p[3], 'args': p[5]}
    else:
        p[0] = {'node': 'dispatch', 'expr': p[1], 'id': p[3], 'args': []}

def p_expr_self_dispatch(p):
    '''expr : OBJETO ABREPARENTESES expr_list FECHAPARENTESES
            | OBJETO ABREPARENTESES FECHAPARENTESES'''
    if len(p) == 5:
        p[0] = {'node': 'self_dispatch', 'id': p[1], 'args': p[3]}
    else:
        p[0] = {'node': 'self_dispatch', 'id': p[1], 'args': []}

def p_expr_if(p):
    '''expr : IF expr THEN expr ELSE expr FI'''
    p[0] = {'node': 'if', 'condition': p[2], 'then_branch': p[4], 'else_branch': p[6]}

def p_expr_while(p):
    '''expr : WHILE expr LOOP expr POOL'''
    p[0] = {'node': 'while', 'condition': p[2], 'body': p[4]}

def p_expr_block(p):
    '''expr : ABRECHAVES expr_list_pontoevirgula FECHACHAVES'''
    p[0] = {'node': 'block', 'body': p[2]}

def p_expr_let(p):
    '''expr : LET OBJETO DOISPONTOS TIPO ATRIBUICAO expr let_list IN expr
            | LET OBJETO DOISPONTOS TIPO let_list IN expr'''
    if len(p) == 10:
        bindings = [{'id': p[2], 'type': p[4], 'value': p[6]}] + p[7]
        p[0] = {'node': 'let', 'bindings': bindings, 'body': p[9]}
    else:
        bindings = [{'id': p[2], 'type': p[4], 'value': None}] + p[5]
        p[0] = {'node': 'let', 'bindings': bindings, 'body': p[7]}

def p_expr_case(p):
    '''expr : CASE expr OF case_list ESAC'''
    p[0] = {'node': 'case', 'expr': p[2], 'cases': p[4]}

def p_expr_new(p):
    '''expr : NEW TIPO'''
    p[0] = {'node': 'new', 'type': p[2]}

def p_expr_isvoid(p):
    '''expr : ISVOID expr'''
    p[0] = {'node': 'isvoid', 'expr': p[2]}

def p_expr_binop(p):
    '''expr : expr MAIS expr
            | expr MENOS expr
            | expr MULTIPLICACAO expr
            | expr DIVISAO expr
            | expr MENOR expr
            | expr MENORIGUAL expr
            | expr IGUAL expr'''
    p[0] = {'node': 'binop', 'op': p[2], 'left': p[1], 'right': p[3]}

def p_expr_unop(p):
    '''expr : COMPLEMENTO expr
            | NOT expr'''
    p[0] = {'node': 'unop', 'op': p[1], 'expr': p[2]}

def p_expr_parens(p):
    '''expr : ABREPARENTESES expr FECHAPARENTESES'''
    p[0] = p[2]

def p_expr_objeto(p):
    '''expr : OBJETO'''
    p[0] = {'node': 'identifier', 'name': p[1]}

def p_expr_numero(p):
    '''expr : NUMERO'''
    p[0] = {'node': 'integer', 'value': p[1]}

def p_expr_string(p):
    '''expr : STRING'''
    p[0] = {'node': 'string', 'value': p[1]}

def p_expr_bool(p):
    '''expr : BOOL'''
    p[0] = {'node': 'boolean', 'value': p[1]}

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
    
    ast = parser.parse(codigo_teste, lexer=lexer)
    
    print("Análise finalizada! Resultado da AST:\n")
    print("-" * 40)
    
    if ast:
        pprint.pprint(ast, sort_dicts=False, indent=2)
    else:
        print("A AST não foi gerada devido a erros de sintaxe.")