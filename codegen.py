class BrilGenerator:
    def __init__(self):
        self.code = []
        self.temp_count = 0

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

    def visit_class(self, node):
        for feature in node["features"]:
            self.visit(feature)

    def visit_method(self, node):
        self.emit(f"# método {node['name']}")

        result = self.visit(node["body"])

        if result:
            self.emit(f"print {result};")

        self.emit("")

    # -----------------------------------
    # literais
    # -----------------------------------

    def visit_integer(self, node):
        temp = self.new_temp()

        self.emit(
            f"{temp}: int = const {node['value']};"
        )

        return temp

    def visit_boolean(self, node):
        temp = self.new_temp()

        value = "true" if node["value"] else "false"

        self.emit(
            f"{temp}: bool = const {value};"
        )

        return temp

    # -----------------------------------
    # identificadores
    # -----------------------------------

    def visit_identifier(self, node):
        return node["name"]

    # -----------------------------------
    # operações binárias
    # -----------------------------------

    def visit_binop(self, node):
        left = self.visit(node["left"])
        right = self.visit(node["right"])

        result = self.new_temp()

        bril_ops = {
            "+": "add",
            "-": "sub",
            "*": "mul",
            "/": "div",
        }

        op = bril_ops[node["op"]]

        self.emit(
            f"{result}: int = {op} {left} {right};"
        )

        return result

    # -----------------------------------
    # parênteses
    # -----------------------------------

    def visit_parens(self, node):
        return self.visit(node["expr"])