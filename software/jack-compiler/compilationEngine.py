from tokenizer import Tokenizer


class CompilationEngine:
    def __init__(self, inp_file, out_file):
        self.tokenizer = Tokenizer(inp_file)
        self.current_token = ""
        self.current_token_type = ""
        self.curr_token_ptr = -1
        self.advance()
        self.compileClass()

    def compileClass(self):
        self.eat("class")
        class_name = self.current_token
        self.advance()
        self.eat("{")
        self.compileClassVarDec()
        self.compileSubroutineDec(class_name)
        self.eat("}")

    def compileClassVarDec(self):
        while self.current_token in ("field", "static"):
            self.advance()
            var_type = self.current_token
            print(var_type)
            self.advance()
            var_name = self.current_token
            print(var_name)
            self.advance()
            while self.current_token == ",":
                self.eat(",")
                var_name_cont = self.current_token
                print(var_name_cont)
                self.advance()
            self.eat(";")

    def compileSubroutineDec(self, class_name):
        while self.current_token in ("constructor", "function", "method"):
            if self.current_token == "constructor":
                self.eat("constructor")
                self.eat(class_name)
                self.eat("new")
            elif self.current_token in ("function", "method"):
                self.advance()
                subroutine_type = self.current_token
                print(subroutine_type)
                self.advance()
                subroutine_name = self.current_token
                print(subroutine_name)
                self.advance()
            self.eat("(")
            self.compileParamList()
            self.eat(")")
            self.compileSubroutineBody()

    def compileParamList(self):
        if self.current_token != ")":
            param_type = self.current_token
            print(param_type)
            self.advance()
            param_name = self.current_token
            print(param_name)
            self.advance()
            while self.current_token == ",":
                self.eat(",")
                param_type_cont = self.current_token
                print(param_type_cont)
                self.advance()
                param_name_cont = self.current_token
                print(param_name_cont)
                self.advance()

    def compileSubroutineBody(self):
        self.eat("{")
        while self.current_token == "var":
            self.compilevarDec()
        self.compileStatements()
        self.eat("}")

    def compilevarDec(self):
        self.eat("var")
        var_type = self.current_token
        print(var_type)
        self.advance()
        var_name = self.current_token
        print(var_name)
        self.advance()
        while self.current_token == ",":
            self.eat(",")
            var_name_cont = self.current_token
            print(var_name_cont)
            self.advance()
        self.eat(";")

    def compileStatements(self):
        while self.current_token in ("let", "if", "while", "do", "return"):
            if self.current_token == "let":
                self.compileLet()
            elif self.current_token == "if":
                self.compileIf()
            elif self.current_token == "while":
                self.compileWhile()
            elif self.current_token == "do":
                self.compileDo()
            elif self.current_token == "return":
                self.compileReturn()

    def compileLet(self):
        self.eat("let")
        var_name = self.current_token
        print(var_name)
        self.advance()
        if self.current_token == "[":
            self.eat("[")
            self.compileExpression()
            self.eat("]")
        self.eat("=")
        self.compileExpression()
        self.eat(";")

    def compileIf(self):
        self.eat("if")
        self.eat("(")
        self.compileExpression()
        self.eat(")")
        self.eat("{")
        self.compileStatements()
        self.eat("}")
        while self.current_token == "else":
            self.eat("else")
            if self.current_token == "if":
                self.eat("if")
                self.eat("(")
                self.compileExpression()
                self.eat(")")
            self.eat("{")
            self.compileStatements()
            self.eat("}")

    def compileWhile(self):
        self.eat("while")
        self.eat("(")
        self.compileExpression()
        self.eat(")")
        self.eat("{")
        self.compileStatements()
        self.eat("}")

    def compileDo(self):
        self.eat("do")
        name1 = self.current_token
        print(name1)
        self.advance()
        if self.current_token == ".":
            self.eat(".")
            name2 = self.current_token  # method_name
            print(name2)
            self.advance()
        self.eat("(")
        self.compileExpressionList()
        self.eat(")")
        self.eat(";")

    def compileReturn(self):
        self.eat("return")
        if self.current_token != ";":
            self.compileExpression()
        self.eat(";")

    def compileExpression(self):
        self.compileTerm()
        while self.current_token in ("+", "-", "*", "/", "&", "|", "<", ">", "="):
            op = self.current_token
            print(op)
            self.advance()
            self.compileTerm()

    def compileExpressionList(self):
        if self.current_token != ")":
            self.compileExpression()
            while self.current_token == ",":
                self.eat(",")
                self.compileExpression()

    def compileTerm(self):
        if self.current_token_type in ("identifier", "stringConstant", "integerConstant") or self.current_token in ("true", "false", "null", "this", "-", "~"):
            term = self.current_token
            print(term)
            if self.current_token_type == "identifier":
                self.advance()
                if self.current_token == "[":
                    self.eat("[")
                    self.compileExpression()
                    self.eat("]")
                elif self.current_token == ".":
                    self.eat(".")
                    name2 = self.current_token  # method_name
                    print(name2)
                    self.advance()
            else:
                self.advance()
        if self.current_token == "(":
            self.eat("(")
            self.compileExpressionList()
            self.eat(")")

    def eat(self, string):
        if self.current_token != string:
            raise SyntaxError(
                f"Expected {string} in place of {self.current_token}")
        print(self.current_token)
        self.advance()

    def advance(self):
        if self.tokenizer.advance():
            (token, token_type) = self.tokenizer.tokenWithType()
            html_alternate = {
                "&lt;": "<",
                "&gt;": ">",
                "&quot;": '"',
                "&amp;": "&"
            }
            if token in ("&lt;", "&gt;", "&quot;", "&amp;"):
                token = html_alternate[token]

            self.current_token = token
            self.current_token_type = token_type
            self.curr_token_ptr += 1
            return True
        return False


def main():
    engine = CompilationEngine("Square.jack", "Square.xml")
    print(engine)


main()
