from parser import parser
from lexer import lexer

class SemanticAnalyzer:

    def __init__(self, ast):
        self.ast = ast
        self.errors = []
        self.class_table = {}
        self.symbol_table = [{}]
        self.current_class = None
        self.setup_basic_classes()

    def setup_basic_classes(self):
        self.class_table['Object'] = {
            'name': 'Object',
            'inherits': None, 
            'methods': {
                'abort': {'formals': [], 'type': 'Object'},
                'type_name': {'formals': [], 'type': 'String'},
                'copy': {'formals': [], 'type': 'SELF_TYPE'}
            }
        }

        self.class_table['IO'] = {
            'name': 'IO',
            'inherits': 'Object',
            'methods': {
                'out_string': {'formals': [{'name':'x', 'type':'String'}], 'type': 'SELF_TYPE'},
                'out_int': {'formals': [{'name':'x', 'type':'Int'}], 'type': 'SELF_TYPE'},
                'in_string': {'formals': [], 'type': 'String'},
                'in_int': {'formals': [], 'type': 'Int'}
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
                'length': {'formals': [], 'type': 'Int'},
                'concat': {'formals': [{'name':'s', 'type':'String'}], 'type': 'String'},
                'substr': {'formals': [{'name':'i', 'type':'Int'}, {'name':'l', 'type':'Int'}], 'type': 'String'}
            }
        }

        self.class_table['Bool'] = {
            'name': 'Bool',
            'inherits': 'Object',
            'methods': {}
        }

    def analyze(self):
        self.visit_program(self.ast)
        self.check_cycles()

        if not self.errors:
            self.type_check_program(self.ast)

        if self.errors:
            print("\n❌ Erros semânticos:")
            for error in self.errors:
                print(error)
        else:
            print("\n✅ Programa semanticamente estruturado e correto!")

    def visit_class(self, node):
        class_name = node['name']
        parent_name = node.get('inherits', 'Object')

        if class_name in self.class_table:
            self.errors.append(f"Linha {node.get('line', '?')}: Classe '{class_name}' redefinida.")
            return
        
        if class_name in ['Int', 'String', 'Bool', 'Object', 'IO']:
            self.errors.append(f"Linha {node.get('line', '?')}: Redefinição da classe básica '{class_name}' não é permitida.")
            return
            
        if parent_name in ['Int', 'String', 'Bool']:
            self.errors.append(f"Linha {node.get('line', '?')}: Classe '{class_name}' não pode herdar de tipo básico '{parent_name}'.")

        self.class_table[class_name] = node

    def visit_program(self, node):
        for cls in node['classes']:
            self.visit_class(cls)

        if 'Main' not in self.class_table:
            self.errors.append("Classe 'Main' não foi encontrada no programa.")

    def check_cycles(self):
        for class_name in self.class_table:
            if class_name in ['Object', 'Int', 'String', 'Bool', 'IO']:
                continue
                
            path = set()
            current = class_name
            
            while current and current != 'Object':
                if current in path:
                    self.errors.append(f"Ciclo de herança detetado a envolver a classe '{current}'")
                    break
                
                path.add(current)
                
                node = self.class_table.get(current)
                if not node:
                    self.errors.append(f"Classe pai '{current}' não encontrada")
                    break
                    
                current = node.get('inherits', 'Object')

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

    def is_subtype(self, type1, type2):
        if type1 == type2: return True
        if type2 == 'Object': return True
        if type2 == 'SELF_TYPE': return False 

        curr_t1 = self.current_class if type1 == 'SELF_TYPE' else type1

        current = curr_t1
        while current and current != 'Object':
            if current == type2:
                return True
            node = self.class_table.get(current)
            if not node: break
            current = node.get('inherits', 'Object')
        return False

    def find_lca(self, type1, type2):
        if type1 == type2: return type1
        
        t1 = self.current_class if type1 == 'SELF_TYPE' else type1
        t2 = self.current_class if type2 == 'SELF_TYPE' else type2
        
        path = set()
        curr = t1
        while curr:
            path.add(curr)
            if curr == 'Object': break
            curr = self.class_table.get(curr, {}).get('inherits', 'Object')
            
        curr = t2
        while curr:
            if curr in path:
                return curr
            if curr == 'Object': break
            curr = self.class_table.get(curr, {}).get('inherits', 'Object')
            
        return 'Object'

    def lookup_method(self, class_name, method_name):
        curr = class_name
        while curr:
            cls_node = self.class_table.get(curr)
            if not cls_node: break
            
            if 'methods' in cls_node and method_name in cls_node['methods']:
                return cls_node['methods'][method_name]
                
            if 'features' in cls_node:
                for feature in cls_node['features']:
                    if feature['node'] == 'method' and feature['name'] == method_name:
                        return feature
                        
            curr = cls_node.get('inherits', 'Object')
        return None

    def type_check_program(self, node):
        for cls in node['classes']:
            self.current_class = cls['name']

            seen_methods = set()
            for feature in cls.get('features', []):
                if feature['node'] == 'method':
                    fname = feature['name']
                    if fname in seen_methods:
                        self.errors.append(f"Linha {feature.get('line', '?')}: redefinição de método na mesma classe.")
                    seen_methods.add(fname)

            self.enter_scope()
            self.define_variable('self', 'SELF_TYPE')
            
            curr = self.current_class
            while curr:
                curr_node = self.class_table.get(curr)
                if not curr_node: break
                
                for feature in curr_node.get('features', []):
                    if feature['node'] == 'attribute':
                        if not self.lookup_variable(feature['name']):
                            self.define_variable(feature['name'], feature['type'])
                            
                curr = curr_node.get('inherits', 'Object')

            for feature in cls.get('features', []):
                self.visit_feature(feature)
                
            self.exit_scope()
            
        main_class = self.class_table.get('Main')
        if main_class:
            main_method = self.lookup_method('Main', 'main')
            if not main_method:
                self.errors.append("Classe 'Main' deve conter um método 'main'.")
            elif len(main_method['formals']) > 0:
                self.errors.append("O método 'main' da classe 'Main' não pode receber parâmetros.")

    def visit_feature(self, node):
        if node['node'] == 'attribute':
            if node['name'] == 'self':
                self.errors.append(f"Linha {node.get('line', '?')}: atributo não pode se chamar self.")

            parent = self.class_table.get(self.current_class, {}).get('inherits', 'Object')
            curr = parent
            while curr:
                p_node = self.class_table.get(curr)
                if not p_node: break
                for feat in p_node.get('features', []):
                    if feat['node'] == 'attribute' and feat['name'] == node['name']:
                        self.errors.append(f"Linha {node['line']}: Atributo '{node['name']}' não pode ser redefinido (já existe na classe ascendente '{curr}').")
                curr = p_node.get('inherits', 'Object')

            if node['init']:
                init_type = self.visit_expr(node['init'])
                if init_type and not self.is_subtype(init_type, node['type']):
                    self.errors.append(f"Linha {node['line']}: Tipo inferido '{init_type}' não está em conformidade com o tipo declarado '{node['type']}' no atributo '{node['name']}'.")
                    
        elif node['node'] == 'method':
            parent = self.class_table.get(self.current_class, {}).get('inherits', 'Object')
            parent_method = self.lookup_method(parent, node['name'])
            
            if parent_method:
                if len(parent_method['formals']) != len(node['formals']):
                    self.errors.append(f"Linha {node['line']}: Método '{node['name']}' redefinido com número diferente de parâmetros.")
                else:
                    for pf, f in zip(parent_method['formals'], node['formals']):
                        p_t = pf['type'] if isinstance(pf, dict) else pf[1]
                        if p_t != f['type']:
                            self.errors.append(f"Linha {node['line']}: Parâmetro '{f['name']}' do método '{node['name']}' muda de tipo na redefinição.")
                
                if parent_method['type'] != node['type']:
                    self.errors.append(f"Linha {node['line']}: Tipo de retorno do método '{node['name']}' difere da classe ascendente.")

            self.enter_scope()
            
            seen_formals = set()
            for formal in node['formals']:
                if formal['name'] == 'self':
                    self.errors.append(f"Linha {node['line']}: 'self' não pode ser usado como nome de parâmetro.")
                
                if formal['type'] == 'SELF_TYPE':
                    self.errors.append(f"Linha {node['line']}: SELF_TYPE não pode ser usado como tipo de parâmetro formal.")
                
                if formal['name'] in seen_formals:
                    self.errors.append(f"Linha {node['line']}: parâmetros formais duplicados.")
                    
                seen_formals.add(formal['name'])
                self.define_variable(formal['name'], formal['type'])
                
            return_type = self.visit_expr(node['body'])
            
            if return_type and not self.is_subtype(return_type, node['type']):
                self.errors.append(f"Linha {node['line']}: Tipo retornado '{return_type}' não está em conformidade com '{node['type']}' no método '{node['name']}'.")
                
            self.exit_scope()

    def visit_expr(self, node):
        if not isinstance(node, dict) or 'node' not in node:
            return 'Object'
            
        n_type = node['node']
        line = node.get('line', '?')
        
        if n_type == 'integer': return 'Int'
        elif n_type == 'string': return 'String'
        elif n_type == 'boolean': return 'Bool'
            
        elif n_type == 'identifier':
            var_type = self.lookup_variable(node['name'])
            if not var_type:
                self.errors.append(f"Linha {line}: Identificador '{node['name']}' não declarado neste âmbito.")
                return 'Object'
            return var_type
            
        elif n_type == 'assign':
            if node['id'] == 'self':
                self.errors.append(f"Linha {line}: Não é possível atribuir um valor à variável reservada 'self'.")
                
            expr_type = self.visit_expr(node['expr'])
            var_type = self.lookup_variable(node['id'])
            if not var_type:
                self.errors.append(f"Linha {line}: Atribuição a variável não declarada '{node['id']}'.")
            elif expr_type and not self.is_subtype(expr_type, var_type):
                self.errors.append(f"Linha {line}: Tipo '{expr_type}' incompatível com variável '{node['id']}' do tipo '{var_type}'.")
            return expr_type
            
        elif n_type == 'binop':
            left_t = self.visit_expr(node['left'])
            right_t = self.visit_expr(node['right'])
            
            if node['op'] in ['+', '-', '*', '/']:
                if left_t != 'Int' or right_t != 'Int':
                    self.errors.append(f"Linha {line}: Operação '{node['op']}' requer operandos Int (recebeu {left_t} e {right_t}).")
                return 'Int'
            
            elif node['op'] in ['<', '<=']:
                if left_t != 'Int' or right_t != 'Int':
                    self.errors.append(f"Linha {line}: Operação relacional requer Int.")
                return 'Bool'
                
            elif node['op'] == '=':
                basicos = ['Int', 'String', 'Bool']
                if left_t in basicos or right_t in basicos:
                    if left_t != right_t:
                        self.errors.append(f"Linha {line}: Comparação '=' ilegal entre tipos básicos diferentes.")
                return 'Bool'
                
        elif n_type == 'unop':
            expr_t = self.visit_expr(node['expr'])
            if node['op'] == 'not':
                if expr_t != 'Bool': self.errors.append(f"Linha {line}: 'not' requer Bool.")
                return 'Bool'
            elif node['op'] == '~':
                if expr_t != 'Int': self.errors.append(f"Linha {line}: '~' requer Int.")
                return 'Int'
                
        elif n_type == 'if':
            cond_t = self.visit_expr(node['condition'])
            if cond_t != 'Bool':
                self.errors.append(f"Linha {line}: Condição do 'if' deve ser Bool.")
            then_t = self.visit_expr(node['then_branch'])
            else_t = self.visit_expr(node['else_branch'])
            return self.find_lca(then_t, else_t)
            
        elif n_type == 'while':
            cond_t = self.visit_expr(node['condition'])
            if cond_t != 'Bool':
                self.errors.append(f"Linha {line}: Condição do 'while' deve ser Bool.")
            self.visit_expr(node['body'])
            return 'Object'
            
        elif n_type == 'block':
            last_type = 'Object'
            for expr in node['body']:
                last_type = self.visit_expr(expr)
            return last_type
            
        elif n_type == 'let':
            self.enter_scope()
            for binding in node['bindings']:
                if binding['id'] == 'self':
                    self.errors.append(f"Linha {line}: 'self' não pode ser usado como variável num 'let'.")
                    
                bind_t = binding['type']
                if binding['value']:
                    val_t = self.visit_expr(binding['value'])
                    if not self.is_subtype(val_t, bind_t):
                        self.errors.append(f"Linha {line}: Tipo '{val_t}' não pode ser atribuído a '{binding['id']}' de tipo '{bind_t}' no let.")
                self.define_variable(binding['id'], bind_t)
            
            body_t = self.visit_expr(node['body'])
            self.exit_scope()
            return body_t
            
        elif n_type == 'case':
            self.visit_expr(node['expr'])
            branch_types = []
            declared_branch_types = set()
            
            for branch in node['cases']:
                b_type = branch['type']
                if b_type in declared_branch_types:
                    self.errors.append(f"Linha {branch.get('line', line)}: branches do case devem ter tipos distintos.")
                declared_branch_types.add(b_type)

                self.enter_scope()
                if branch['id'] == 'self':
                    self.errors.append(f"Linha {branch.get('line', line)}: 'self' não pode ser usado como variável num 'case'.")
                self.define_variable(branch['id'], branch['type'])
                branch_types.append(self.visit_expr(branch['expr']))
                self.exit_scope()
                
            res_type = branch_types[0] if branch_types else 'Object'
            for t in branch_types[1:]:
                res_type = self.find_lca(res_type, t)
            return res_type
            
        elif n_type == 'new':
            if node['type'] == 'SELF_TYPE':
                return 'SELF_TYPE'
                
            if node['type'] not in self.class_table:
                self.errors.append(f"Linha {line}: Uso de 'new' com classe desconhecida '{node['type']}'.")
                return 'Object'
            return node['type']
            
        elif n_type == 'isvoid':
            self.visit_expr(node['expr'])
            return 'Bool'
            
        elif n_type in ['dispatch', 'self_dispatch', 'static_dispatch']:
            if n_type == 'self_dispatch':
                caller_type = 'SELF_TYPE'
                dispatch_class = self.current_class
            else:
                caller_type = self.visit_expr(node['expr'])
                dispatch_class = self.current_class if caller_type == 'SELF_TYPE' else caller_type
                
            if n_type == 'static_dispatch':
                if not self.is_subtype(caller_type, node['type']):
                    self.errors.append(f"Linha {line}: Dispatch estático inválido. '{caller_type}' não é subtipo de '{node['type']}'.")
                dispatch_class = node['type']

            method_name = node['id']
            method_def = self.lookup_method(dispatch_class, method_name)
            
            if not method_def:
                self.errors.append(f"Linha {line}: Método '{method_name}' não encontrado na classe '{dispatch_class}'.")
                return 'Object'
                
            formals = method_def['formals']
            args = node['args']
            
            if len(formals) != len(args):
                self.errors.append(f"Linha {line}: Método '{method_name}' chamado com {len(args)} argumentos, mas requer {len(formals)}.")
            else:
                for formal, arg in zip(formals, args):
                    arg_t = self.visit_expr(arg)
                    formal_t = formal['type'] if isinstance(formal, dict) else formal[1]
                    if not self.is_subtype(arg_t, formal_t):
                        self.errors.append(f"Linha {line}: Argumento do tipo '{arg_t}' incompatível com tipo esperado '{formal_t}'.")
            
            ret_type = method_def['type']
            return caller_type if ret_type == 'SELF_TYPE' else ret_type

        elif n_type == 'parens':
            return self.visit_expr(node['expr'])

        return 'Object'