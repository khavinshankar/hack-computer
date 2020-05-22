class SymbolTable:
    def __init__(self):
        self.class_table = {}
        self.func_table = {}
        self.counter = {
            "argument": 0,
            "local": 0,
            "this": 0,  # field
            "static": 0,
        }

    def startSubroutine(self):
        self.counter["argument"] = 0
        self.counter["local"] = 0
        self.func_table.clear()

    def define(self, name, type, kind):
        if kind in ("this", "static"):
            self.class_table[name] = (type, kind, self.counter[kind])
        elif kind in ("argument", "local"):
            self.func_table[name] = (type, kind, self.counter[kind])

        self.counter[kind] += 1

    def varCount(self, kind):
        return self.counter[kind]

    def getVariable(self, name):
        if name in self.func_table:
            return self.func_table[name]
        elif name in self.class_table:
            return self.class_table[name]
        else:
            return (None, None, -1)
