import ply.lex as lex

tokens = (
    'CLASS', 'ELSE', 'FALSE', 'FI', 'IF', 'IN', 'INHERITS', 'ISVOID', 'LET', 'LOOP', 'POOL', 'THEN', 'WHILE', 'CASE', 'ESAC', 'NEW', 'OF', 'NOT', 'TRUE',
    'TIPO', 'OBJETO',                         
    'NUMERO', 'STRING', 'BOOL',                                
    'MAIS', 'MENOS', 'MULTIPLICACAO', 'DIVISAO',
    'IGUAL', 'MENOR', 'MAIOR', 'MENORIGUAL', 'MAIORIGUAL',
    'DOISPONTOS', 'PONTO', 'VIRGULA', 'PONTOEVIRGULA', 'LPARENTESES', 'RPARENTESES', 'LCHAVES', 'RCHAVES', 'ATRIBUICAO', 'SETACASE', 'ARROBA', 'TILDE'
)

reserved = {
    'class': 'CLASS',
    'else': 'ELSE',
    'fi': 'FI',
    'if': 'IF',
    'in': 'IN',
    'inherits': 'INHERITS',
    'then': 'THEN',
    'isvoid': 'ISVOID',
    'let': 'LET',
    'loop': 'LOOP',
    'pool': 'POOL',
    'while': 'WHILE',
    'case': 'CASE',
    'esac': 'ESAC',
    'new': 'NEW',
    'of': 'OF',
    'not': 'NOT',
    'true': 'TRUE',
    'false': 'FALSE'
}

t_MAIS = r'\+'
t_MENOS = r'-'
t_MULTIPLICACAO = r'\*'
t_DIVISAO = r'/'
t_IGUAL = r'='
t_MENOR = r'<'
t_MAIOR = r'>'
t_MENORIGUAL = r'<='
t_MAIORIGUAL = r'>='
t_DOISPONTOS = r':'
t_PONTO = r'\.'
t_VIRGULA = r','
t_PONTOEVIRGULA = r';'
t_LPARENTESES = r'\('
t_RPARENTESES = r'\)'
t_LCHAVES = r'\{'
t_RCHAVES = r'\}'
t_ATRIBUICAO = r'<-'
t_SETACASE = r'=>'
t_ARROBA = r'@'
t_TILDE = r'~'

states = (
    ('comment', 'exclusive'),
)

def t_TIPO(t):
    r'[A-Z][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'TIPO')
    return t

def t_OBJETO(t):
    r'[a-z][a-zA-Z0-9_]*'
    lower_val = t.value.lower()
    if lower_val in ('true', 'false'):
        if t.value.islower():
            t.type = 'BOOL'
            return t
    t.type = reserved.get(lower_val, 'OBJETO')
    return t

def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'"([^"\\\n]|\\.)*"'
    
    if '\0' in t.value:
        print(f"Erro Léxico: String contém caractere nulo na linha {t.lexer.lineno}")
        t.lexer.skip(1)
        return
        
    if len(t.value) - 2 > 1024:
        print(f"Erro Léxico: String excede 1024 caracteres na linha {t.lexer.lineno}")
        t.lexer.skip(1)
        return
        
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore  = ' \t\r\f\v'
t_comment_ignore = ' \t\r\f\v'

def t_COMMENTLINE(t):
    r'--.*'
    pass

def t_start_comment(t):
    r'\(\*'
    t.lexer.comment_level = 1
    t.lexer.begin('comment')

def t_comment_start_inner(t):
    r'\(\*'
    t.lexer.comment_level += 1

def t_comment_end(t):
    r'\*\)'
    t.lexer.comment_level -= 1
    if t.lexer.comment_level == 0:
        t.lexer.begin('INITIAL')

def t_comment_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_comment_error(t):
    t.lexer.skip(1)

def t_error(t):
    print(f"Caractere ilegal '{t.value}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

if __name__ == '__main__':
    data = r'''
    class Main inherits IO {
        main() : Object {
            out_string("Hello, world.\n")
            let x : Int <- 5;
            if x > 0 then
        };
    };
    -- Comentário de uma linha
    (* Comentário de múltiplas linhas
       com aninhamento (* comentário aninhado *) *)
    '''

    lexer.input(data)
    
    for tok in lexer:
        print(tok)