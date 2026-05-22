from parser import parser
from lexer import lexer

class SemanticAnalyzer:

    def __init__(self, ast):
        self.ast = ast
        self.errors = []
        self.class_table = {}
        self.symbol_table = [{}]
        self.setup_basic_classes()

    def setup_basic_classes(self):
        self.class_table['Object'] = {
            'name': 'Object',
            'inherits': None, 
            'methods': {
                'abort': {'formals': [], 'return_type': 'Object'},
                'type_name': {'formals': [], 'return_type': 'String'},
                'copy': {'formals': [], 'return_type': 'SELF_TYPE'}
            }
        }

        self.class_table['IO'] = {
            'name': 'IO',
            'inherits': 'Object',
            'methods': {
                'out_string': {'formals': [('x', 'String')], 'return_type': 'SELF_TYPE'},
                'out_int': {'formals': [('x', 'Int')], 'return_type': 'SELF_TYPE'},
                'in_string': {'formals': [], 'return_type': 'String'},
                'in_int': {'formals': [], 'return_type': 'Int'}
            }
        }

        self.class_table['Int'] = {
            'name': 'Int',
            'inherits': 'Object',
            'methods': {}
        }

        self.class_table['String'] = {
            'name': 'String',
            'inherits': 'Object',
            'methods': {
                'length': {'formals': [], 'return_type': 'Int'},
                'concat': {'formals': [('s', 'String')], 'return_type': 'String'},
                'substr': {'formals': [('i', 'Int'), ('l', 'Int')], 'return_type': 'String'}
            }
        }

        self.class_table['Bool'] = {
            'name': 'Bool',
            'inherits': 'Object',
            'methods': {}
        }
        pass

    def analyze(self):
        self.visit_program(self.ast)
        self.check_cycles()

        if self.errors:
            print("Erros semânticos:")
            for error in self.errors:
                print(error)
        else:
            print("Programa semanticamente estruturado e correto")

    def visit_class(self, node):
        class_name = node['name']
        parent_name = node.get('inherits', 'Object')

        if class_name in self.class_table:
            self.errors.append(f"Classe '{class_name}' redefinida")
            return
        
        if class_name in ['Int', 'String', 'Bool', 'Object', 'IO']:
            self.errors.append(f"Redefinição da classe básica '{class_name}' não é permitida")
            return
            
        if parent_name in ['Int', 'String', 'Bool']:
            self.errors.append(f"Classe '{class_name}' não pode herdar de '{parent_name}'")

        self.class_table[class_name] = node

    def visit_program(self, node):
        for cls in node['classes']:
            self.visit_class(cls)

        if 'Main' not in self.class_table:
            self.errors.append("Classe 'Main' não foi encontrada no programa.")
    
    def enter_scope(self):
        self.symbol_table.append({})
    
    def define_variable(self, name, var_type):
        self.symbol_table[-1][name] = var_type
    
    def lookup_variable(self, name):
        for scope in reversed(self.symbol_table):
            if name in scope:
                return scope[name]
        return None

    def exit_scope(self):
        self.symbol_table.pop()