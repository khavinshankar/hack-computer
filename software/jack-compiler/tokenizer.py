import re


class Tokenizer:
    def __init__(self, file_name):
        self.curr_token_ptr = -1
        self.current_token = ""
        self.tokens = []
        file = open(file_name, "r")
        data = file.read()
        data = self.remove_comments(data)
        data = self.remove_whitespace(data)
        self.tokenize(data)

    def remove_whitespace(self, data):
        new = []
        for instruction in data:
            instruction = instruction.strip()
            if instruction != "":
                new.append(instruction)
        return new

    def remove_comments(self, data):
        pattern = re.compile(r"\/\*\*.+?\*\/")  # multi line comments
        multiline_comments = pattern.findall(data)
        for mlc in multiline_comments:
            data = data.replace(mlc, "")
        data = data.split("\n")
        new = []
        for instruction in data:
            instruction = instruction.split("//")
            new.append(instruction[0])
        return new

    def tokenize(self, data):
        variable = re.compile(r"([a-zA-Z_][a-zA-Z_0-9]*)")
        num_const = re.compile(r"(\d+)")
        str_const = re.compile(r'(\".+\")')
        data = self.handleStringConstants(data)
        for x in data:
            if not str_const.match(x):
                words = x.split(" ")
                for word in words:
                    tokens = variable.split(word)
                    for token in tokens:
                        if not variable.match(token) and token != "":
                            values = num_const.split(token)
                            for value in values:
                                if not num_const.match(value) and value != "":
                                    self.tokens.extend(value)
                                else:
                                    if value != "":
                                        self.tokens.append(value)
                        else:
                            if token != "":
                                self.tokens.append(token)
            else:
                self.tokens.append(x)

    def handleStringConstants(self, data):
        str_const = re.compile(r'(\".+\")')
        new = []
        for line in data:
            new.extend(str_const.split(line))
        return new

    def hasMoreTokens(self):
        if self.curr_token_ptr < len(self.tokens) - 1:
            return True
        return False

    def advance(self):
        if self.hasMoreTokens():
            self.curr_token_ptr += 1
            self.current_token = self.tokens[self.curr_token_ptr]
            return True
        return False

    def tokenWithType(self):
        keywords = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean",
                    "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]
        symbols = ["{", "}", "(", ")", "[", "]", ".", ",", ";",
                   "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]

        num_const = re.compile(r"(\d+)")
        str_const = re.compile(r'(\".+\")')
        tokenType = ""

        if str_const.match(self.current_token):
            tokenType = "stringConstant"
            self.current_token = self.current_token[1:-1]
        elif num_const.match(self.current_token):
            tokenType = "integerConstant"
        elif self.current_token in keywords:
            tokenType = "keyword"
        elif self.current_token in symbols:
            html_alternate = {
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "&": "&amp;"
            }
            tokenType = "symbol"
            try:
                self.current_token = html_alternate[self.current_token]
            except KeyError:
                pass
        else:
            tokenType = "identifier"

        return (self.current_token, tokenType)


def main():
    tokenizer = Tokenizer("Main.jack")
    file = open("xml.xml", "a")
    file.write("<tokens>\n")
    while tokenizer.advance():
        (token, tokenType) = tokenizer.tokenWithType()
        file.write(f"<{tokenType}> {token} </{tokenType}>\n")
    file.write("</tokens>")


main()
