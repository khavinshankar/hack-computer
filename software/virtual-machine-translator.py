import sys
import os


class Parser:
    def __init__(self, file_name):
        file = open(file_name, "r")
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
        ins = self.current_instruction.split(" ")[0]
        ins_tbl = {
            "pop": "C_POP",
            "push": "C_PUSH",
            "label": "C_LABEL",
            "goto": "C_GOTO",
            "if-goto": "C_IF",
            "function": "C_FUNC",
            "call": "C_CALL",
            "return": "C_RETURN"
        }
        try:
            return ins_tbl[ins]
        except:
            return "C_ARITHMETIC"

    def arg1(self):
        args = self.current_instruction.split(" ")
        if len(args) > 1:
            return args[1]
        return args[0]

    def arg2(self):
        args = self.current_instruction.split(" ")
        if len(args) > 2:
            return args[2]
        return None


class Coder:
    def __init__(self, file_name):
        self.file_name = file_name
        self.looper_const = 0
        self.calledFunctions = []
        # self.clearFile()

    def clearFile(self):
        self.file = open(self.file_name, "w")
        self.file.write("")

    def appendToFile(self, content):
        self.file = open(self.file_name, "a")
        self.file.write(f"{content}\n")

    def initialize(self):
        asm_cmd = "@256\nD=A\n@SP\nM=D\n"
        self.appendToFile(asm_cmd)
        self.writeFuncCall("Sys.init", 0)

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
            asm_ins = f"@SP\nM=M-1\nA=M\nD=M\nM=0\n@SP\nM=M-1\n@R13\nM=D\n@SP\nA=M\nD=M\nM=0\n@R13\nD=D{cmd_sym[cmd]}M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
            self.appendToFile(asm_ins)
            return True
        elif cmd == "neg" or cmd == "not":
            asm_ins = f"@SP\nM=M-1\nA=M\nM={cmd_sym[cmd]}M\n@SP\nM=M+1\n"
            self.appendToFile(asm_ins)
            return True
        asm_ins = f"@SP\nM=M-1\nA=M\nD=M\nM=0\n@R13\nM=D\n@SP\nM=M-1\nA=M\nD=M\nM=0\nM=!M\n@R13\nD=D-M\nM=0\n@SP\nM=M+1\n@END{self.looper_const}\nD;{cmd_sym[cmd]}\n@SP\nM=M-1\nA=M\nM=0\n@SP\nM=M+1\n@END{self.looper_const}\n0;JMP\n(END{self.looper_const})\n"
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
        # print(self.calledFunctions)
        if len(self.calledFunctions) > 0:
            currentFunction = self.calledFunctions[-1].split(".")[0]

        if type == "C_PUSH":
            if segment == "constant":
                asm_ins = f"@{value}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                self.appendToFile(asm_ins)
                return True
            elif segment in ("temp", "pointer"):
                asm_ins = f"@{value}\nD=A\n@{seg_tbl[segment]}\nD=D+A\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                self.appendToFile(asm_ins)
                return True
            elif segment == "static":
                # print(f"@{currentFunction}.x{value}")
                asm_ins = f"@{currentFunction}.x{value}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                self.appendToFile(asm_ins)
                return True
            else:
                asm_ins = f"@{value}\nD=A\n@{seg_tbl[segment]}\nD=D+M\nA=D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"
                self.appendToFile(asm_ins)
                return True
        elif type == "C_POP":
            if segment in ("temp", "pointer"):
                asm_ins = f"@{value}\nD=A\n@{seg_tbl[segment]}\nD=D+A\n@R13\nM=D\n@SP\nM=M-1\nA=M\nD=M\nM=0\n@R13\nA=M\nM=D\n@SP\n"
                self.appendToFile(asm_ins)
                return True
            elif segment == "static":
                # print(f"@{currentFunction}.x{value}")
                asm_ins = f"@SP\nM=M-1\nA=M\nD=M\nM=0\n@{currentFunction}.x{value}\nM=D\n"
                self.appendToFile(asm_ins)
                return True
            else:
                asm_ins = f"@{value}\nD=A\n@{seg_tbl[segment]}\nD=D+M\n@R13\nM=D\n@SP\nM=M-1\nA=M\nD=M\nM=0\n@R13\nA=M\nM=D\n@SP\n"
                self.appendToFile(asm_ins)
                return True

    def writeLabel(self, label):
        asm_ins = f"({label})\n"
        self.appendToFile(asm_ins)

    def writeGoto(self, label):
        asm_ins = f"@{label}\n0;JMP\n"
        self.appendToFile(asm_ins)

    def writeIfGoto(self, label):
        asm_ins = f"@SP\nM=M-1\nA=M\nD=M\n@{label}\nD;JNE\n"
        self.appendToFile(asm_ins)

    def writeFuncCall(self, funcName, numArgs):
        asm_ins = f"@END.{funcName}.{self.looper_const}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n@5 \nD=A\n@{numArgs}\nD=D+A\n@SP\nD=M-D\n@ARG\nM=D\n@SP\nD=M\n@LCL\nM=D\n@{funcName}\n0;JMP\n(END.{funcName}.{self.looper_const})\n"
        self.looper_const += 1
        self.appendToFile(asm_ins)

    def writeFuncDef(self, funcName, numVars):
        self.calledFunctions.append(funcName)
        asm_ins = f"({funcName})\n"
        self.appendToFile(asm_ins)
        for _ in range(int(numVars)):
            self.writePushPop("C_PUSH", "constant", 0)

    def writeFuncReturn(self):
        self.calledFunctions.pop()
        asm_ins = "@LCL\nD=M\n@R15\nM=D\n@5\nA=D-A\nD=M\n@R14\nM=D\n@ARG\nD=M\n@R13\nM=D\n@SP\nAM=M-1\nD=M\n@R13\nA=M\nM=D\n@ARG\nD=M\n@SP\nM=D+1\n@R15\nAMD=M-1\nD=M\n@THAT\nM=D\n@R15\nAMD=M-1\nD=M\n@THIS\nM=D\n@R15\nAMD=M-1\nD=M\n@ARG\nM=D\n@R15\nAMD=M-1\nD=M\n@LCL\nM=D\n@R14\nA=M\n0;JMP\n"
        self.appendToFile(asm_ins)

    def closeFile(self):
        self.file.close()


