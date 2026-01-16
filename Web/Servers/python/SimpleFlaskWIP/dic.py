

class M:
    def name(self):
        return "Print MClass()"

class E:
    def name(self):
        return "Print EClass()"
    

dic = {M : M().name,
       E : E().name}

for cls in dic:
    print(dic[cls]())