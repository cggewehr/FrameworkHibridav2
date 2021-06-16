
class CoordinateHelper:

    def __init__(self, BaseNoCDimensions, SquareNoCBound):
        
        self.BaseNoCDimensions = BaseNoCDimensions
        self.SquareNoCBound = SquareNoCBound
        
        self.PEPosStack = []
        self.setPEPosStack()
        
    @staticmethod
    def sequentialToXY(PEPos):

        return PEPos % self.BaseNoCDimensions[0], PEPos / self.BaseNoCDimensions[0]

    @staticmethod
    def XYtoSequential(x, y, xMax = self.BaseNoCDimensions[0]):
    
        return (y * xMax) + x
    
    # WIP: Sets PEPos stack
    def setPEPosStack(self):
    
        self.PEPosStack = []
        
        # xSquare and ySquare represent current position in square NoC, ranging from 0 to SquareNoCBound - 1.
        xSquare = 0
        ySquare = 0
        xSquareLimit = 0
        ySquareLimit = 0
        
        # If Base NoC X dimension == Square NoC X dimension, init Square NoC X value at first X above base NoC (X = 0, Y = Base NoC Y dimension)
        if self.BaseNoCDimensions[0] == squareNoCBound:
            
            xSquare = 0
            ySquare = self.BaseNoCDimensions[1]
            
            xSquareLimit = self.BaseNoCDimensions[0]
            ySquareLimit = self.BaseNoCDimensions[1]
            
        # If Base NoC Y dimension == Square NoC Y dimension, 
        elif self.BaseNoCDimensions[1] == squareNoCBound:
        
            xSquare = self.BaseNoCDimensions[0]
            ySquare = self.BaseNoCDimensions[1] - 1
            
            xSquareLimit = self.BaseNoCDimensions[0]
            ySquareLimit = self.BaseNoCDimensions[1] - 1
            
        else:
        
            xSquare = 0
            ySquare = self.BaseNoCDimensions[1]
            
            xSquareLimit = self.BaseNoCDimensions[0]
            ySquareLimit = self.BaseNoCDimensions[1]
        
        while True:
        
            # Push PEPos value to stack
            self.PEPosStack.append(self.XYtoSequential(x = xSquare, y = ySquare, xMax = self.SquareNoCBound))
            
            # If computed PEPos values (for Bus/Crossbars) + base NoC PEs == 
            if len(self.PEPosStack) + (self.BaseNoCDimensions[0] * self.BaseNoCDimensions[1]) == self.SquareNoCBound * self.SquareNoCBound:
                self.PEPosStack = reversed(self.PEPosStack)
                break
            
            # Increment XY coordinates on square NoC
            if xSquare < xSquareLimit:
                xSquare += 1
                
            else:
                
                if ySquare > 0:
                    ySquare -= 1
                    
                else:
                
                    if self.BaseNoCDimensions[0] == squareNoCBound:
                        xSquare = 0
                        xSquareLimit += 1
                        
                    elif self.BaseNoCDimensions[1] == squareNoCBound:
                        ySquare = ySquareLimit + 1
                        ySquareLimit += 1
                        
                    else:
                        xSquare = 0
                        ySquare = ySquareLimit + 1
                        xSquareLimit += 1
                        ySquareLimit += 1
    
    # Returns a stack of PEPos values
    def popPEPosStack(self):
        
        value = self.PEPosStack.pop()
        
        if value is None:
            print("Error: No PEPos value left to give")
            exit(1)
        else:
            return value
        