class Main:
    def __init__(self, file_path):
        self.sysVm = False

        if ".vm" in file_path:
            out_file = file_path.split(".vm")[0]
            coder = Coder(f"{out_file}.asm")
            self.convert(file_path, coder)
        else:
            self.parse_files(file_path)
            coder = Coder(self.out_file)
            if self.sysVm:
                coder.initialize()
            for vm_file in self.vm_files:
                self.convert(vm_file, coder)

    def parse_files(self, file_path):
        self.vm_files = []
        files = os.listdir(file_path)
        for file in files:
            if ".vm" in file:
                vm_file = f"{file_path}/{file}"
                if file == "Sys.vm":
                    self.sysVm = True
                    self.vm_files.insert(0, vm_file)
                else:
                    self.vm_files.append(vm_file)
        folder_name = file_path.split("/")[-1]
        self.out_file = f"{file_path}/{folder_name}.asm"

    def convert(self, in_file, coder):
        parser = Parser(in_file)

        while parser.advance():
            ins_type = parser.instructionType()
            arg1 = parser.arg1()
            arg2 = parser.arg2()

            #print(ins_type, arg1, arg2)

            if ins_type == "C_ARITHMETIC":
                coder.writeArithmetic(arg1)
            elif ins_type == "C_POP" or ins_type == "C_PUSH":
                coder.writePushPop(ins_type, arg1, arg2)
            elif ins_type == "C_LABEL":
                coder.writeLabel(arg1)
            elif ins_type == "C_GOTO":
                coder.writeGoto(arg1)
            elif ins_type == "C_IF":
                coder.writeIfGoto(arg1)
            elif ins_type == "C_FUNC":
                coder.writeFuncDef(arg1, arg2)
            elif ins_type == "C_CALL":
                coder.writeFuncCall(arg1, arg2)
            elif ins_type == "C_RETURN":
                coder.writeFuncReturn()

        coder.closeFile()


if __name__ == '__main__':

    file_path = sys.argv[1]
    Main(file_path)
