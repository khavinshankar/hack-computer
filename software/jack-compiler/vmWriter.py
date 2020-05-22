class VMWriter:
    def __init__(self, out_file):
        # clearing file before starting
        file = open(out_file, "w")
        file.write("")
        file.close()
        self.file = open(out_file, "a")

    def appendToFile(self, content):
        self.file.write(content)
        # create a newline for every call
        self.file.write("\n")

    def writePushPop(self, command, segment, index):
        if command in ("push", "pop"):
            if segment in ("argument", "local", "static", "this", "that", "pointer", "temp", "constant"):
                vm_code = f"{command} {segment} {index}"
                self.appendToFile(vm_code)

    def writeArithmetic(self, command):
        if command in ("add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"):
            vm_code = f"{command}"
            self.appendToFile(vm_code)

    def writeLabel(self, label):
        vm_code = f"label {label}"
        self.appendToFile(vm_code)

    def writeGoto(self, label):
        vm_code = f"goto {label}"
        self.appendToFile(vm_code)

    def writeIf(self, label):
        vm_code = f"if-goto {label}"
        self.appendToFile(vm_code)

    def writeCall(self, func_name, args):
        vm_code = f"call {func_name} {args}"
        self.appendToFile(vm_code)

    def writeFunction(self, func_name, vars):
        vm_code = f"function {func_name} {vars}"
        self.appendToFile(vm_code)

    def writeReturn(self):
        vm_code = "return"
        self.appendToFile(vm_code)

    def closeFile(self):
        self.file.close()
