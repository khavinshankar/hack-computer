import sys
import os

from tokenizer import Tokenizer, tokenizerXML


class CompilationEngine:
    def __init__(self, inp_file, out_file):
        self.tokenizer = Tokenizer(inp_file)
        self.out_file = open(out_file, "a")
        self.current_token = ""
        self.current_token_type = ""
        self.curr_token_ptr = -1
        self.advance()
        self.compileClass()

    def appendToOutFile(self, content):
        self.out_file.write(content)

    def xmlify(self, tag=None, content=None):
        if tag == None:
            tag = self.current_token_type
        if content == None:
            content = self.current_token
        html_alternate = {
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "&": "&amp;"
        }
        if content in ("<", ">", '"', "&"):
            content = html_alternate[content]
        self.appendToOutFile(f"<{tag}> {content} </{tag}>\n")

    def compileClass(self):
        self.appendToOutFile("<class>\n")
        self.eat("class")
        class_name = self.current_token
        self.xmlify()
        self.advance()
        self.eat("{")
        self.compileClassVarDec()
        self.compileSubroutineDec(class_name)
        self.eat("}")
        self.appendToOutFile("</class>")

    def compileClassVarDec(self):
        while self.current_token in ("field", "static"):
            self.appendToOutFile("<classVarDec>\n")
            self.xmlify()
            self.advance()
            var_type = self.current_token
            self.xmlify()
            print(var_type)
            self.advance()
            var_name = self.current_token
            self.xmlify()
            print(var_name)
            self.advance()
            while self.current_token == ",":
                self.eat(",")
                var_name_cont = self.current_token
                self.xmlify()
                print(var_name_cont)
                self.advance()
            self.eat(";")
            self.appendToOutFile("</classVarDec>\n")

    def compileSubroutineDec(self, class_name):
        while self.current_token in ("constructor", "function", "method"):
            self.appendToOutFile("<subroutineDec>\n")
            if self.current_token == "constructor":
                self.eat("constructor")
                self.eat(class_name)
                self.eat("new")
            elif self.current_token in ("function", "method"):
                self.xmlify()
                self.advance()
                subroutine_type = self.current_token
                self.xmlify()
                print(subroutine_type)
                self.advance()
                subroutine_name = self.current_token
                self.xmlify()
                print(subroutine_name)
                self.advance()
            self.eat("(")
            self.compileParamList()
            self.eat(")")
            self.compileSubroutineBody()
            self.appendToOutFile("</subroutineDec>\n")

    def compileParamList(self):
        self.appendToOutFile("<parameterList>\n")
        if self.current_token != ")":
            param_type = self.current_token
            self.xmlify()
            print(param_type)
            self.advance()
            param_name = self.current_token
            self.xmlify()
            print(param_name)
            self.advance()
            while self.current_token == ",":
                self.eat(",")
                param_type_cont = self.current_token
                self.xmlify()
                print(param_type_cont)
                self.advance()
                param_name_cont = self.current_token
                self.xmlify()
                print(param_name_cont)
                self.advance()
        self.appendToOutFile("</parameterList>\n")

    def compileSubroutineBody(self):
        self.appendToOutFile("<subroutineBody>\n")
        self.eat("{")
        while self.current_token == "var":
            self.compilevarDec()
        self.compileStatements()
        self.eat("}")
        self.appendToOutFile("</subroutineBody>\n")

    def compilevarDec(self):
        self.appendToOutFile("<varDec>\n")
        self.eat("var")
        var_type = self.current_token
        self.xmlify()
        print(var_type)
        self.advance()
        var_name = self.current_token
        self.xmlify()
        print(var_name)
        self.advance()
        while self.current_token == ",":
            self.eat(",")
            var_name_cont = self.current_token
            self.xmlify()
            print(var_name_cont)
            self.advance()
        self.eat(";")
        self.appendToOutFile("</varDec>\n")

    def compileStatements(self):
        self.appendToOutFile("<statements>\n")
        while self.current_token in ("let", "if", "while", "do", "return"):
            if self.current_token == "let":
                self.appendToOutFile("<letStatement>\n")
                self.compileLet()
                self.appendToOutFile("</letStatement>\n")
            elif self.current_token == "if":
                self.appendToOutFile("<ifStatement>\n")
                self.compileIf()
                self.appendToOutFile("</ifStatement>\n")
            elif self.current_token == "while":
                self.appendToOutFile("<whileStatement>\n")
                self.compileWhile()
                self.appendToOutFile("</whileStatement>\n")
            elif self.current_token == "do":
                self.appendToOutFile("<doStatement>\n")
                self.compileDo()
                self.appendToOutFile("</doStatement>\n")
            elif self.current_token == "return":
                self.appendToOutFile("<returnStatement>\n")
                self.compileReturn()
                self.appendToOutFile("</returnStatement>\n")
        self.appendToOutFile("</statements>\n")

    def compileLet(self):
        self.eat("let")
        var_name = self.current_token
        self.xmlify()
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
        self.xmlify()
        print(name1)
        self.advance()
        if self.current_token == ".":
            self.eat(".")
            name2 = self.current_token  # method_name
            self.xmlify()
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
        self.appendToOutFile("<expression>\n")
        self.compileTerm()
        while self.current_token in ("+", "-", "*", "/", "&", "|", "<", ">", "="):
            op = self.current_token
            self.xmlify()
            print(op)
            self.advance()
            self.compileTerm()
        self.appendToOutFile("</expression>\n")

    def compileExpressionList(self):
        self.appendToOutFile("<expressionList>\n")
        if self.current_token != ")":
            self.compileExpression()
            while self.current_token == ",":
                self.eat(",")
                self.compileExpression()
        self.appendToOutFile("</expressionList>\n")

    def compileTerm(self):
        self.appendToOutFile("<term>\n")
        if self.current_token_type in ("identifier", "stringConstant", "integerConstant") or self.current_token in ("true", "false", "null", "this"):
            term = self.current_token
            self.xmlify()
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
                    self.xmlify()
                    print(name2)
                    self.advance()
                if self.current_token == "(":
                    self.eat("(")
                    self.compileExpressionList()
                    self.eat(")")
            else:
                self.advance()
        elif self.current_token == "(":
            self.eat("(")
            self.compileExpression()
            self.eat(")")
        elif self.current_token in ("-", "~"):
            uop = self.current_token
            self.xmlify()
            print(uop)
            self.advance()
            self.compileTerm()
        self.appendToOutFile("</term>\n")

    def eat(self, string):
        if self.current_token != string:
            raise SyntaxError(
                f"Expected {string} in place of {self.current_token}")
        self.xmlify()
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
    file_path = sys.argv[1]

    if ".jack" in file_path:
        out_file = file_path.split(".jack")[0]
        # clearing file before starting
        file = open(out_file, "w")
        file.write("")
        CompilationEngine(file_path, f"{out_file}.xml")
        tokenizerXML(out_file)
    else:
        files = os.listdir(file_path)
        for file in files:
            if ".jack" in file:
                print(file)
                file = file.split(".jack")[0]

                # clearing file before starting
                # file = open(f"{file}.xml", "w")
                # file.write("")

                CompilationEngine(f"{file_path}/{file}.jack",
                                  f"{file_path}/{file}.xml")
                tokenizerXML(f"{file_path}/{file}")


main()
