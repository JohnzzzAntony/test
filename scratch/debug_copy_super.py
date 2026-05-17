import copy

class Base:
    def __init__(self):
        self.x = 1
    def __copy__(self):
        print(f"Base.__copy__ called, super() is {super()}")
        try:
            duplicate = self.__class__.__new__(self.__class__)
            print(f"duplicate is {type(duplicate)}")
            duplicate.__dict__.update(self.__dict__)
            duplicate.y = 2
            return duplicate
        except Exception as e:
            print(f"Error in Base.__copy__: {e}")
            return None

class Derived(Base):
    def __copy__(self):
        print("Derived.__copy__ called")
        return super().__copy__()

d = Derived()
d2 = copy.copy(d)
print(f"Result: {d2}")
