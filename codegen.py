class BrilGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0
        self.current_class = None

        # pilha de escopos
        self.env = [{}]

        # contador para renomeação
        self.var_count = 0

    # -----------------------------------
    # utilitários
    # -----------------------------------

    def new_temp(self):
        self.temp_count += 1
        return f"v{self.temp_count}"
    
    def new_label(self, prefix):
        self.label_count += 1
        return f".{prefix}.{self.label_count}"

    def emit(self, line):
        self.code.append(line)

    def emit_label(self, label):
        self.code.append(f"{label}:")

    def generate(self, ast):
        self.visit(ast)
        return "\n".join(self.code)

    def visit(self, node):
        if node is None:
            return None

        method_name = f"visit_{node['node']}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(
            f"Gerador não implementado para nó '{node['node']}'"
        )
    
    # -----------------------------------
    # gerenciamento de escopo e tipos
    # -----------------------------------

    def enter_scope(self):
        self.env.append({})

    def exit_scope(self):
        self.env.pop()

    def new_variable(self, cool_name):
        self.var_count += 1
        return f"{cool_name}_{self.var_count}"

    def define_variable(self, cool_name, bril_type):
        bril_name = self.new_variable(cool_name)
        self.env[-1][cool_name] = (bril_name, bril_type)
        return bril_name

    def lookup_variable(self, cool_name):
        for scope in reversed(self.env):
            if cool_name in scope:
                return scope[cool_name]
        raise Exception(f"Variável '{cool_name}' não encontrada.")

    def cool_to_bril_type(self, cool_type):
        mapping = {
            "Int": "int",
            "Bool": "bool"
        }
        return mapping.get(cool_type, "Object")
    
    # -----------------------------------
    # programa
    # -----------------------------------

    def visit_program(self, node):
        for cls in node["classes"]:
            self.visit(cls)
        return None, None

    def visit_class(self, node):
        self.current_class = node["name"]
        for feature in node["features"]:
            self.visit(feature)
        self.current_class = None
        return None, None

    def visit_method(self, node):
        if self.current_class == "Main" and node["name"] == "main":
            method_name = "main"
        else:
            method_name = f"{self.current_class}_{node['name']}"

        self.emit(f"@{method_name} {{")
        self.enter_scope()

        result_var, result_type = self.visit(node["body"])

        if result_var:
            self.emit(f"  print {result_var};")

        self.exit_scope()

        self.emit("}")
        self.emit("")
        
        return None, None

    # -----------------------------------
    # Expressões e Variáveis Locais
    # -----------------------------------

    def visit_let(self, node):
        self.enter_scope()

        for binding in node["bindings"]:
            cool_name = binding["id"]
            bril_type = self.cool_to_bril_type(binding["type"])
            
            bril_name = self.define_variable(cool_name, bril_type)

            if binding["value"] is not None:
                value_var, value_type = self.visit(binding["value"])
                self.emit(f"  {bril_name}: {bril_type} = id {value_var};")
            else:
                if bril_type == "int":
                    self.emit(f"  {bril_name}: int = const 0;")
                elif bril_type == "bool":
                    self.emit(f"  {bril_name}: bool = const false;")

        result_var, result_type = self.visit(node["body"])
        
        self.exit_scope()
        return result_var, result_type

    def visit_assign(self, node):
        expr_var, expr_type = self.visit(node["expr"])
        target_var, target_type = self.lookup_variable(node["id"])

        self.emit(f"  {target_var}: {target_type} = id {expr_var};")
        return target_var, target_type

    def visit_identifier(self, node):
        return self.lookup_variable(node["name"])
    
    # -----------------------------------
    # literais
    # -----------------------------------

    def visit_integer(self, node):
        temp = self.new_temp()
        self.emit(f"  {temp}: int = const {node['value']};")
        return temp, "int"

    def visit_boolean(self, node):
        temp = self.new_temp()
        value = "true" if node["value"] else "false"
        self.emit(f"  {temp}: bool = const {value};")
        return temp, "bool"

    # -----------------------------------
    # operações binárias
    # -----------------------------------

    def visit_binop(self, node):
        left_var, left_type = self.visit(node["left"])
        right_var, right_type = self.visit(node["right"])

        if left_type != right_type:
            raise ValueError("Tipos incompatíveis na operação binária")

        result = self.new_temp()

        bril_ops = {
            "+": "add",
            "-": "sub",
            "*": "mul",
            "/": "div",
            "<": "lt",
            "<=": "le",
            "=": "eq",
        }
        
        op = bril_ops[node["op"]]

        ret_type = "bool" if op in ["lt", "le", "eq"] else "int"

        self.emit(f"  {result}: {ret_type} = {op} {left_var} {right_var};")

        return result, ret_type

    # -----------------------------------
    # parênteses
    # -----------------------------------

    def visit_parens(self, node):
        return self.visit(node["expr"])
    
    # -----------------------------------
    # controle de fluxo (if e while)
    # -----------------------------------

    def visit_if(self, node):
        cond_var, cond_type = self.visit(node["condition"])

        if cond_type != "bool":
            raise Exception(f"If espera condição bool, recebeu {cond_type}")

        then_label = self.new_label("then")
        else_label = self.new_label("else")
        end_label = self.new_label("end")

        result_var = self.new_temp()

        self.emit(f"  br {cond_var} {then_label} {else_label};")

        # ---------- THEN ----------
        self.emit_label(then_label)
        then_var, then_type = self.visit(node["then_branch"])
        
        self.emit(f"  {result_var}: {then_type} = id {then_var};")
        self.emit(f"  jmp {end_label};")

        # ---------- ELSE ----------
        self.emit_label(else_label)
        else_var, else_type = self.visit(node["else_branch"])

        if then_type != else_type:
            raise Exception(
                f"If produz tipos diferentes "
                f"({then_type} e {else_type})"
            )

        self.emit(f"  {result_var}: {else_type} = id {else_var};")
        self.emit(f"  jmp {end_label};")

        # ---------- END ----------
        self.emit_label(end_label)

        return result_var, then_type

    def visit_while(self, node):
        loop_label = self.new_label("loop")
        body_label = self.new_label("body")
        end_label = self.new_label("endloop")

        self.emit(f"  jmp {loop_label};")

        # ---------- TESTE ----------
        self.emit_label(loop_label)
        cond_var, cond_type = self.visit(node["condition"])

        if cond_type != "bool":
            raise Exception(f"While espera condição bool, recebeu {cond_type}")

        self.emit(f"  br {cond_var} {body_label} {end_label};")

        # ---------- CORPO ----------
        self.emit_label(body_label)
        self.visit(node["body"])
        
        self.emit(f"  jmp {loop_label};")

        # ---------- FIM ----------
        self.emit_label(end_label)

        return None, "Object"