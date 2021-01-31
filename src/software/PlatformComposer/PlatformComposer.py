
import json
import sys

from AppComposer import *
from Structures import *
from PE import PE
from Injector import Injector

# TODO: Check if Python version is 3

class Platform:

    # Constructor
    def __init__(self, BaseNoCDimensions, ReferenceClock, StandaloneStruct = False, BridgeBufferSize = 512, MasterPEPos = 0, DVFSServiceID, "200"):

        #self.BaseNoC = [[None for x in range(BaseNoCDimensions[0])] for y in range(BaseNoCDimensions[1])]

        if bool(StandaloneStruct):
            self.BaseNoCDimensions = (1,1)
        else:
            self.BaseNoCDimensions = BaseNoCDimensions
            
        self.BaseNoC = [[None for y in range(BaseNoCDimensions[1])] for x in range(BaseNoCDimensions[0])]
        self.ReferenceClock = ReferenceClock  # In MHz
        self.StandaloneFlag = bool(StandaloneStruct)

        self.BridgeBufferSize = BridgeBufferSize
        
        # WARNING: Any value other than 0 for master PE location will not reflect on any actual changes as of yet, since in computeClusterClocks() a 0 value for PEPos is assumed
        self.MasterPEPos = MasterPEPos

        self.Buses = []
        self.Crossbars = []
        
        # Maps a PEPos value to its wrapper's address in base NoC
        #self.WrapperAddresses = dict()  
        
        #self.Injectors = dict()
        #self.PEs = dict()
        
        self.AllocationMap = dict()
        self.ClusterClocks = dict()
        self.Workload = None
        
        # Generate initial PE objects at every NoC address (to be replaced by a Bus/Crossbar when addStructure() is called)
        i = 0
        for y in range(BaseNoCDimensions[1]):

            for x in range(BaseNoCDimensions[0]):

                self.BaseNoC[x][y] = PE(PEPos = i, BaseNoCPos = i)
                #self.PEs[i] = self.BaseNoC[x][y]

                i += 1


    @property
    def AmountOfPEs(self):
    
        amountOfPEs = int(self.BaseNoCDimensions[0] * self.BaseNoCDimensions[1])
    
        for y in range(self.BaseNoCDimensions[1]):
            for x in range(self.BaseNoCDimensions[0]):
                if isinstance(self.BaseNoC[x][y], Structure):
                    amountOfPEs += self.BaseNoC[x][y].AmountOfPEs - 1
                
        return amountOfPEs

    
    @property
    def AmountOfWrappers(self):
    
        amountOfWrappers = int(0)
        
        for y in range(self.BaseNoCDimensions[1]):
            for x in range(self.BaseNoCDimensions[0]):
                if isinstance(self.BaseNoC[x][y], Structure):
                    amountOfWrappers += 1
        
        return amountOfWrappers

        
    @property
    def AmountOfBuses(self):
    
        amountOfBuses = int(0)
        
        for y in range(self.BaseNoCDimensions[1]):
            for x in range(self.BaseNoCDimensions[0]):
                if isinstance(self.BaseNoC[x][y], Bus):
                    amountOfBuses += 1
        
        return amountOfBuses
        

    @property
    def AmountOfPEsInBuses(self):
    
        amountOfPEsInBuses = []
        
        for y in range(self.BaseNoCDimensions[1]):
            for x in range(self.BaseNoCDimensions[0]):
                if isinstance(self.BaseNoC[x][y], Bus):
                    amountOfPEsInBuses.append(int(self.BaseNoC[x][y].AmountOfPEs))
                    
        return amountOfPEsInBuses
        
        
    @property
    def BusWrapperAddresses(self):
    
        busWrapperAddresses = []
            
        for y in range(self.BaseNoCDimensions[1]):
            for x in range(self.BaseNoCDimensions[0]):
                if isinstance(self.BaseNoC[x][y], Bus):
                    busWrapperAddresses.append((y * self.BaseNoCDimensions[0]) + x)

        return busWrapperAddresses
        
        
    @property
    def IsStandaloneBus(self):
    
        if self.AmountOfBuses == 1 and isinstance(self.BaseNoC[0][0], Bus) and self.BaseNoCDimensions == (1,1) and bool(self.StandaloneFlag):
            return True
        else:
            return False
            
            
    @property
    def AmountOfCrossbars(self):
    
        amountOfCrossbars = int(0)
        
        for y in range(self.BaseNoCDimensions[1]):
            for x in range(self.BaseNoCDimensions[0]):
                if isinstance(self.BaseNoC[x][y], Crossbar):
                    amountOfCrossbars += 1
                    
        return amountOfCrossbars 
        
        
    @property
    def AmountOfPEsInCrossbars(self):
    
        amountOfPEsInCrossbars = []
        
        for y in range(self.BaseNoCDimensions[1]):
            for x in range(self.BaseNoCDimensions[0]):
                if isinstance(self.BaseNoC[x][y], Crossbar):
                    amountOfPEsInCrossbars.append(int(self.BaseNoC[x][y].AmountOfPEs))
                    
        return amountOfPEsInCrossbars
        
        
    @property
    def CrossbarWrapperAddresses(self):
    
        crossbarWrapperAddresses = []
            
        for y in range(self.BaseNoCDimensions[1]):
            for x in range(self.BaseNoCDimensions[0]):
                if isinstance(self.BaseNoC[x][y], Crossbar):
                    crossbarWrapperAddresses.append((y * self.BaseNoCDimensions[0]) + x)

        return crossbarWrapperAddresses
        
        
    @property
    def IsStandaloneCrossbar(self):
    
        if self.AmountOfCrossbars == 1 and isinstance(self.BaseNoC[0][0], Crossbar) and self.BaseNoCDimensions == (1,1) and bool(self.StandaloneFlag):
            return True
        else:
            return False
        
    
    @property
    def SquareNoCBound(self):
    
        import math
        squareNoCBound = int(math.ceil(math.sqrt(self.AmountOfPEs)))
        
        if self.BaseNoCDimensions[0] > squareNoCBound:
            return BaseNoCDimensions[0]
            
        elif self.BaseNoCDimensions[1] > squareNoCBound:
            return BaseNoCDimensions[1]
        
        else:
            return squareNoCBound   
            
           
    @property
    def PEs(self):  # Updates PE objects with workload info (PE objects are created only at Platform.__init__(), Structure.__init__() and Platform.resizeBaseNoC())
    
        # DEBUG
        print("Setting PEs")
    
        # PEs[PEPos] = (PE Object)
        PEs = [None] * self.AmountOfPEs
        
        # Gets local copy of SquareNoCBound value, in order to not perform many square root computations due to getter method
        squareNoCBound = self.SquareNoCBound   
        
        # Sets PEs in Base NoC and first PE of Bus/Crossbar
        for y in range(self.BaseNoCDimensions[1]):
        
            for x in range(self.BaseNoCDimensions[0]):
           
                # Unique network ID based on square NoC algorithm
                PEPos = int((y * squareNoCBound) + x)

                if isinstance(self.BaseNoC[x][y], PE):
                
                    #with PEinNoC as self.BaseNoC[x][y]:
                    PEinNoC = self.BaseNoC[x][y]
                        
                    # Sets PEPos value
                    PEinNoC.PEPos = PEPos
                    
                    # Updates PE list
                    PEs[PEPos] = PEinNoC
                    
                    # Updates PE object with Workload info
                    if self.Workload is not None and self.AllocationMap is not None:
                        
                        #PEPos = self.BaseNoC[x][y].PEPos
                        #PEThread = self.AllocationMap[PEPos]  # TODO: Build such that AllocMap[PEPos] = (Thread object)
                        #self.BaseNoC[x][y] = PE(PEPos = PEPos, CommStructure = "NoC", Thread = PEThread, InjectorClockFrequency = self.ReferenceClock)
                        PEinNoC.updateWorkloadInfo(ThreadSet = self.AllocationMap[PEinNoC.PEPos])
                    
                elif isinstance(self.BaseNoC[x][y], Structure):
                
                    #self.BaseNoC[xBase][yBase].PEs[0].PEPos = PEPos
                    #self.PEs[PEPos] = self.BaseNoC[xBase][yBase].PEs[0]
                
                    #with PEinStruct as self.BaseNoC[x][y].PEs[0]:
                    PEinStruct = self.BaseNoC[x][y].PEs[0]
                    
                    # Sets PEPos value to first PE of this Structure
                    PEinStruct.PEPos = PEPos
                    
                    # Updates PE list
                    PEs[PEPos] = PEinStruct
                
                    #PEs[PEinStruct.PEPos] = PEinStruct
                    
                    # Updates PE object with Workload info
                    if self.Workload is not None and self.AllocationMap is not None:
                        PEinStruct.updateWorkloadInfo(ThreadSet = self.AllocationMap[PEinStruct.PEPos])
        
        
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
                
                # Updates PE object with Workload info
                if self.Workload is not None and self.AllocationMap is not None:
                    
                    PEinBus.updateWorkloadInfo(ThreadSet = self.AllocationMap[PEinBus.PEPos])

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
                
                # Updates PE object with Workload info
                if self.Workload is not None and self.AllocationMap is not None:
                    
                    PEinCrossbar.updateWorkloadInfo(ThreadSet = self.AllocationMap[PEinCrossbar.PEPos])

                # Update square NoC X & Y indexes
                updateSquareXY()
        
        # DEBUG
        print("PEs set")
        
        return PEs
    
    
    @property
    # Injectors[PEPos][Thread] = [Injector object, Injector object, ...]
    def Injectors(self):
        
        if self.AllocationMap is None:
            print("Warning: No allocation map has been set, so no Injectors can be instantiated.")
            return [None] * self.AmountOfPEs
            
        else:
            # AllocationMap[PEPos] = [Thread object, Thread object, ...]
            #return [[[Injector(Flow = OutgoingFlow) for OutgoingFlow in Thread.OutgoingFlows] for Thread in ThreadSet] for ThreadSet in self.AllocationMap.values()]
            return [[[Injector(Flow = OutgoingFlow) for OutgoingFlow in Thread.OutgoingFlows] for Thread in ThreadSet] if isinstance(ThreadSet, list) else [[Injector(Flow = OutgoingFlow) for OutgoingFlow in ThreadSet.OutgoingFlows]] if isinstance(ThreadSet, Thread) else [[None]] for ThreadSet in self.AllocationMap.values()]
            
            injectors = []
            for ThreadSet in self.AllocationMap.values():
            
                if isinstance(ThreadSet, Thread):
                
                    ThreadInSetList = [[Injector(Flow = OutgoingFlow) for OutgoingFlow in ThreadInSet.OutgoingFlows]]
                    injectors.append(ThreadInSetList)
                    
                elif isinstance(ThreadSet, list):
                
                    ThreadInSetList = [[Injector(Flow = OutgoingFlow) for OutgoingFlow in ThreadInSet.OutgoingFlows] for ThreadInSet in ThreadSet]

                    for ThreadInSet in ThreadSet:
                    
                        InjList = [Injector(Flow = OutgoingFlow) for OutgoingFlow in ThreadInSet.OutgoingFlows]
                        
                        for OutgoingFlow in ThreadInSet.OutgoingFlows:
                            InjList.append(Injector(Flow = OutgoingFlow))
                            
                        ThreadInSetList.append(InjList)
                        
                    injectors.append(ThreadInSetList)
    
    @property
    def WrapperAddresses(self):
    
        # WrapperAddresses[PEPos] = ADDR of PEs[PEPos] in base NoC
        wrapperAddresses = [None] * self.AmountOfPEs
        
        for y in range(self.BaseNoCDimensions[1]):
            for x in range(self.BaseNoCDimensions[0]):
            
                if isinstance(self.BaseNoC[x][y], PE):
                    wrapperAddresses[int((y * self.SquareNoCBound) + x)] = int(((y * self.BaseNoCDimensions[0]) + x))
                    
                elif isinstance(self.BaseNoC[x][y], Structure):
                    for PEinStruct in self.BaseNoC[x][y].PEs:
                        wrapperAddresses[PEinStruct.PEPos] = self.BaseNoC[x][y].BaseNoCPos
        
        #print(str(wrapperAddresses) + "\n")
        return wrapperAddresses
        
    
    # Forces setting of PEPos values in PE objects. Useful for when self.PEs getter method is never called, such as when generating Platform from JSON, but PE addresses still must be set.
    def updatePEAddresses(self):

        for PEinPlatform in self.PEs:
            
            xCoord = int(PEinPlatform.BaseNoCPos % self.BaseNoCDimensions[0])
            yCoord = int(PEinPlatform.BaseNoCPos / self.BaseNoCDimensions[0])
            
            if isinstance(self.BaseNoC[xCoord][yCoord], PE):
                self.BaseNoC[xCoord][yCoord].PEPos = PEinPlatform.PEPos
                
            elif isinstance(self.BaseNoC[xCoord][yCoord], Structure):
                #self.BaseNoC[xCoord][yCoord].PEs[PEinPlatform.PosInStruct].PEPos = PEinPlatform.PEPos
                self.BaseNoC[xCoord][yCoord].PEs[PEinPlatform.StructPos].PEPos = PEinPlatform.PEPos
                
    
    # Alters BaseNoC dimensions
    def resizeBaseNoC(self, NewBaseNoCDimensions):
    
        # Checks if NewBaseNoCDimensions is a 2 dimensonal tuple/list, containing updated XY coordinates for base NoC
        if len(tuple(NewBaseNoCDimensions)) != 2:
            print("Error: Unexpected NewBaseNoCDimensions <" + str(NewBaseNoCDimensions) + "> (must be a tuple/list of length 2: (XSize, YSize))")
            exit(1)
        
        newBaseNoC = [[None for y in range(BaseNoCDimensions[1])] for x in range(BaseNoCDimensions[0])]
        
        # Creates PEs in all base NoC locations
        i = 0
        for y in range(BaseNoCDimensions[1]):

            for x in range(BaseNoCDimensions[0]):

                newBaseNoC[x][y] = PE(PEPos=i, BaseNoCPos = i, AppID=None, ThreadID=None, InjectorClockFrequency=self.ReferenceClock)
                self.PEs[i] = newBaseNoC[x][y]

                i += 1
        
        # Adds Buses at same XY coordinates
        Buses = self.Buses
        
        for Bus in Buses:
        
            # Tuple of (X,Y) in base NoC
            XYAddr = tuple([int(Bus.BaseNoCPos % self.BaseNoCDimensions[0]), int(Bus.BaseNoCPos / self.BaseNoCDimensions[0])])
            
            # Tries to add same struct in new base NoC at same XY coordinates
            try:
                newBaseNoC[XYAddr[0]][XYAddr[1]] = Bus
                
            # XYAddr doesnt exist in new Base NoC, remove it from Platform
            except IndexError or KeyError:
                print("Warning: Bus <" + str(Bus) + "> will be removed from Platform, since its original XY coordinates in base NoC dont exist anymore")
                Buses.remove(Bus)
                pass
        
        # Updates Platform with new Bus list
        self.Buses = Buses
        
        # Adds Crossbars at same XY coordinates
        Crossbars = self.Crossbars
        
        for Crossbar in Crossbars:
        
            # Tuple of (X,Y) in base NoC
            XYAddr = tuple([int(Crossbar.BaseNoCPos % self.BaseNoCDimensions[0]), int(Crossbar.BaseNoCPos / self.BaseNoCDimensions[0])])
            
            # Tries to add same struct in new base NoC at same XY coordinates
            try:
                newBaseNoC[XYAddr[0]][XYAddr[1]] = Crossbar
                
            # XYAddr doesnt exist in new Base NoC, remove it from Platform
            except IndexError or KeyError:
                print("Warning: Crossbar <" + str(Crossbar) + "> will be removed from Platform, since its original XY coordinates in base NoC dont exist anymore")
                Crossbars.remove(Crossbar)
                pass
        
        # Updates Platform with new Crossbar list
        self.Crossbars = Crossbars
        
        # Updates Platform base NoC with new base NoC
        self.BaseNoC = newBaseNoC
        
    
    # Adds structure (Bus or Crossbar) to base NoC
    def addStructure(self, NewStructure, WrapperLocationInBaseNoC):
    
        # Checks if NewStructure is a Structure object (describing either a Bus or Crossbar)
        if not isinstance(NewStructure, Structure):
            print("Error: Given NewStructure <" + str(NewStructure) + "> is not a Struct object (Bus or Crossbar)")
            exit(1)
    
        # Checks if WrapperLocationInBaseNoC is a 2 dimensonal tuple/list, containing XY coordinates for Bus/Crossbar to be added to Platform
        if len(tuple(WrapperLocationInBaseNoC)) != 2:
            print("Error: Unexpected WrapperLocationInBaseNoC <" + str(WrapperLocationInBaseNoC) + "> (must be a tuple/list of length = 2: (XSize, YSize))")
            exit(1)
        
        # Checks if given XY coordinates for new Bus/Crossbar exist in base NoC
        try:
            self.BaseNoC[WrapperLocationInBaseNoC[0]][WrapperLocationInBaseNoC[1]]

        # Given XY coordinates for new Bus/Crossbar dont exist in base NoC
        except IndexError or KeyError: 
            print("Error: Given XY coordinates <" + str(WrapperLocationInBaseNoC) + "> for new Bus/Crossbar dont exist in base NoC (Base NoC dimensions: " + str(self.BaseNoCDimensions) + ")")
            exit(1)
            
        # Checks for a Bus/Crossbar at given location in base NoC
        if isinstance(self.BaseNoC[WrapperLocationInBaseNoC[0]][WrapperLocationInBaseNoC[1]], Structure):

            # There already is a Bus/Crossbar at this position in base NoC
            print("Error: There already is a " + str(self.BaseNoC[WrapperLocationInBaseNoC[0]][WrapperLocationInBaseNoC[1]].StructureType) + " at given location <" + str(WrapperLocationInBaseNoC) + ">")
            exit(1)    
        
        # Inserts given structure into base NoC
        if str(NewStructure.StructureType).casefold() == "bus":
            self.Buses.append(NewStructure)
            #print("Added Bus containing " + str(NewStructure.AmountOfPEs) + " elements @ base NoC " + str(WrapperLocationInBaseNoC))

        elif str(NewStructure.StructureType).casefold() == "crossbar":
            self.Crossbars.append(NewStructure)
            #print("Added Crossbar containing " + str(NewStructure.AmountOfPEs) + " elements @ base NoC " + str(WrapperLocationInBaseNoC))
            
        else:
            print("Error: Given StructureType <" + str(NewStructure.StructureType) + "> not recognized")
            exit(1)

        self.BaseNoC[WrapperLocationInBaseNoC[0]][WrapperLocationInBaseNoC[1]] = NewStructure
        NewStructure.BaseNoCPos = (WrapperLocationInBaseNoC[1] * self.BaseNoCDimensions[0]) + WrapperLocationInBaseNoC[0]
        
        for PEinStruct in NewStructure.PEs:
            PEinStruct.BaseNoCPos = (WrapperLocationInBaseNoC[1] * self.BaseNoCDimensions[0]) + WrapperLocationInBaseNoC[0]


    # Removes a given Bus/Crossbar (either as a Structure object <StructToRemove> or XY coordinates in base NoC <WrapperLocationInBaseNoC>) from Platform
    def removeStructure(self, StructToRemove = None, WrapperLocationInBaseNoC = None):
    
        # Checks if both StructToRemove and WrapperLocationInBaseNoC are None
        if StructToRemove is None and WrapperLocationInBaseNoC is None:
        
            print("Warning: Both <StructToRemove> and <WrapperLocationInBaseNoC> given arguments are None. removeStructure() will do nothing")
            return None
            
        # 
        elif StructToRemove is not None and WrapperLocationInBaseNoC is None:
        
            # Checks if StructToRemove is a Structure object, describing either a Bus or Crossbar
            if not isinstance(StructToRemove, Structure):
            
                print("Error: Given StructToRemove <" + str(StructToRemove) + "> is not a Structure object (describing either a Bus or Crossbar)")
                exit(1)
    
            # Checks if StructToRemove is a Bus
            if isinstance(StructToRemove, Bus):
            
                # Removes StructToRemove from Bus list
                try:
                    return Buses.remove(StructToRemove)
                    
                except ValueError:
                    print("Warning: Bus <" + str(StructToRemove) + "> doesnt exist in this Platform")
                    return None
            
            # Checks if StructToRemove is a Crossbar
            elif isinstance(StructToRemove, Crossbar):
            
                # Removes StructToRemove from Crossbar list
                try:
                    return Crossbars.remove(StructToRemove)
                    
                except ValueError:
                    print("Warning: Crossbar <" + str(StructToRemove) + "> doesnt exist in this Platform")
                    return None
                    
            else:
                print("Error: Given Structure is of a different kind than Bus or Crossbar")
                exit(1)
        
        elif StructToRemove is None and WrapperLocationInBaseNoC is not None:
        
            # Checks if WrapperLocationInBaseNoC is a 2 dimensonal tuple/list, containing updated XY coordinates for base NoC
            if len(tuple(WrapperLocationInBaseNoC)) != 2:
                print("Error: Unexpected WrapperLocationInBaseNoC <" + str(WrapperLocationInBaseNoC) + "> (must be a tuple/list of length = 2: (XSize, YSize))")
                exit(1)
            
            try:
                Struct = self.BaseNoC[WrapperLocationInBaseNoC[0]][WrapperLocationInBaseNoC[1]]
                
            except IndexError or KeyError:
                print("Error: Given WrapperLocationInBaseNoC <" + str(WrapperLocationInBaseNoC) + "> doesnt not correspond to a valid XY coordinate in base NoC (Base NoC dimensions = " + str(self.BaseNoCDimensions) + ")")
                exit(1)
                
            else:
                return self.removeStructure(StructToRemove = Struct)
        
        elif StructToRemove is not None and WrapperLocationInBaseNoC is not None:
        
            try: 
                StructInBaseNoC = self.BaseNoC[WrapperLocationInBaseNoC[0]][WrapperLocationInBaseNoC[1]]
            
            except IndexError or KeyError: 
                print("Error: Given WrapperLocationInBaseNoC <" + str(WrapperLocationInBaseNoC) + "> doesnt not correspond to a valid XY coordinate in base NoC (Base NoC dimensions = " + str(self.BaseNoCDimensions) + ")")
                exit(1)
                
            else:
                
                if StructInBaseNoC is StructToRemove:
                    return self.removeStructure(StructToRemove = StructInBaseNoC)
                    
                else:
                    print("Warning: Given StructInBaseNoC <" + str(StructToRemove) + "> and WrapperLocationInBaseNoC <" + str(WrapperLocationInBaseNoC) + "> correspond to different Structure objects. removeStructure() will do nothing")
                    return None


    # Associates a Workload object (from AppComposer module) to Platform
    def setWorkload(self, Workload):

        # TODO: Check if AllocationMap has already been set, and if so, update given Workload with allocation information, so that setAllocationMap() doesnt have to be called again

        Workload.ParentPlatform = self
        self.Workload = Workload


    # Sets allocation map (Maps AppID and ThreadID to an unique PE)
    def setAllocationMap(self, AllocationMap):
    
        # AllocationMap[PEPos] = Thread object, str (ThreadName), List or Dict of Thread objects

        if len(AllocationMap) > self.AmountOfPEs:
            print("Error: Amount of PEs in given AllocationMap <" + str(len(AllocationMap)) + "> exceeds amount of PEs in Platform (" + str(self.AmountOfPEs) + ")")
            exit(1)
        
        # Sets PEPos values for Threads in Workload
        for PEPos, ThreadInAllocMap in enumerate(AllocationMap):
            
            if isinstance(ThreadInAllocMap, Thread):

                # TODO: Find Thread in Workload wich is identical to thread in AllocMap dict and set its PEPos value
                #ThreadInAllocMap.PEPos = PEPos
                NotImplementedError

            elif isinstance(ThreadInAllocMap, str):

                if self.Workload is None:
                    print("Error: Thread lookup by ThreadName parameter is impossible if Workload hasnt been set before calling setAllocationMap()")
                    exit(1)

                ThreadInWorkload = self.Workload.getThread(ThreadName = ThreadInAllocMap)
                
                # DEBUG
                #print(ThreadInWorkload)
                #print("Thread object ID: " + str(id(ThreadInWorkload)))
                
                if ThreadInWorkload.PEPos is None:
                
                    ThreadInWorkload.PEPos = PEPos
                    ThreadInWorkload.BaseNoCPos = self.PEs[PEPos].BaseNoCPos
                    
                    # Allocated PE is in a Bus/Crossbar
                    try:
                        for PE in self.BaseNoC[PEPos % self.SquareNoCBound][PEPos / self.SquareNoCBound].PEs:
                            if PEPos = PE.PEPos:
                                ThreadInWorkload.StructPos = PE.StructPos
                            
                    # Allocated PE is in base NoC
                    except AttributeError:
                        ThreadInWorkload.StructPos = self.BaseNoC[PEPos % self.SquareNoCBound][PEPos / self.SquareNoCBound].StructPos
                            
                    self.AllocationMap[PEPos] = ThreadInWorkload
                    
                else:
                
                    print("Error: Thread <" + str(ThreadInWorkload) + "> has already been allocated at PEPos <" + str(ThreadInWorkload.PEPos) + ">")
                    exit(1)
                
            elif isinstance(ThreadInAllocMap, list):  # Assumes "ThreadInAllocMap" is a list of strings (Thread names)
            
                if self.Workload is None:
                    print("Error: Thread lookup by ThreadName parameter is impossible if Workload hasnt been set before calling setAllocationMap()")
                    exit(1)
                
                ThreadSet = [self.Workload.getThread(ThreadName = ThreadName) for ThreadName in ThreadInAllocMap]
                
                #ThreadInWorkload.PEPos = PEPos
                for ThreadInSet in ThreadSet:
                
                    ThreadInSet.PEPos = PEPos
                    ThreadInSet.BaseNoCPos = self.PEs[PEPos].BaseNoCPos
                    
                    try:
                        for PE in self.BaseNoC[PEPos % self.SquareNoCBound][PEPos / self.SquareNoCBound].PEs:
                            if PEPos = PE.PEPos:
                                ThreadInSet.StructPos = PE.StructPos
                            
                    # Allocated PE is in base NoC
                    except AttributeError:
                        ThreadInSet.StructPos = self.BaseNoC[PEPos % self.SquareNoCBound][PEPos / self.SquareNoCBound].StructPos
                    
                # TODO: Check if allocated Threads allocated to a same PE communicate between themselves, and if so, dont generate Injectors for those Flows
                    
                self.AllocationMap[PEPos] = ThreadSet
            
            elif ThreadInAllocMap is None:

                print("Warning: PEPos <" + str(PEPos) + "> has no Thread allocated")
                self.AllocationMap[PEPos] = None

            else:

                print("Error: <ThreadInAllocMap>'s type is not a Thread object, string, list or None")
                exit(1)
        
        #self.AllocationMap = AllocationMap

    
    # Sets Cluster Clock info, given either by periods or frequencies
    def setClusterClocks(self, ClusterClocks):
    
        # ClusterClocks["ClusterClocksPeriods"][AddrInBaseNoC] = Cluster clock period, in ns
        
        if isinstance(ClusterClocks, dict) and "ClusterClockPeriods" in ClusterClocks.keys():
            self.ClusterClocks = ClusterClocks["ClusterClockPeriods"]

        elif isinstance(ClusterClocks, dict) and "ClusterClockFrequencies" in ClusterClocks.keys():
            self.ClusterClocks = [float(1000/ClusterClocks["ClusterClockPeriods"][Cluster]) for Cluster in ClusterClocks["ClusterClockPeriods"]]  # MHz -> ns

        else:

            # Assumes values are periods (in nanoseconds)
            self.ClusterClocks = ClusterClocks
        
    
    # Defines cluster clocks from computed link usage
    def computeClusterClocks(self, Policy = "RMSD"):
        
        if self.Workload is None:
            print("Error: A Workload has not yet been defined. Aborting computeLinkUsage()")
            exit(1)
            
        if self.AllocationMap is None:
            print("Error: An Allocation Map has not yet been defined. Aborting computeLinkUsage()")
            exit(1)   
            
        import numpy
            
        def SequentialToXY(SequentialCoord):
            return SequentialCoord % self.BaseNoCDimensions[0], SequentialCoord / self.BaseNoCDimensions[0]
           
           
        def XYToSequential(XYTuple):
            return (XYTuple[1] * self.BaseNoCDimensions[0]) + XYTuple[0]
               
        # Returns a list of routers according to the XY routing algorithm
        def RouteFlow(FlowToRoute, TimeBarriers, RoutingAlgorithm = "XY", GenDVFSInjectors = False):
            
            SourceX, SourceY = SequentialToXY(FlowToRoute.SourceThread.BaseNoCPos)
            TargetX, TargetY = SequentialToXY(FlowToRoute.TargetThread.BaseNoCPos)
            
            # [XDimension][YDimension][Port][TimeBarrier]
            # Ports as numbers: EAST = 0, WEST = 1, NORTH = 2, SOUTH = 3, LOCAL = 4;
            OutputPortUsage = [[[[0 for TimeBarrier in TimeBarriers] for i in range(5)] for y in range(self.BaseNoCDimensions[1])] for x in range(self.BaseNoCDimensions[0])]
            InputPortUsage = [[[[0 for TimeBarrier in TimeBarriers] for i in range(5)] for y in range(self.BaseNoCDimensions[1])] for x in range(self.BaseNoCDimensions[0])]
            
            if RoutingAlgorithm = "XY":
                RouterList = [(X, SourceY) for X in range(SourceX, TargetX + 1] + [(TargetX, Y) for Y in range(SourceY, TargetY + 1)]
            
            FlowTimeBarriers = []
            for TimeBarrier in TimeBarriers:
                if TimeBarrier >= FlowToRoute.StartTime and (TimeBarrier <= FlowToRoute.StopTime or FlowToRoute.StopTime == -1):
                    FlowTimeBarriers.append(TimeBarrier)
                    
            # Set router ports along the routed path
            for i, Router in enumerate(RouterList):
            
                X = Router[0]
                Y = Router[1]
                
                OutputLink = None
                InputLink = None
                
                try:
                    NextX = RouterList[i+1][0]
                    NextY = RouterList[i+1][1]
                    
                # Last router in path, set local ports and return
                except IndexError:  
                    OutputPortUsage[SourceX][SourceY][4][TimeBarrier] = FlowToRoute.Bandwidth
                    InputPortUsage[TargetX][TargetY][4][TimeBarrier] = FlowToRoute.Bandwidth
                    break
                
                # Horizontal movement
                if NextX != X:
                
                    # West -> East
                    if NextX > X:
                        OutputLink = 1
                        InputLink = 0
                        
                    # East -> West
                    else:
                        OutputLink = 0
                        InputLink = 1

                # Vertical movement
                else:
                
                    # South -> North
                    if NextY > Y:
                        OutputLink = 3
                        InputLink = 2
                        
                    # North -> South
                    else:
                        OutputLink = 2
                        InputLink = 3
                
                for TimeBarrier in FlowTimeBarriers:
                
                    OutputPortUsage[X][Y][OutputLink][TimeBarrier] = FlowToRoute.Bandwidth
                    InputPortUsage[NextX][NextY][InputLink][TimeBarrier] = FlowToRoute.Bandwidth
            
            FlowLinkUsage = [[[[max(OutputPortUsage[x][y][i][TimeBarrier], InputPortUsage[x][y][i][TimeBarrier]) for TimeBarrier in TimeBarriers] for i in range(5)] for y in range(self.BaseNoCDimensions[1])] for x in range(self.BaseNoCDimensions[0])]
            return numpy.array(FlowLinkUsage)
        
        # TODO: Check if any Flows have hard real-time restrictions
        
        # Finds all Flow StartTime and StopTime values
        TimeBarriers = []
        
        for App in self.Workload.Applications:
            for ThreadInApp in App:
                for OutgoingFlow in ThreadInApp.OutgoingFlows:
                
                    if OutgoingFlow.StartTime not in TimeBarriers:
                        TimeBarriers.append(OutgoingFlow.StartTime)
                        
                    if OutgoingFlow.StopTime not in TimeBarriers:
                        TimeBarriers.append(OutgoingFlow.StopTime)
             
        TimeBarriers.sort()
        
        # For Routers set clock according to the max of its links usages. 
        # For Buses, set it as the sum of usages of PEs in it + local port of associated router
        # For Crossbars, set it as the max of usages of PEs in it + local port of associated router
        
        BusUsage = [[0 for TimeBarrier in TimeBarriers] for BusInPlat in self.Buses]
        #CrossbarUsage = [[[0 for PosInStruct in range(CrossbarInPlat.AmountOfPEs)] for TimeBarrier in TimeBarriers] for CrossbarInPlat in self.Crossbars] 
        CrossbarOutputUsage = [[[0 for TimeBarrier in TimeBarriers] for PosInStruct in range(CrossbarInPlat.AmountOfPEs)] for CrossbarInPlat in self.Crossbars] 
        CrossbarInputUsage = [[[0 for TimeBarrier in TimeBarriers] for PosInStruct in range(CrossbarInPlat.AmountOfPEs)] for CrossbarInPlat in self.Crossbars] 
        NoCLinkUsage = numpy.array([[[[0 for TimeBarrier in TimeBarriers] for i in range(5)] for y in range(self.BaseNoCDimensions[1])] for x in range(self.BaseNoCDimensions[0])])

        # Compute NoC link and Bus/Crossbar usages
        for App in self.Workload.Applications:
            for ThreadInApp in App:
                for OutgoingFlow in ThreadInApp.OutgoingFlows:
                    
                    # Bus/Crossbar -> Bus/Crossbar
                    #if OutgoingFlow.SourceThread.BaseNoCPos = BusinPlat.BaseNoCPos:
                    if OutgoingFlow.SourceThread.BaseNoCPos = OutgoingFlow.TargetThread.BaseNoCPos:
                    
                        FlowTimeBarriers = []
                        for TimeBarrier in TimeBarriers:
                            if TimeBarrier >= OutgoingFlow.StartTime and (TimeBarrier <= OutgoingFlow.StopTime or OutgoingFlow.StopTime == -1):
                                FlowTimeBarriers.append(TimeBarrier)
                        
                        BaseNoCX, BaseNoCY = SequentialToXY(OutgoingFlow.SourceThread.BaseNoCPos)
                        
                        # Source Struct = Bus
                        if isinstance(self.BaseNoC[BaseNoCX][BaseNoCY], Bus):
                            for TimeBarrier in FlowTimeBarriers:
                                BusUsage[i][TimeBarrier] += OutgoingFlow.Bandwidth
                           
                        # Source Struct = Crossbar
                        elif isinstance(self.BaseNoC[BaseNoCX][BaseNoCY], Crossbar):
                            for TimeBarrier in FlowTimeBarriers:
                                CrossbarOutputUsage[i][OutgoingFlow.SourceThread.StructPos][TimeBarrier] += OutgoingFlow.Bandwidth
                                CrossbarInputUsage[i][OutgoingFlow.TargetThread.StructPos][TimeBarrier] += OutgoingFlow.Bandwidth
                    
                    else:
                    
                        NoCLinkUsage += RouteFlow(OutgoingFlow, TimeBarriers)
             
        # Compute final usages per cluster
        RouterUsage = [0] * (self.BaseNoCDimensions[0] * self.BaseNoCDimensions[1])
        BusUsage = numpy.array(BusUsage)
        CrossbarUsage = numpy.array([[[max(CrossbarOutputUsage[i][PosInStruct][TimeBarrier], CrossbarInputUsage[i][PosInStruct][TimeBarrier]) for TimeBarrier in TimeBarriers] for PosInStruct in range(CrossbarInPlat.AmountOfPEs)] for i, CrossbarInPlat in enumerate(self.Crossbars)])
        BusCount = 0
        CrossbarCount = 0           
        
        if not GenDVFSInjectors:
        
            # Compute max bandwidth per router
            for x in range(self.BaseNoCDimensions[0]):
                for y in range(self.BaseNoCDimensions[1]):
                
                    # Add local Bus usage to associated router's local port
                    if isinstance(self.BaseNoC[x][y], Bus):
                    
                        NoCLinkUsage[x][y][4] += BusUsage[BusCount]
                        BusCount += 1
                        
                    # Set local Crossbar usage to associated router's local port
                    elif isinstance(self.BaseNoC[x][y], Crossbar):
                    
                        NoCLinkUsage[x][y][4] = numpy.amax(CrossbarUsage[CrossbarCount])
                        CrossbarCount += 1
                    
                    # Set router usage as max of link usages
                    RouterUsage[XYToSequential((x,y))] = numpy.amax(NoCLinkUsage[x][y])
                    
            # Compute periods (in nanoseconds) such that the calculated bandwidth is provided
            # self.InjectorClockPeriod = (DataWidth / 8) / (Flow.Bandwidth * 1000)  # in nanoseconds
            ClusterClocks = [(32 / 8) / (MaxBandwidthPerRouter * 1000) for MaxBandwidthPerRouter in RouterUsage]
            return ClusterClocks
        
        else:
        
            # Compute max bandwidth per router
            for x in range(self.BaseNoCDimensions[0]):
                for y in range(self.BaseNoCDimensions[1]):
                
                    # Add local Bus usage to associated router's local port
                    if isinstance(self.BaseNoC[x][y], Bus):
                    
                        NoCLinkUsage[x][y][4] += BusUsage[BusCount]
                        BusCount += 1
                        
                    # Set local Crossbar usage to associated router's local port
                    elif isinstance(self.BaseNoC[x][y], Crossbar):
                    
                        for TimeBarrier in TimeBarriers:
                            
                            CrossbarUsagePerTimeBarrier = [UsagePerPosInStruct[TimeBarrier] for UsagePerPosInStruct in CrossbarUsage[CrossbarCount]]
                            NoCLinkUsage[x][y][4][TimeBarrier] = numpy.amax(LocalCrossbarUsage)
                            
                        CrossbarCount += 1
                    
                    # Set router usage as max of link usages
                    #RouterUsage[XYToSequential((x,y))] = numpy.amax(NoCLinkUsage[x][y])
                    
            # Generates DVFS config injectors for every cluster for every time barrier
            DVFSControlThread = AppComposer.Thread(ThreadName = "DVFSControlThread")
            # TODO: Make DVFSControlThread.PEPos = self.MasterPEPos and determine BaseNoCPos and StructPos accordingly
            DVFSControlThread.PEPos = 0
            DVFSControlThread.BaseNoCPos = 0
            DVFSControlThread.StructPos = 0
            
            # TODO: Add to DVFSControlThread allocated ThreadSet
            
            for x in range(self.BaseNoCDimensions[0]):
                for y in range(self.BaseNoCDimensions[1]):
                    for TimeBarrier in TimeBarriers:
                        
                        DummyReceiverThread = AppComposer.Thread(ThreadName = "DVFSDummyReceiverThread")
                        # TODO: Add PEPos, BaseNoCPos & StructPos to DummyReceiverThread
                        
                        DVFSFlow = Flow(Bandwidth = 100, SourceThread = DVFSControlThread, TargetThread = DummyReceiverThread, StartTime = TimeBarrier, MSGAmount = 1, ControlFlowFlag = True)
                        DVFSControlThread.addFlow(DVFSFlow)
                    
                        # TODO: Compute payload for DVFS control message using calibration data from syntesis
                        #getVoltageLevel(Frequency)
                        
            return True
                        
        
    # Generate JSON config files for PEs, Injectors and Platform
    def generateJSON(self, ProjectPath):

        import os

        # Checks if ProjectPath exists
        if not os.path.exists(ProjectPath):
            print("Error: Given <ProjectPath: " + str(ProjectPath) + "> doesnt exist. Did you run \"projgen\"?")
            exit(1)
        
        if self.Workload is None:
            print("Error: No Workload has been set, aborting generateJSON()")
            exit(1)
            
        if self.AllocationMap is None:
            print("Error: No AllocationMap has been set, aborting generateJSON()")
            exit(1)

        # Checks if all Threads in Workload have been allocated (Thread.PEPos is not None)
        for App in self.Workload.Applications:
        
            for ThreadInApp in App.Threads:
                
                if ThreadInApp.PEPos is None:
                
                    print("Error: Thread <\n" + str(ThreadInApp) + "\n> has not been allocated, aborting generateJSON()")
                    exit(1)
                
                elif ThreadInApp.PEPos > self.AmountOfPEs - 1:
                
                    print("Error: Thread\n" + str(ThreadInApp) + "\n's PEPos value <" + str(ThreadInApp.PEPos) + "> exceeds amount of PEs in Platform " + str(self.AmountOfPEs) + ", aborting generateJSON()")
                    exit(1)
                

        if self.ClusterClocks is None:
            print("Error: No ClusterClocks has been set, aborting generateJSON()")
            exit(1)

        if len(self.ClusterClocks) < self.BaseNoCDimensions[0] * self.BaseNoCDimensions[1]:
            print("Error: Platform ClusterClocks has different len <" + str(len(self.ClusterClocks)) + "> than expected <" + str(self.BaseNoCDimensions[0] * self.BaseNoCDimensions[1]) + ">")
            exit(1)

        if len(self.ClusterClocks) != self.BaseNoCDimensions[0] * self.BaseNoCDimensions[1]:
            print("Warning: Platform ClusterClocks has different len <" + str(len(self.ClusterClocks)) + "> than expected <" + str(self.BaseNoCDimensions[0] * self.BaseNoCDimensions[1]) + ">") 
            
        # Creates flow dirs (cant be done in projgen because AmountOfPEs information is not known at that stage)
        for i in range(self.AmountOfPEs):
            os.makedirs(ProjectPath + "/flow/PE " + str(i) + "/", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
            
        # Writes PE config files
        for i, PEinPlatform in enumerate(self.PEs):
            with open(ProjectPath + "/flow/PE " + str(i) + "/PE " + str(PEinPlatform.PEPos) + ".json", 'w') as PEFile:
                PEFile.write(PEinPlatform.toJSON())
                
        # Writes Injector config files
        for PEPos, ThreadSet in enumerate(self.Injectors):
            for ThreadNum, ThreadInSet in enumerate(ThreadSet):
                for FlowNum, Injector in enumerate(ThreadInSet):
                
                    os.makedirs(ProjectPath + "/flow/PE " + str(PEPos) + "/Thread " + str(ThreadNum) + "/", exist_ok = True)  # exist_ok argument to makedirs() only works for Python3.2+
                    
                    with open(ProjectPath + "/flow/PE " + str(PEPos) + "/Thread " + str(ThreadNum) + "/Flow " + str(FlowNum) + ".json", 'w') as INJFile:
                        #INJFile.write(InjectorInPlatform.toJSON())
                        if self.Injectors[PEPos][ThreadNum][FlowNum] is not None:
                            INJFile.write(self.Injectors[PEPos][ThreadNum][FlowNum].toJSON())
                
        # Writes Platform config file
        with open(ProjectPath + "/platform/PlatformConfig.json", 'w') as PlatformFile:
            PlatformFile.write(self.toJSON())
        
        # Writes ClusterClocks config file
        with open(ProjectPath + "/platform/ClusterClocks.json", 'w') as ClusterClocksFile:

            CCdict = dict()
            CCdict["ClusterClockPeriods"] = self.ClusterClocks

            #ClusterClocksFile.write(json.dumps(self.ClusterClocks))
            ClusterClocksFile.write(json.dumps(CCdict, sort_keys = False, indent = 4))


    def toJSON(self, SaveToFile = False, FileName = None):

        # A "hand-built" dict is required because self.__dict__ doesnt have @property decorators keys (self.AmountOfPEs, etc)
        JSONDict = dict()
        
        # General Info
        JSONDict["AmountOfPEs"] = self.AmountOfPEs
        JSONDict["AmountOfWrappers"] = self.AmountOfWrappers
        JSONDict["BaseNoCDimensions"] = self.BaseNoCDimensions
        JSONDict["ReferenceClock"] = self.ReferenceClock
        JSONDict["SquareNoCBound"] = self.SquareNoCBound
        #JSONDict["StandaloneFlag"] = self.StandaloneFlag
        #JSONDict["WrapperAddresses"] = [self.WrapperAddresses[PEPos] for PEPos in self.WrapperAddresses.keys()]  #  Dict -> List
        JSONDict["WrapperAddresses"] = self.WrapperAddresses
        JSONDict["BridgeBufferSize"] = self.BridgeBufferSize
        JSONDict["MasterPEPos"] = self.MasterPEPos

        # Bus info
        JSONDict["IsStandaloneBus"] = self.IsStandaloneBus
        JSONDict["AmountOfBuses"] = self.AmountOfBuses 
        JSONDict["AmountOfPEsInBuses"] = self.AmountOfPEsInBuses if self.AmountOfBuses > 0 else [-1]
        JSONDict["BusWrapperAddresses"] = self.BusWrapperAddresses if self.AmountOfBuses > 0 else [-1]
        
        BusPEIDs = dict()
        LargestBus = 0
        
        for i, BusInPlat in enumerate(self.Buses):
        
            BusPEIDs["Bus" + str(i)] = [PEinBus.PEPos for PEinBus in BusInPlat.PEs]
            
            if len(BusInPlat.PEs) > LargestBus:
                LargestBus = len(BusInPlat.PEs)
            
        JSONDict["BusPEIDs"] = BusPEIDs
        JSONDict["LargestBus"] = LargestBus
        
        JSONDict["BusWrapperIDs"] = [int(BusInPlat.BaseNoCPos) for BusInPlat in self.Buses]
        
        # Crossbar info
        JSONDict["IsStandaloneCrossbar"] = self.IsStandaloneCrossbar
        JSONDict["AmountOfCrossbars"] = self.AmountOfCrossbars
        JSONDict["AmountOfPEsInCrossbars"] = self.AmountOfPEsInCrossbars if self.AmountOfCrossbars > 0 else [-1]
        JSONDict["CrossbarWrapperAddresses"] = self.CrossbarWrapperAddresses if self.AmountOfCrossbars > 0 else [-1]
        
        CrossbarPEIDs = dict()
        LargestCrossbar = 0
        
        for i, CrossbarInPlat in enumerate(self.Crossbars):
        
            CrossbarPEIDs["Crossbar" + str(i)] = [PEinCrossbar.PEPos for PEinCrossbar in CrossbarInPlat.PEs]
            
            if len(CrossbarInPlat.PEs) > LargestCrossbar:
                LargestCrossbar = len(CrossbarInPlat.PEs)
            
        JSONDict["CrossbarPEIDs"] = CrossbarPEIDs
        JSONDict["LargestCrossbar"] = LargestCrossbar
        
        JSONDict["CrossbarWrapperIDs"] = [int(CrossbarInPlat.BaseNoCPos) for CrossbarInPlat in self.Crossbars]
        
        # sort_keys must be set as False so Buses and Crossbars are inserted in the same order in reconstructed Platform object
        JSONString = json.dumps(JSONDict, sort_keys = False, indent = 4)
        
        # Saves JSON-formatted string to a file
        if bool(SaveToFile):
            
            if FileName is not None:
                JSONFile = open(str(FileName) + ".json", "w")
            else:
                JSONFile = open("NewPlatform.json", "w")
                
            JSONFile.write(JSONString)
            JSONFile.close()
        
        return JSONString


    # Builds a Platform object from a given JSON formatted string
    def fromJSON(self, JSONString):
    
        # Generates dictionary from given JSON file
        JSONDict = json.loads(JSONString)
        print(JSONDict)
        
        self.BaseNoCDimensions = tuple(JSONDict["BaseNoCDimensions"])
        #self.BaseNoC = [[None for x in range(BaseNoCDimensions[0])] for y in range(BaseNoCDimensions[1])]
        self.BaseNoC = [[None for y in range(self.BaseNoCDimensions[1])] for x in range(self.BaseNoCDimensions[0])]
        self.ReferenceClock = JSONDict["ReferenceClock"]  # In MHz
        self.StandaloneFlag = True if JSONDict["IsStandaloneBus"] or JSONDict["IsStandaloneCrossbar"] else False
        #self.BridgeBufferSize = JSONDict["BridgeBufferSize"]        
        self.MasterPEPos = JSONDict["MasterPEPos"]        
        
        self.Buses = []
        self.Crossbars = []
        
        #self.Injectors = dict()
        #self.PEs = dict()
        
        self.AllocationMap = dict()
        self.ClusterClocks = dict()
        self.Workload = None
        
        # Generate initial PE objects at every NoC address (to be replaced by a wrapper when a structure is added)
        i = 0
        for y in range(self.BaseNoCDimensions[1]):

            for x in range(self.BaseNoCDimensions[0]):

                self.BaseNoC[x][y] = PE(PEPos=i, BaseNoCPos = i, CommStructure = "NoC")
                #self.PEs[i] = self.BaseNoC[x][y]

                i += 1
        
        # Add Buses to Platform
        for i, BusSize in enumerate(JSONDict["AmountOfPEsInBuses"]):
            BaseNoCTuple = (int(JSONDict["BusWrapperAddresses"][i] % self.BaseNoCDimensions[0]), int(JSONDict["BusWrapperAddresses"][i] / self.BaseNoCDimensions[0]))
            self.addStructure(Bus(AmountOfPEs = BusSize), BaseNoCTuple)

        # Add Crossbars to Platform
        for i, CrossbarSize in enumerate(JSONDict["AmountOfPEsInCrossbars"]):
            BaseNoCTuple = (int(JSONDict["CrossbarWrapperAddresses"][i] % self.BaseNoCDimensions[0]), int(JSONDict["CrossbarWrapperAddresses"][i] / self.BaseNoCDimensions[0]))
            self.addStructure(Crossbar(AmountOfPEs = CrossbarSize), BaseNoCTuple)
        

    # TODO: Print Platform info for debug
    def __str__(self):
    
        returnString = ""
        
        returnString += "Amount of PEs: " + str(self.AmountOfPEs) + "\n"
        returnString += "Base NoC Dimensions: " + str(self.BaseNoCDimensions) + "\n"
        returnString += "ReferenceClock: " + str(self.ReferenceClock) + " MHz \n"
        returnString += "SquareNoCBound: " + str(self.SquareNoCBound) + "\n\n"
        
        returnString += "Amount of Buses: " + str(self.AmountOfBuses) + "\n"
        returnString += "Amount of PEs in Buses: " + str(self.AmountOfPEsInBuses) + "\n"
        returnString += "Bus Wrapper Addresses (in base NoC): " + str(self.BusWrapperAddresses) + "\n\n"
        
        returnString += "Amount of Crossbars: " + str(self. AmountOfCrossbars) + "\n"
        returnString += "Amount of PEs in Crossbars: " + str(self.AmountOfPEsInCrossbars) + "\n"
        returnString += "Crossbar Wrapper Addresses (in base NoC): " + str(self.CrossbarWrapperAddresses) + "\n\n"
        
        return returnString
        
        
    # TODO: Implement automated comparison between 2 Platform objects for debug
    def __eq__(self):
    
        return NotImplemented
        
        
