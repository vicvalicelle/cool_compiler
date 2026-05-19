from parser import parser
from lexer import lexer

class SemanticAnalyzer:

    def __init__(self, ast):
        self.ast = ast
        self.errors = []
        self.class_table = {}
        self.symbol_table = [{}]

    def analyze(self):
        self.visit_program(self.ast)
        if self.errors:
            print("Erros semânticos:")
            for error in self.errors:
                print(error)
        else:
            print("Programa semanticamente correto")

    def visit_class(self, node):
        class_name = node['name']
        if class_name in self.class_table:
            self.errors.append(
                f"Classe '{class_name}' redefinida"
            )
        else:
            self.class_table[class_name] = node

    def visit_program(self, node):
        for cls in node['classes']:
            self.visit_class(cls)
    
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