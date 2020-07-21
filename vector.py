class Vector:
    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y
    def magnitude(self):
        return (self.x**2+self.y**2)**.5
    def normalize(self):
        return self / self.magnitude()
    def copy(self):
        return Vector(*self)
    # Finds one of two vectors perpendicular to this vector with the same magnitude
    def perpendicular(self):
        normalized = self.normalize()
        return Vector(-normalized.y,normalized.x)*self.magnitude()
    def toInt(self):
        return Vector(int(self.x),int(self.y))
    def __add__(self,other):
        return Vector(self.x+other.x,self.y+other.y)
    def __mul__(self,other):
        return Vector(self.x*other,self.y*other)
    def __rmul__(self,other):
        return self*other
    def __truediv__(self,other):
        return self * (1/other)
    def __sub__(self,other):
        return self + other*(-1)
    def __repr__(self):
        return f"<{self.x},{self.y}>"
    def __getitem__(self,index):
        return (self.x,self.y)[index]
    def __len__(self):
        return 2
