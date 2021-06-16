
class CoordinateHelper:

    def __init__(self, BaseNoCDimensions, SquareNoCBound):
        
        self.BaseNoCDimensions = BaseNoCDimensions
        self.SquareNoCBound = SquareNoCBound
        
        # TODO: Set stack of PEPos values, according to the square NoC algorithm
        
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
        
        def updateSquareXY():
        
            nonlocal xSquare
            nonlocal xSquareLimit
            nonlocal ySquare
            nonlocal ySquareLimit
            
            # print("Before update: ")
            # print("xSquare: " + str(xSquare))
            # print("ySquare: " + str(ySquare))
            # print("xSquareLimit: " + str(xSquareLimit))
            # print("ySquareLimit: " + str(ySquareLimit))
        
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
            
            # DEBUG 
            # print("After update: ")
            # print("xSquare: " + str(xSquare))
            # print("ySquare: " + str(ySquare))
            # print("xSquareLimit" + str(xSquareLimit))
            # print("ySquareLimit" + str(ySquareLimit) + "\n")    
            
        # Loop through every Bus
        for Bus in self.Buses:
        
            # Loop through PEs in this Bus, except for the first, which has already been updated
            for PEinBus in Bus.PEs[1:]:

                # Assigns unique network addresses according to the square NoC algorithm
                PEPos = int((ySquare * squareNoCBound) + xSquare)
                
                # Update PEPos value at current PE object
                PEinBus.PEPos = PEPos
                
                # Updates reference to current PE object at master PE dictionary
                PEs[PEPos] = PEinBus

                # Update square NoC X & Y indexes
                updateSquareXY()

        # Loop through every crossbar
        for Crossbar in self.Crossbars:

            # Loop through PEs in this Bus, except for the first, which has already been updated
            for PEinCrossbar in Crossbar.PEs[1:]:

                # Assigns unique network addresses according to the square NoC algorithm
                PEPos = int((ySquare * squareNoCBound) + xSquare)
                
                # Update PEPos value at current PE object
                PEinCrossbar.PEPos = PEPos

                # Updates reference to current PE object at master PE dictionary
                PEs[PEPos] = PEinCrossbar

                # Update square NoC X & Y indexes
                updateSquareXY()
                
        
    
        
    @staticmethod
    def sequentialToXY(PEPos):

        return PEPos % self.BaseNoCDimensions[0], PEPos / self.BaseNoCDimensions[0]

    @staticmethod
    def XYtoSequential(x, y, xMax = self.BaseNoCDimensions[0]):
    
        return (y * xMax) + x
    
    # Returns a stack of PEPos values
    def popPEPos(self):
        