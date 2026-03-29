import ply.lex as lex

tokens = (
    'CLASS', 'ELSE', 'FI', 'IF', 'IN', 'INHERITS', 'THEN', 'ISVOID', 'LET', 'LOOP', 'POOL', 'WHILE', 'CASE', 'ESAC', 'NEW', 'OF', 'NOT',
    'TIPO', 'OBJETO', 'NUMERO', 'STRING', 'BOOL',                                        
    'MAIS', 'MENOS', 'MULTIPLICACAO', 'DIVISAO',
    'IGUAL', 'MENOR', 'MENORIGUAL', 'COMPLEMENTO',
    'DOISPONTOS', 'PONTO', 'VIRGULA', 'PONTOEVIRGULA', 'ABREPARENTESES', 'FECHAPARENTESES', 'ABRECHAVES', 'FECHACHAVES',
    'ATRIBUICAO', 'SETACASE', 'ARROBA',
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
    'not': 'NOT'
}

t_MAIS = r'\+'
t_MENOS = r'-'
t_MULTIPLICACAO = r'\*'
t_DIVISAO = r'/'
t_SETACASE = r'=>'
t_IGUAL = r'='
t_MENORIGUAL = r'<='
t_ATRIBUICAO = r'<-'
t_MENOR = r'<'
t_DOISPONTOS = r':'
t_PONTO = r'\.'
t_VIRGULA = r','
t_PONTOEVIRGULA = r';'
t_ABREPARENTESES = r'\('
t_FECHAPARENTESES = r'\)'
t_ABRECHAVES = r'\{'
t_FECHACHAVES = r'\}'
t_ARROBA = r'@'
t_COMPLEMENTO = r'~'

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
        t.type = 'BOOL'
        return t
        
    t.type = reserved.get(lower_val, 'OBJETO')
    return t

def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'"([^"\\\n]|\\.|\\\n)*"'
    
    if '\0' in t.value:
        print(f"Erro Léxico: String contém caractere nulo na linha {t.lexer.lineno}")
        return
        
    if len(t.value) - 2 > 1024:
        print(f"Erro Léxico: String excede 1024 caracteres na linha {t.lexer.lineno}")
        return

    t.lexer.lineno += t.value.count('\n')

    raw_str = t.value[1:-1]
    processed_str = ""
    i = 0

    while i < len(raw_str):
        if raw_str[i] == '\\':
            i += 1 
            if i < len(raw_str):
                c = raw_str[i]
                if c == 'n':
                    processed_str += '\n'
                elif c == 't':
                    processed_str += '\t'
                elif c == 'b':
                    processed_str += '\b'
                elif c == 'f':
                    processed_str += '\f'
                else:
                    processed_str += c
        else:
            processed_str += raw_str[i]
        i += 1

    t.value = processed_str
    return t

def t_UNMATCHED_COMMENT(t):
    r'\*\)'
    print(f"Erro Léxico: Fechamento de comentário '*)' inesperado na linha {t.lexer.lineno}")

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
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

def t_comment_eof(t):
    print(f"Erro léxico: Comentário não fechado na linha {t.lexer.lineno}")
    return None

def t_string_error_newline(t):
    r'"([^"\\\n]|\\.)*\n'
    print(f"Erro léxico: String não fechada na linha {t.lexer.lineno}")
    t.lexer.lineno += 1

def t_string_error_eof(t):
    r'"([^"\\\n]|\\.)*$'
    print(f"Erro léxico: String não fechada (EOF) na linha {t.lexer.lineno}")

lexer = lex.lex()

if __name__ == '__main__':
    data = r'''
    class Main inherits IO {
        main() : Object {
            out_string("Hello, world \C \0")
            tRuE
            True
        
        };
    };
    -- Comentário de uma linha
    *)
    (* Comentário de múltiplas linhas
       com aninhamento (* comentário aninhado *)
    '''

    lexer.input(data)
    
    for tok in lexer:
        print(tok)