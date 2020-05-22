import sys
import os

from tokenizer import Tokenizer
from symbolTable import SymbolTable
from vmWriter import VMWriter


class CompilationEngine:

    def __init__(self, inp_file, out_file):
        self.tokenizer = Tokenizer(inp_file)
        self.sym_tbl = SymbolTable()
        self.vm_writer = VMWriter(out_file)
        self.out_file = open(out_file, "a")
        self.current_token = ""
        self.current_token_type = ""
        self.curr_token_ptr = -1
        self.label_counter = {
            "if": 0,
            "while": 0
        }
        self.advance()
        self.compileClass()

    def appendToOutFile(self, content):
        # self.out_file.write(content)
        pass

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
        # self.appendToOutFile(f"<{tag}> {content} </{tag}>\n")

    def compileClass(self):
        # self.appendToOutFile("<class>\n")
        self.eat("class")
        self.class_name = self.current_token
        # self.xmlify()
        self.advance()
        self.eat("{")
        self.compileClassVarDec()
        self.compileSubroutineDec()
        self.eat("}")
        # self.appendToOutFile("</class>")

    def compileClassVarDec(self):
        while self.current_token in ("field", "static"):
            var_kind = self.current_token
            if self.current_token == "field":
                var_kind = "this"
            # self.appendToOutFile("<classVarDec>\n")
            # self.xmlify()
            self.advance()
            var_type = self.current_token
            # self.xmlify()
            # print(var_type)
            self.advance()
            var_name = self.current_token
            # self.xmlify()
            # print(var_name)
            self.advance()
            # print(var_kind, var_type, var_name)
            self.sym_tbl.define(var_name, var_type, var_kind)
            while self.current_token == ",":
                self.eat(",")
                var_name_cont = self.current_token
                # self.xmlify()
                # print(var_kind, var_type, var_name_cont)
                self.sym_tbl.define(var_name_cont, var_type, var_kind)
                self.advance()
            self.eat(";")
            # self.appendToOutFile("</classVarDec>\n")
        # print(self.sym_tbl.class_table)

    def compileSubroutineDec(self):
        while self.current_token in ("constructor", "function", "method"):
            # self.appendToOutFile("<subroutineDec>\n")
            subroutine = ""
            subroutine_name = ""
            if self.current_token == "constructor":
                self.eat("constructor")
                self.eat(self.class_name)
                self.eat("new")
                subroutine = "constructor"
                subroutine_name = "new"
            elif self.current_token in ("function", "method"):
                subroutine = self.current_token
                # self.xmlify()
                self.advance()
                subroutine_type = self.current_token
                # self.xmlify()
                # print(subroutine_type)
                self.advance()
                subroutine_name = self.current_token
                # self.xmlify()
                # print(subroutine_name)
                self.advance()
            self.eat("(")
            self.compileParamList(subroutine)
            self.eat(")")
            self.compileSubroutineBody(subroutine, subroutine_name)
            # self.appendToOutFile("</subroutineDec>\n")

    def compileParamList(self, subroutine):
        # self.appendToOutFile("<parameterList>\n")
        self.sym_tbl.startSubroutine()
        if subroutine == "method":
            self.sym_tbl.define("this", self.class_name, "argument")
        if self.current_token != ")":
            param_type = self.current_token
            # self.xmlify()
            # print(param_type)
            self.advance()
            param_name = self.current_token
            # self.xmlify()
            # print(param_name)
            self.advance()
            self.sym_tbl.define(param_name, param_type, "argument")
            while self.current_token == ",":
                self.eat(",")
                param_type_cont = self.current_token
                # self.xmlify()
                # print(param_type_cont)
                self.advance()
                param_name_cont = self.current_token
                # self.xmlify()
                # print(param_name_cont)
                self.advance()
                self.sym_tbl.define(
                    param_name_cont, param_type_cont, "argument")
        # self.appendToOutFile("</parameterList>\n")

    def compileSubroutineBody(self, subroutine, subroutine_name):
        # self.appendToOutFile("<subroutineBody>\n")
        self.eat("{")
        while self.current_token == "var":
            self.compilevarDec()
        func_name = f"{self.class_name}.{subroutine_name}"
        print(func_name)
        vars = self.sym_tbl.varCount("local")
        self.vm_writer.writeFunction(func_name, vars)
        if subroutine == "constructor":
            fields = self.sym_tbl.varCount("this")
            self.vm_writer.writePushPop("push", "constant", fields)
            self.vm_writer.writeCall("Memory.alloc", 1)
            self.vm_writer.writePushPop("pop", "pointer", 0)
        elif subroutine == "method":
            self.vm_writer.writePushPop("push", "argument", 0)
            self.vm_writer.writePushPop("pop", "pointer", 0)
        self.compileStatements()
        self.eat("}")
        # self.appendToOutFile("</subroutineBody>\n")

    def compilevarDec(self):
        # self.appendToOutFile("<varDec>\n")
        self.eat("var")
        var_type = self.current_token
        # self.xmlify()
        # print(var_type)
        self.advance()
        var_name = self.current_token
        # self.xmlify()
        # print(var_name)
        self.advance()
        self.sym_tbl.define(var_name, var_type, "local")
        while self.current_token == ",":
            self.eat(",")
            var_name_cont = self.current_token
            # self.xmlify()
            # print(var_name_cont)
            self.advance()
            self.sym_tbl.define(var_name_cont, var_type, "local")
        self.eat(";")
        # self.appendToOutFile("</varDec>\n")
        # print(self.sym_tbl.func_table)

    def compileStatements(self):
        # self.appendToOutFile("<statements>\n")
        while self.current_token in ("let", "if", "while", "do", "return"):
            if self.current_token == "let":
                # self.appendToOutFile("<letStatement>\n")
                self.compileLet()
                # self.appendToOutFile("</letStatement>\n")
            elif self.current_token == "if":
                # self.appendToOutFile("<ifStatement>\n")
                self.compileIf()
                # self.appendToOutFile("</ifStatement>\n")
            elif self.current_token == "while":
                # self.appendToOutFile("<whileStatement>\n")
                self.compileWhile()
                # self.appendToOutFile("</whileStatement>\n")
            elif self.current_token == "do":
                # self.appendToOutFile("<doStatement>\n")
                self.compileDo()
                # self.appendToOutFile("</doStatement>\n")
            elif self.current_token == "return":
                # self.appendToOutFile("<returnStatement>\n")
                self.compileReturn()
                # self.appendToOutFile("</returnStatement>\n")
        # self.appendToOutFile("</statements>\n")

    def compileLet(self):
        self.eat("let")
        var_name = self.current_token
        # self.xmlify()
        # print(var_name)
        (_type, kind, index) = self.sym_tbl.getVariable(var_name)
        self.advance()
        if self.current_token == "[":
            self.eat("[")
            self.compileExpression()
            self.eat("]")

            self.vm_writer.writePushPop("push", kind, index)
            self.vm_writer.writeArithmetic("add")
            self.vm_writer.writePushPop("pop", "temp", 0)

            self.eat("=")
            self.compileExpression()

            self.vm_writer.writePushPop("push", "temp", 0)
            self.vm_writer.writePushPop("pop", "pointer", 1)
            self.vm_writer.writePushPop("pop", "that", 0)
        else:
            self.eat("=")
            self.compileExpression()

            self.vm_writer.writePushPop("pop", kind, index)

        self.eat(";")

    def compileIf(self):
        self.eat("if")
        self.eat("(")
        self.compileExpression()
        self.eat(")")

        label_true = f"IF_TRUE{self.label_counter['if']}"
        label_false = f"IF_FALSE{self.label_counter['if']}"
        label_end = f"IF_END{self.label_counter['if']}"
        self.label_counter["if"] += 1

        self.vm_writer.writeIf(label_true)
        self.vm_writer.writeGoto(label_false)
        self.vm_writer.writeLabel(label_true)

        self.eat("{")
        self.compileStatements()
        self.vm_writer.writeGoto(label_end)
        self.eat("}")
        self.vm_writer.writeLabel(label_false)
        if self.current_token == "else":
            self.eat("else")
            # if self.current_token == "if":
            #     self.eat("if")
            #     self.eat("(")
            #     self.compileExpression()
            #     self.eat(")")
            self.eat("{")
            self.compileStatements()
            self.eat("}")
        self.vm_writer.writeLabel(label_end)

    def compileWhile(self):

        label_while = f"WHILE_EXP{self.label_counter['while']}"
        label_end = f"WHILE_END{self.label_counter['while']}"
        self.label_counter['while'] += 1

        self.eat("while")
        self.vm_writer.writeLabel(label_while)
        self.eat("(")
        self.compileExpression()
        self.vm_writer.writeArithmetic("not")
        self.vm_writer.writeIf(label_end)
        self.eat(")")
        self.eat("{")
        self.compileStatements()
        self.vm_writer.writeGoto(label_while)
        self.eat("}")
        self.vm_writer.writeLabel(label_end)

    def compileDo(self):
        self.eat("do")
        func_name = self.current_token
        # self.xmlify()
        # print(name1)
        self.advance()
        if self.current_token == ".":
            self.eat(".")
            name2 = self.current_token  # method_name
            func_name = f"{func_name}.{name2}"
            # self.xmlify()
            # print(name2)
            self.advance()

        self.handleSubroutineCall(func_name)
        self.vm_writer.writePushPop("pop", "temp", 0)

        self.eat(";")

    def compileReturn(self):
        self.eat("return")
        if self.current_token != ";":
            self.compileExpression()
        else:
            self.vm_writer.writePushPop("push", "constant", 0)

        self.vm_writer.writeReturn()
        self.eat(";")

    def compileExpression(self):
        op_table = {
            '+': 'add',
            '-': 'sub',
            '&': 'and',
            '|': 'or',
            '<': 'lt',
            '>': 'gt',
            '=': 'eq'
        }
        exp = ""
        # self.appendToOutFile("<expression>\n")
        term = self.compileTerm()
        exp = exp + str(term)
        while self.current_token in ("+", "-", "*", "/", "&", "|", "<", ">", "="):
            op = self.current_token
            # self.xmlify()
            self.advance()
            term_cont = self.compileTerm()

            if op in op_table:
                self.vm_writer.writeArithmetic(op_table[op])
            elif op == "*":
                self.vm_writer.writeCall("Math.multiply", 2)
            elif op == "/":
                self.vm_writer.writeCall("Math.divide", 2)
            else:
                raise SyntaxError("Invalid Operator")

            exp = exp + f" {op} {term_cont}"
        # self.appendToOutFile("</expression>\n")
        return exp

    def compileExpressionList(self):
        args = 0
        # self.appendToOutFile("<expressionList>\n")
        if self.current_token != ")":
            self.compileExpression()
            args += 1
            while self.current_token == ",":
                self.eat(",")
                self.compileExpression()
                args += 1
        # self.appendToOutFile("</expressionList>\n")
        return args

    def compileTerm(self):
        full_term = ""
        # self.appendToOutFile("<term>\n")
        if self.current_token_type in ("identifier", "stringConstant", "integerConstant") or self.current_token in ("true", "false", "null", "this"):
            term = self.current_token
            # self.xmlify()
            # print(term)

            if self.current_token_type == "stringConstant":
                self.compileString(term)
            elif self.current_token_type == "integerConstant":
                self.vm_writer.writePushPop("push", "constant", term)
                print(f"push constant {term}")
            elif self.current_token in ("true", "false", "null"):
                self.vm_writer.writePushPop("push", "constant", 0)
                if self.current_token == "true":
                    self.vm_writer.writeArithmetic("not")
            elif self.current_token == "this":
                self.vm_writer.writePushPop("push", "pointer", 0)

            full_term = str(term)
            if self.current_token_type == "identifier":
                # print(term)
                (_type, kind, index) = self.sym_tbl.getVariable(self.current_token)
                args = 0
                self.advance()
                if self.current_token == "[":
                    self.eat("[")
                    exp = self.compileExpression()
                    self.eat("]")
                    full_term = full_term + f"[{exp}]"
                elif self.current_token == ".":
                    self.eat(".")
                    name2 = self.current_token  # method_name
                    # self.xmlify()
                    full_term = full_term + f".{name2}"
                    # print(name2)
                    self.advance()
                if self.current_token == "(":
                    full_term = full_term + "()"

                if "[" in full_term:
                    self.vm_writer.writePushPop("push", kind, index)
                    self.vm_writer.writeArithmetic("add")
                    self.vm_writer.writePushPop("pop", "pointer", 1)
                    self.vm_writer.writePushPop("push", "that", 0)
                elif "(" in full_term:
                    self.handleSubroutineCall(full_term)
                else:
                    self.vm_writer.writePushPop("push", kind, index)
            else:
                self.advance()
        elif self.current_token == "(":
            self.eat("(")
            exp = self.compileExpression()
            self.eat(")")
            full_term = full_term + f"({exp})"
        elif self.current_token in ("-", "~"):
            uop = self.current_token
            # self.xmlify()
            # print(uop)
            self.advance()
            term_cont = self.compileTerm()

            if uop == "-":
                self.vm_writer.writeArithmetic("neg")
            else:
                self.vm_writer.writeArithmetic("not")

            full_term = full_term + f"{uop}{term_cont}"
        # self.appendToOutFile("</term>\n")
        return full_term

    def handleSubroutineCall(self, func_name):
        args = 0
        if "(" in func_name:
            func_name = func_name[0:-2]
        if "." not in func_name:
            func_name = f"{self.class_name}.{func_name}"
            args += 1
            self.vm_writer.writePushPop("push", "pointer", 0)
            # print("pointer 0")
        if "." in func_name:
            c_name = func_name.split(".")[0]
            s_name = func_name.split(".")[1]
            (_type, kind, index) = self.sym_tbl.getVariable(c_name)
            if _type != None:
                self.vm_writer.writePushPop("push", kind, index)
                # print(f"push {kind} {index}")
                func_name = f"{_type}.{s_name}"
                args += 1
        self.eat("(")
        args += self.compileExpressionList()
        self.eat(")")
        print(func_name, args)
        self.vm_writer.writeCall(func_name, args)

    def compileString(self, string):
        self.vm_writer.writePushPop("push", "constant", len(string))
        self.vm_writer.writeCall("String.new", 1)
        for char in string:
            self.vm_writer.writePushPop("push", "constant", ord(char))
            self.vm_writer.writeCall("String.appendChar", 2)

    def eat(self, string):
        if self.current_token != string:
            raise SyntaxError(
                f"Expected {string} in place of {self.current_token}")
        # self.xmlify()
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
        # file = open(out_file, "w")
        # file.write("")
        CompilationEngine(file_path, f"{out_file}.vm")
        # tokenizerXML(out_file)
    else:
        files = os.listdir(file_path)
        for file in files:
            if ".jack" in file:
                # print(file)
                file = file.split(".jack")[0]

                # clearing file before starting
                # file = open(f"{file}.xml", "w")
                # file.write("")

                CompilationEngine(f"{file_path}/{file}.jack",
                                  f"{file_path}/{file}.vm")
                # tokenizerXML(f"{file_path}/{file}")


main()
