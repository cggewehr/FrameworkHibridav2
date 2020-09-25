
import json
import sys

from AppComposer import *
from Structures import *
from PE import PE
from Injector import Injector

# TODO: Check if Python version is 3

class Platform:

    # Constructor
    def __init__(self, BaseNoCDimensions, ReferenceClock, StandaloneStruct = False):

        #self.BaseNoC = [[None for x in range(BaseNoCDimensions[0])] for y in range(BaseNoCDimensions[1])]

        if bool(StandaloneStruct):
            self.BaseNoCDimensions = (1,1)
        else:
            self.BaseNoCDimensions = BaseNoCDimensions
            
        self.BaseNoC = [[None for y in range(BaseNoCDimensions[1])] for x in range(BaseNoCDimensions[0])]
        self.ReferenceClock = ReferenceClock  # In MHz
        self.StandaloneFlag = bool(StandaloneStruct)
        
        self.Buses = []
        self.Crossbars = []
        
        # Maps a PEPos value to its wrapper's address in base NoC
        #self.WrapperAddresses = dict()  
        
        #self.Injectors = dict()
        #self.PEs = dict()
        
        self.AllocationMap = dict()
        self.ClusterClocks = dict()
        self.Workload = None
        
        # Generate initial PE objects at every NoC address (to be replaced by a wrapper when a structure is added)
        i = 0
        for y in range(BaseNoCDimensions[1]):

            for x in range(BaseNoCDimensions[0]):

                self.BaseNoC[x][y] = PE(PEPos = i, AddressInBaseNoC = i, CommStructure = "NoC", InjectorClockFrequency=self.ReferenceClock)
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
    def PEs(self):
    
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
                        PEinNoC.updateWorkloadInfo(Thread = self.AllocationMap[PEinNoC.PEPos])
                    
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
                        PEinStruct.updateWorkloadInfo(Thread = self.AllocationMap[PEinStruct.PEPos])
        
        
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
                    
                    PEinBus.updateWorkloadInfo(Thread = self.AllocationMap[PEinBus.PEPos])

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
                    
                    PEinCrossbar.updateWorkloadInfo(Thread = self.AllocationMap[PEinCrossbar.PEPos])

                # Update square NoC X & Y indexes
                updateSquareXY()
        
        print("PEs set")
        
        return PEs
    
    
    @property
    def Injectors(self):
    
        # Injectors[PEPos] = (Injector Object)
        injectors = [None] * self.AmountOfPEs
        
        if self.AllocationMap is None:
            return injectors
        
        for PEinPlatform in self.PEs:
            injectors[PEinPlatform.PEPos] = Injector(PEPos = PEinPlatform.PEPos, Thread = self.AllocationMap[PEinPlatform.PEPos], InjectorClockFrequency = self.ReferenceClock)
        
        return injectors
    
    
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
                        wrapperAddresses[PEinStruct.PEPos] = self.BaseNoC[x][y].AddressInBaseNoC
        
        #print(str(wrapperAddresses) + "\n")
        return wrapperAddresses
        
    
    # Forces setting of PEPos values. Useful for when self.PEs getter method is never called, such as when generating Platform from JSON but not generating Injectors, but PE addresses still must be set
    def updatePEAddresses(self):

        for PEinPlatform in self.PEs:
            
            xCoord = int(PEinPlatform.AddressInBaseNoC % self.BaseNoCDimensions[0])
            yCoord = int(PEinPlatform.AddressInBaseNoC / self.BaseNoCDimensions[0])
            
            if isinstance(self.BaseNoC[xCoord][yCoord], PE):
                self.BaseNoC[xCoord][yCoord].PEPos = PEinPlatform.PEPos
                
            elif isinstance(self.BaseNoC[xCoord][yCoord], Structure):
                self.BaseNoC[xCoord][yCoord].PEs[PEinPlatform.PosInStruct].PEPos = PEinPlatform.PEPos
                
    
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

                newBaseNoC[x][y] = PE(PEPos=i, AddressInBaseNoC = i, AppID=None, ThreadID=None, InjectorClockFrequency=self.ReferenceClock)
                self.PEs[i] = newBaseNoC[x][y]

                i += 1
        
        # Adds Buses at same XY coordinates
        Buses = self.Buses
        
        for Bus in Buses:
        
            # Tuple of (X,Y) in base NoC
            XYAddr = tuple([int(Bus.AddressInBaseNoC % self.BaseNoCDimensions[0]), int(Bus.AddressInBaseNoC / self.BaseNoCDimensions[0])])
            
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
            XYAddr = tuple([int(Crossbar.AddressInBaseNoC % self.BaseNoCDimensions[0]), int(Crossbar.AddressInBaseNoC / self.BaseNoCDimensions[0])])
            
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
        NewStructure.AddressInBaseNoC = (WrapperLocationInBaseNoC[1] * self.BaseNoCDimensions[0]) + WrapperLocationInBaseNoC[0]
        
        for PEinStruct in NewStructure.PEs:
            PEinStruct.AddressInBaseNoC = (WrapperLocationInBaseNoC[1] * self.BaseNoCDimensions[0]) + WrapperLocationInBaseNoC[0]


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


    # Adds an application (containing various Thread objects) to platform
    def setWorkload(self, Workload):

        Workload.ParentPlatform = self
        self.Workload = Workload


    # Sets allocation map (Maps AppID and ThreadID to an unique PE)
    def setAllocationMap(self, AllocationMap):
    
        # AllocationMap[PEPos] = Thread object
        
        # Sets PEPos values for Threads in Workload
        for PEPos, ThreadInAllocMap in enumerate(AllocationMap):
            
            if isinstance(ThreadInAllocMap, Thread):

                # TODO: Find thread in workload wich is identical to thread in AllocMap dict and set its PEPos value
                #ThreadInAllocMap.PEPos = PEPos
                NotImplementedError

            elif isinstance(ThreadInAllocMap, str):

                if self.Workload is None:
                    print("Error: Thread lookup by ThreadName parameter is impossible if Workload hasnt been set before calling setAllocationMap()")
                    exit(1)

                ThreadInWorkload = self.Workload.getThread(ThreadName = ThreadInAllocMap)

                # DEBUG
                print(ThreadInWorkload)

                ThreadInWorkload.PEPos = PEPos
                self.AllocationMap[PEPos] = ThreadInWorkload

            elif ThreadInAllocMap is None:

                print("Warning: PEPos <" + str(PEPos) + "> has no Thread allocated")
                self.AllocationMap[PEPos] = None

            else:

                print("Error: <ThreadInAllocMap> is not a Thread object or string or None")
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

        # TODO: Check if all Threads in Workload have benn allocated (Thread.PEPos is not None)

        if self.ClusterClocks is None:
            print("Error: No ClusterClocks has been set, aborting generateJSON()")
            exit(1)

        if len(self.ClusterClocks) < self.BaseNoCDimensions[0] * self.BaseNoCDimensions[1]:
            print("Error: Platform ClusterClocks has different len <" + str(len(self.ClusterClocks)) + "> than expected <" + str(self.BaseNoCDimensions[0] * self.BaseNoCDimensions[1]) + ">")
            exit(1)

        if len(self.ClusterClocks) != self.BaseNoCDimensions[0] * self.BaseNoCDimensions[1]:
            print("Warning: Platform ClusterClocks has different len <" + str(len(self.ClusterClocks)) + "> than expected <" + str(self.BaseNoCDimensions[0] * self.BaseNoCDimensions[1]) + ">") 
            
        # Writes PE config files
        for PEinPlatform in self.PEs:
            with open(ProjectPath + "/flow/PE" + str(PEinPlatform.PEPos) + ".json", 'w') as PEFile:
                PEFile.write(PEinPlatform.toJSON())
                
        # Writes Injector config files
        for InjectorInPlatform in self.Injectors:
            with open(ProjectPath + "/flow/INJ" + str(InjectorInPlatform.PEPos) + ".json", 'w') as INJFile:
                INJFile.write(InjectorInPlatform.toJSON())
                
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
        
        # Bus info
        JSONDict["IsStandaloneBus"] = self.IsStandaloneBus
        JSONDict["AmountOfBuses"] = self.AmountOfBuses 
        JSONDict["AmountOfPEsInBuses"] = self.AmountOfPEsInBuses if self.AmountOfBuses > 0 else [-1]
        JSONDict["BusWrapperAddresses"] = self.BusWrapperAddresses if self.AmountOfBuses > 0 else [-1]
        
        BusPEIDs = dict()
        
        for i, BusInPlat in enumerate(self.Buses):
            BusPEIDs["Bus" + str(i)] = [PEinBus.PEPos for PEinBus in BusInPlat.PEs]
            
        JSONDict["BusPEIDs"] = BusPEIDs
        
        # Crossbar info
        JSONDict["IsStandaloneCrossbar"] = self.IsStandaloneCrossbar
        JSONDict["AmountOfCrossbars"] = self.AmountOfCrossbars
        JSONDict["AmountOfPEsInCrossbars"] = self.AmountOfPEsInCrossbars if self.AmountOfCrossbars > 0 else [-1]
        JSONDict["CrossbarWrapperAddresses"] = self.CrossbarWrapperAddresses if self.AmountOfCrossbars > 0 else [-1]
        
        CrossbarPEIDs = dict()
        
        for i, CrossbarInPlat in enumerate(self.Crossbars):
            CrossbarPEIDs["Crossbar" + str(i)] = [PEinCrossbar.PEPos for PEinCrossbar in CrossbarInPlat.PEs]
            
        JSONDict["CrossbarPEIDs"] = CrossbarPEIDs
        
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
        
        self.BaseNoCDimensions = tuple(JSONDict["BaseNoCDimensions"])
        #self.BaseNoC = [[None for x in range(BaseNoCDimensions[0])] for y in range(BaseNoCDimensions[1])]
        self.BaseNoC = [[None for y in range(self.BaseNoCDimensions[1])] for x in range(self.BaseNoCDimensions[0])]
        self.ReferenceClock = JSONDict["ReferenceClock"]  # In MHz
        self.StandaloneFlag = True if JSONDict["IsStandaloneBus"] or JSONDict["IsStandaloneCrossbar"] else False
        
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

                self.BaseNoC[x][y] = PE(PEPos=i, AddressInBaseNoC = i, CommStructure = "NoC", InjectorClockFrequency=self.ReferenceClock)
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
        
        