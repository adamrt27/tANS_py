import bisect

class CompPoint:
    def __init__(self, point, s_tab):
        # Initialize CompPoint with given point and symbol table (s_tab)
        self.s_tab = s_tab
        self.point = point
        self.symbol = self.get_symbol()
        self.off = self.get_off()
        
    def __str__(self):
        # String representation of CompPoint
        return "Point: %d, Symbol: %d, Offset: %d" % (self.point, self.symbol, self.off)
        
    def get_symbol(self):
        # Use binary search to find the symbol
        vmin = self.s_tab["vmin"]
        idx = bisect.bisect_left(vmin, self.point)
        return idx - 1 if idx > 0 else 0
    
    def get_off(self):
        # Calculate the offset from the symbol
        return self.point - self.s_tab["vmin"][self.symbol]

class CompTensor:
    def __init__(self, tensor, s_tab):
        # Initialize CompTensor with given tensor and symbol table (s_tab)
        self.tensor = tensor
        self.shape = tensor.shape
        self.flat = tensor.flatten()
        
        # Get the symbols and offsets for each point (as a list of CompPoints)
        self.points = [CompPoint(point, s_tab) for point in self.flat]

    def update_tensor(self):
        # Update tensor with new values from self.flatten
        self.tensor = self.flatten.reshape(self.shape)
        
    def update_flatten(self):
        # Update flatten with new values from self.tensor
        self.flat = self.tensor.flatten()
        
    def to(self, type):
        # Convert tensor to a specified type and update flatten
        self.tensor = self.tensor.to(type)
        self.update_flatten()
        
        return self
