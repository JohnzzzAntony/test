import copy

class Base:
    def __init__(self):
        self.a = 1
    def __copy__(self):
        print(f"Base.__copy__ called")
        # This is what Django does
        try:
            res = copy.copy(super())
            print(f"copy(super()) success: {type(res)}")
            return res
        except Exception as e:
            print(f"copy(super()) failed: {e}")
            raise

class Derived(Base):
    def __init__(self):
        super().__init__()
        self.b = 2
    def __copy__(self):
        print(f"Derived.__copy__ called")
        obj = super().__copy__()
        obj.b = self.b
        return obj

d = Derived()
try:
    d2 = copy.copy(d)
    print(f"d2.a = {d2.a}, d2.b = {d2.b}")
except Exception as e:
    print(f"Final error: {e}")
