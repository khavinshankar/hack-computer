class Parser:
    def __init__(self, file_name):
        file = open(f"{file_name}.vm", "r")
        self.instructions = file.read().split("\n")
        self.remove_comments()
        self.remove_whitespace()
        self.curr_ins_ptr = 0
        self.current_instruction = ""

    def remove_whitespace(self):
        new = []
        for instruction in self.instructions:
            instruction = instruction.strip()
            if instruction != "":
                new.append(instruction)
        self.instructions = new

    def remove_comments(self):
        new = []
        for instruction in self.instructions:
            instruction = instruction.split("//")
            new.append(instruction[0])
        self.instructions = new

    def hasMoreCommands(self):
        if self.curr_ins_ptr + 1 > len(self.instructions):
            return False
        return True

    def advance(self):
        if self.hasMoreCommands():
            self.current_instruction = self.instructions[self.curr_ins_ptr]
            self.curr_ins_ptr += 1
            return True
        return False

    def instructionType(self):
        ins = self.current_instruction
        if "push" in ins:
            return "C_PUSH"
        elif "pop" in ins:
            return "C_POP"
        return "C_ARITHMETIC"

    def arg1(self):
        args = self.current_instruction.split(" ")
        if len(args) > 1:
            return args[1]
        return args[0]

    def arg2(self):
        args = self.current_instruction.split(" ")
        if len(args) > 1:
            return args[2]
        return None


class Coder:
    def __init__(self, file_name):
        self.file_name = file_name
        self.looper_const = 0

    def appendToFile(self, content):
        self.file = open(f"{self.file_name}.asm", "a")
        self.file.write(f"{content}\n")

    def writeArithmetic(self, cmd):
        cmd_sym = {
            "add": "+",
            "sub": "-",
            "neg": "-",
            "eq": "JEQ",
            "gt": "JGT",
            "lt": "JLT",
            "and": "&",
            "or": "|",
            "not": "!"
        }
        if cmd == "add" or cmd == "sub" or cmd == "and" or cmd == "or":
            asm_ins = f"@SP\nM=M-1\nA=M\nD=M\nM=0\n@SP\nM=M-1\n@temp\nM=D\n@SP\nA=M\nD=M\nM=0\n@temp\nD=D{cmd_sym[cmd]}M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            self.appendToFile(asm_ins)
            return True
        elif cmd == "neg" or cmd == "not":
            asm_ins = f"@SP\nM=M-1\nA=M\nM={cmd_sym[cmd]}M\n@SP\nM=M+1\n"
            self.appendToFile(asm_ins)
            return True
        asm_ins = f"@SP\nM=M-1\nA=M\nD=M\nM=0\n@TEMP\nM=D\n@SP\nM=M-1\nA=M\nD=M\nM=0\nM=!M\n@TEMP\nD=D-M\nM=0\n@SP\nM=M+1\n@END{self.looper_const}\nD;{cmd_sym[cmd]}\n@SP\nM=M-1\nA=M\nM=0\n@SP\nM=M+1\n@END{self.looper_const}\n0;JMP\n(END{self.looper_const})\n"
        self.looper_const += 1
        self.appendToFile(asm_ins)
        return True

    def writePushPop(self, type, segment, value):
        seg_tbl = {
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT',
            'static': 16,
            'temp': 5,
            'pointer': 3
        }

        if type == "C_PUSH":
            if segment == "constant":
                asm_ins = f"@{value}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                self.appendToFile(asm_ins)
                return True
            elif segment in ("static", "temp", "pointer"):
                asm_ins = f"@{value}\nD=A\n@{seg_tbl[segment]}\nD=D+A\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                self.appendToFile(asm_ins)
                return True
            else:
                asm_ins = f"@{value}\nD=A\n@{seg_tbl[segment]}\nD=D+M\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                self.appendToFile(asm_ins)
                return True
        elif type == "C_POP":
            if segment in ("static", "temp", "pointer"):
                asm_ins = f"@{value}\nD=A\n@{seg_tbl[segment]}\nD=D+A\n@temp\nM=D\n@SP\nM=M-1\nA=M\nD=M\nM=0\n@temp\nA=M\nM=D\n@SP\n"
                self.appendToFile(asm_ins)
                return True
            else:
                asm_ins = f"@{value}\nD=A\n@{seg_tbl[segment]}\nD=D+M\n@temp\nM=D\n@SP\nM=M-1\nA=M\nD=M\nM=0\n@temp\nA=M\nM=D\n@SP\n"
                self.appendToFile(asm_ins)
                return True

    def closeFile(self):
        self.file.close()


def main():
    file_name = "StaticTest"
    parser = Parser(file_name)
    coder = Coder(file_name)
    while parser.advance():
        ins_type = parser.instructionType()
        arg1 = parser.arg1()
        arg2 = parser.arg2()

        print(ins_type, arg1, arg2)

        if ins_type == "C_ARITHMETIC":
            coder.writeArithmetic(arg1)
        else:
            coder.writePushPop(ins_type, arg1, arg2)

    coder.closeFile()


main()
