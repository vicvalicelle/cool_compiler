class BrilGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.current_class = None

        # tabela simples de variáveis -> tipo bril
        self.env = {}

    # -----------------------------------
    # utilitários
    # -----------------------------------

    def new_temp(self):
        self.temp_count += 1
        return f"v{self.temp_count}"

    def emit(self, line):
        self.code.append(line)

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

        result = self.visit(node["body"])

        result_var, result_type = self.visit(node["body"])

        if result_var:
            self.emit(f"  print {result_var};")

        self.emit("}")
        self.emit("")
        
        return None, None

    # -----------------------------------
    # literais
    # -----------------------------------

    def visit_integer(self, node):
        temp = self.new_temp()

        self.emit(
            f"{temp}: int = const {node['value']};"
        )

        return temp, "int"

    def visit_boolean(self, node):
        temp = self.new_temp()

        value = "true" if node["value"] else "false"

        self.emit(
            f"{temp}: bool = const {value};"
        )

        return temp, "bool"

    # -----------------------------------
    # identificadores
    # -----------------------------------

    def visit_identifier(self, node):
        var_name = node["name"]

        var_type = "int"

        return var_name, var_type

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
        }

        op = bril_ops[node["op"]]

        self.emit(
            f"{result}: int = {op} {left_var} {right_var};"
        )

        return result, "int"

    # -----------------------------------
    # parênteses
    # -----------------------------------

    def visit_parens(self, node):
        return self.visit(node["expr"])