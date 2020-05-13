class Assembler:
    def __init__(self, in_file_name, out_file_name):
        self.in_file_name = in_file_name
        self.out_file_name = out_file_name
        self.sym_tbl = {}
        self.last_var = 16
        self.loopers = 0

    def convert(self):
        instructions = self.get_program_instructions(self.in_file_name)
        instructions = self.remove_comments(instructions)
        instructions = self.remove_whitespace(instructions)
        self.create_symbol_table()
        instructions = self.handle_loopers(instructions)
        machine_code = self.parse(instructions)
        print(machine_code)
        self.write_to_file(self.out_file_name, machine_code)

    def get_program_instructions(self, file_name):
        file = open(f"{file_name}.asm", "r")
        return file.read().split("\n")

    def write_to_file(self, file_name, content):
        file = open(f"{file_name}.hack", "w")
        file.write(content)
        return True

    def remove_whitespace(self, instructions):
        new = []
        for instruction in instructions:
            instruction = instruction.strip()
            if instruction != "":
                new.append(instruction)
        return new

    def remove_comments(self, instructions):
        new = []
        for instruction in instructions:
            instruction = instruction.split("//")
            new.append(instruction[0])
        return new

    def parse(self, instructions):
        new = ""
        for instruction in instructions:
            if instruction[0] == "@":
                new = new + self.parse_a_instruction(instruction)
            else:
                new = new + self.parse_c_instruction(instruction)
        return new

    def parse_a_instruction(self, instruction):
        instruction = instruction[1:]
        try:
            num = int(instruction)
            return f"0{num:015b}\n"
        except:
            try:
                num = self.sym_tbl[instruction]
                return f"0{num:015b}\n"
            except:
                self.sym_tbl[instruction] = self.last_var
                num = self.last_var
                self.last_var += 1
                return f"0{num:015b}\n"

    def parse_c_instruction(self, instruction):
        instruction = instruction.split(";")
        if len(instruction) > 1:
            jump = instruction[1]
        else:
            jump = "null"

        instruction = instruction[0].split("=")
        if len(instruction) > 1:
            comp = instruction[1]
            dest = instruction[0]
        else:
            dest = "null"
            comp = instruction[0]

        if "M" in str(comp):
            a = 1
            comp = comp.replace("M", "A")
        else:
            a = 0

        dest_tbl = {
            "null": "000",
            "M": "001",
            "D": "010",
            "MD": "011",
            "A": "100",
            "AM": "101",
            "AD": "110",
            "AMD": "111",
        }
        jump_tbl = {
            "null": "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111",
        }
        comp_tbl = {
            "0": "101010",
            "1": "111111",
            "-1": "111010",
            "D": "001100",
            "A": "110000",
            "!D": "001101",
            "!A": "110001",
            "-D": "001111",
            "-A": "110011",
            "D+1": "011111",
            "A+1": "110111",
            "D-1": "001110",
            "A-1": "110010",
            "D+A": "000010",
            "D-A": "010011",
            "A-D": "000111",
            "D&A": "000000",
            "D|A": "010101",
        }

        return f"111{a}{comp_tbl[str(comp)]}{dest_tbl[dest]}{jump_tbl[jump]}\n"

    def create_symbol_table(self):
        for i in range(16):
            self.sym_tbl[f"R{i}"] = i
        self.sym_tbl["SCREEN"] = 16384
        self.sym_tbl["KBD"] = 24576
        self.sym_tbl["SP"] = 0
        self.sym_tbl["LCL"] = 1
        self.sym_tbl["ARG"] = 2
        self.sym_tbl["THIS"] = 3
        self.sym_tbl["THAT"] = 4

    def handle_loopers(self, instructions):
        remove_list = []
        for i, instruction in enumerate(instructions):
            if instruction[0] == "(" and instruction[-1] == ")":
                instruction = instruction[1:-1]
                self.sym_tbl[instruction] = i - self.loopers
                self.loopers += 1
                remove_list.append(f"({instruction})")
        for ins in remove_list:
            instructions.remove(ins)
        return instructions


file_name = "Max"
hack = Assembler(file_name, file_name)
hack.convert()
