

class MyClass:
    __static_field = "MY_CONSTANT"
    def __init__(self,name):
        self.name = name
        self._mi_private_field = "3.1416"

    def get_static_field(self):
        return __static_field



my_object = MyClass("Eduardo")

print(my_object.name)
my_object._mi_private_field = "a"

print(my_object._mi_private_field)
