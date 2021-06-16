
import json
import math
import sys

from AppComposer import *
from Structures import *
from PE import PE

from CoordinateHelper import CoordinateHelper

class Platform:

    def __init__(self, BaseNoCDimensions = (1,1), StandaloneStruct = False, BridgeBufferSize = 4, MasterPEPos = 0, DataWidth = 32, DVFSEnable = False, DVFSServiceID = "0000FFFF", DVFSAmountOfVoltageLevels = 2, DVFSCounterResolution = 15):

        self.BaseNoCDimensions = BaseNoCDimensions
        self.StandaloneFlag = bool(StandaloneStruct)

        self.BridgeBufferSize = BridgeBufferSize
        self.DataWidth = DataWidth
        self.MasterPEPos = MasterPEPos

        self.Buses = []
        self.AmountOfBuses = 0
        self.AmountOfPEsInBuses = []
        self.BusWrapperAddresses = []
        self.IsStandaloneBus = False 
        
        self.Crossbars = []
        self.AmountOfCrossbars = 0
        self.AmountOfPEsInCrossbars = []
        self.CrossbarWrapperAddresses = []
        self.IsStandaloneCrossbar = False 
        
        # DVFS Params
        self.DVFSEnable = DVFSEnable
        self.DVFSServiceID = DVFSServiceID
        self.DVFSAmountOfVoltageLevels = DVFSAmountOfVoltageLevels
        self.DVFSCounterResolution = DVFSCounterResolution
        
        # Generate initial PE objects at every NoC address (to be replaced by a Bus/Crossbar when addStructure() is called)
        self.BaseNoC = [[PE(PEPos = y * BaseNoCDimensions[0] + x, BaseNoCPos = y * BaseNoCDimensions[1] + x, StructPos = y * BaseNoCDimensions[1] + x, CommStructure = "NoC") for y in range(BaseNoCDimensions[1])] for x in range(BaseNoCDimensions[0])]


    # Alters BaseNoC dimensions
    def resizeBaseNoC(self, NewBaseNoCDimensions, UpdateAtEnd = True):
    
        NewBaseNoC = [[self.BaseNoC[x][y] for y in range(NewBaseNoCDimensions[1])] for x in range(NewBaseNoCDimensions[0])]
        self.BaseNoC = NewBaseNoC
        self.BaseNoCDimensions = NewBaseNoCDimensions
        
        if UpdateAtEnd:
            self._update()
            

    # Adds structure (Bus or Crossbar) to base NoC
    def addStructure(self, NewStructure, BaseNoCPos, UpdateAtEnd = True):
    
        # Checks if NewStructure is a Structure object (describing either a Bus or Crossbar)
        if not isinstance(NewStructure, Structure):
            print("Error: Given NewStructure <" + str(NewStructure) + "> is not a Struct object (Bus or Crossbar)")
            exit(1)
    
        # Checks if BaseNoCPos is a 2 dimensonal tuple/list, containing XY coordinates for Bus/Crossbar to be added to Platform
        coordHelper = CoordinateHelper(BaseNoCDimensions = self.BaseNoCDimensions, SquareNoCBound = SquareNoCBound)
        if isinstance(BaseNoCPos, int):
            BaseNoCPos = coordHelper.sequentialToXY()
        elif len(tuple(BaseNoCPos)) != 2:
            print("Error: Unexpected BaseNoCPos <" + str(BaseNoCPos) + "> (must be a tuple/list of length = 2: (XSize, YSize))")
            exit(1)
        
        # Checks if given XY coordinates for new Bus/Crossbar exist in base NoC
        try:
            self.BaseNoC[BaseNoCPos[0]][BaseNoCPos[1]]

        # Given XY coordinates for new Bus/Crossbar dont exist in base NoC
        except IndexError or KeyError: 
            print("Error: Given XY coordinates <" + str(BaseNoCPos) + "> for new Bus/Crossbar dont exist in base NoC (Base NoC dimensions: " + str(self.BaseNoCDimensions) + ")")
            exit(1)
            
        # Checks for a Bus/Crossbar at given location in base NoC
        if isinstance(self.BaseNoC[BaseNoCPos[0]][BaseNoCPos[1]], Structure):

            # There already is a Bus/Crossbar at this position in base NoC
            print("Error: There already is a " + str(self.BaseNoC[BaseNoCPos[0]][BaseNoCPos[1]].StructureType) + " at given location <" + str(BaseNoCPos) + ">")
            exit(1)    
        
        # Inserts given structure into base NoC
        if str(NewStructure.StructureType).casefold() == "bus":
            self.Buses.append(NewStructure)
            #print("Added Bus containing " + str(NewStructure.AmountOfPEs) + " elements @ base NoC " + str(BaseNoCPos))

        elif str(NewStructure.StructureType).casefold() == "crossbar":
            self.Crossbars.append(NewStructure)
            #print("Added Crossbar containing " + str(NewStructure.AmountOfPEs) + " elements @ base NoC " + str(BaseNoCPos))
            
        else:
            print("Error: Given StructureType <" + str(NewStructure.StructureType) + "> not recognized")
            exit(1)

        self.BaseNoC[BaseNoCPos[0]][BaseNoCPos[1]] = NewStructure
        NewStructure.BaseNoCPos = (BaseNoCPos[1] * self.BaseNoCDimensions[0]) + BaseNoCPos[0]
        
        for PEinStruct in NewStructure.PEs:
            PEinStruct.BaseNoCPos = (BaseNoCPos[1] * self.BaseNoCDimensions[0]) + BaseNoCPos[0]

        print("Added new " + str(NewStructure.StructureType) + " to base NoC location <" + str(BaseNoCPos) + ">")

        if UpdateAtEnd:
            self._update()
            

    # Removes a given Bus/Crossbar (either as a Structure object <StructToRemove> or XY coordinates in base NoC <BaseNoCPos>) from Platform
    def removeStructure(self, StructToRemove = None, BaseNoCPos = None, UpdateAtEnd = True):
    
        # Checks if both StructToRemove and BaseNoCPos are None
        if StructToRemove is None and BaseNoCPos is None:
        
            print("Warning: Both <StructToRemove> and <BaseNoCPos> given arguments are None. removeStructure() will do nothing")
            return None
            
        # 
        elif StructToRemove is not None and BaseNoCPos is None:
        
            # Checks if StructToRemove is a Structure object, describing either a Bus or Crossbar
            if not isinstance(StructToRemove, Structure):
            
                print("Error: Given StructToRemove <" + str(StructToRemove) + "> is not a Structure object (describing either a Bus or Crossbar)")
                exit(1)
    
            # Checks if StructToRemove is a Bus
            if isinstance(StructToRemove, Bus):
            
                # Removes StructToRemove from Bus list
                try:
                    BusOfInterest = Buses.remove(StructToRemove)
                except ValueError:
                    print("Warning: Bus <" + str(StructToRemove) + "> doesnt exist in this Platform")
                    return None
                    
                # Replace Bus with a PE
                x, y = CoordinateHelper.sequentialToXY(BusOfInterest.BaseNoCPos)
                self.BaseNoC[x][y] = PE(PEPos = -1, BaseNoCPos = -1, StructPos = -1, CommStructure = "NoC")  # Dummy values, will be replaced inside self._update()
                
                return BusOfInterest
            
            # Checks if StructToRemove is a Crossbar
            elif isinstance(StructToRemove, Crossbar):
            
                # Removes StructToRemove from Crossbar list
                try:
                    CrossbarOfInterest = Crossbars.remove(StructToRemove)
                except ValueError:
                    print("Warning: Crossbar <" + str(StructToRemove) + "> doesnt exist in this Platform")
                    return None
                    
                # Replace Crossbar with a PE    
                x, y = CoordinateHelper.sequentialToXY(CrossbarOfInterest.BaseNoCPos)
                self.BaseNoC[x][y] = PE(PEPos = -1, BaseNoCPos = -1, StructPos = -1, CommStructure = "NoC")  # Dummy values, will be replaced inside self._update()
                
                return CrossbarOfInterest
                    
            else:
                print("Error: Given Structure is of a different kind than Bus or Crossbar")
                exit(1)
        
        elif StructToRemove is None and BaseNoCPos is not None:
        
            # Checks if BaseNoCPos is a 2 dimensonal tuple/list, containing updated XY coordinates for base NoC
            coordHelper = CoordinateHelper(BaseNoCDimensions = self.BaseNoCDimensions, SquareNoCBound = SquareNoCBound)
            if isinstance(BaseNoCPos, int):
                BaseNoCPos = coordHelper.sequentialToXY()
            if len(tuple(BaseNoCPos)) != 2:
                print("Error: Unexpected BaseNoCPos <" + str(BaseNoCPos) + "> (must be a tuple/list of length = 2: (XSize, YSize))")
                exit(1)
            
            try:
                Struct = self.BaseNoC[BaseNoCPos[0]][BaseNoCPos[1]]
                
            except IndexError or KeyError:
                print("Error: Given BaseNoCPos <" + str(BaseNoCPos) + "> doesnt not correspond to a valid XY coordinate in base NoC (Base NoC dimensions = " + str(self.BaseNoCDimensions) + ")")
                exit(1)
                
            else:
                return self.removeStructure(StructToRemove = Struct)
        
        elif StructToRemove is not None and BaseNoCPos is not None:
        
            try: 
                StructInBaseNoC = self.BaseNoC[BaseNoCPos[0]][BaseNoCPos[1]]
            
            except IndexError or KeyError: 
                print("Error: Given BaseNoCPos <" + str(BaseNoCPos) + "> doesnt not correspond to a valid XY coordinate in base NoC (Base NoC dimensions = " + str(self.BaseNoCDimensions) + ")")
                exit(1)
                
            if StructInBaseNoC is StructToRemove:
                return self.removeStructure(StructToRemove = StructInBaseNoC)
                
            else:
                print("Warning: Given StructInBaseNoC <" + str(StructToRemove) + "> and BaseNoCPos <" + str(BaseNoCPos) + "> correspond to different Structure objects. removeStructure() will do nothing")
                return None
        
        if UpdateAtEnd:
            self._update()
            

    def toJSON(self, SaveToFile = False, FileName = None):

        # A "hand-built" dict is required because self.__dict__ doesnt have @property decorator keys (self.AmountOfPEs, etc)
        JSONDict = dict()
        
        # General Info
        JSONDict["AmountOfPEs"] = self.AmountOfPEs
        JSONDict["AmountOfWrappers"] = self.AmountOfWrappers
        JSONDict["BaseNoCDimensions"] = self.BaseNoCDimensions
        JSONDict["SquareNoCBound"] = self.SquareNoCBound
        #JSONDict["StandaloneFlag"] = self.StandaloneFlag
        #JSONDict["WrapperAddresses"] = [self.WrapperAddresses[PEPos] for PEPos in self.WrapperAddresses.keys()]  #  Dict -> List
        JSONDict["WrapperAddresses"] = self.WrapperAddresses
        JSONDict["BridgeBufferSize"] = self.BridgeBufferSize
        JSONDict["MasterPEPos"] = self.MasterPEPos
        JSONDict["DataWidth"] = self.DataWidth
        
        # DVFS params
        JSONDict["DVFSEnable"] = self.DVFSEnable
        JSONDict["DVFSServiceID"] = self.DVFSServiceID
        JSONDict["DVFSAmountOfVoltageLevels"] = self.DVFSAmountOfVoltageLevels
        JSONDict["DVFSCounterResolution"] = self.DVFSCounterResolution

        # Bus info
        JSONDict["IsStandaloneBus"] = self.IsStandaloneBus
        JSONDict["AmountOfBuses"] = self.AmountOfBuses
        JSONDict["LargestBus"] = 0  # Default value, will be replaced below if there are any Busses
        
        if self.AmountOfBuses > 0:

            JSONDict["AmountOfPEsInBuses"] = self.AmountOfPEsInBuses
            JSONDict["BusWrapperAddresses"] = self.BusWrapperAddresses
            
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
        JSONDict["LargestCrossbar"] = 0  # Default value, will be replaced below if there are any Crossbars

        if self.AmountOfCrossbars > 0:

            JSONDict["AmountOfPEsInCrossbars"] = self.AmountOfPEsInCrossbars 
            JSONDict["CrossbarWrapperAddresses"] = self.CrossbarWrapperAddresses
            
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
        
        self.BaseNoCDimensions = tuple(JSONDict["BaseNoCDimensions"])
        #self.BaseNoC = [[None for y in range(self.BaseNoCDimensions[1])] for x in range(self.BaseNoCDimensions[0])]
        self.BaseNoC = [[PE(PEPos = y * BaseNoCDimensions[0] + x, BaseNoCPos = y * BaseNoCDimensions[1] + x, StructPos = y * BaseNoCDimensions[1] + x, CommStructure = "NoC") for y in range(BaseNoCDimensions[1])] for x in range(BaseNoCDimensions[0])]
        
        self.StandaloneFlag = True if JSONDict["IsStandaloneBus"] or JSONDict["IsStandaloneCrossbar"] else False
        self.BridgeBufferSize = JSONDict["BridgeBufferSize"]        
        self.MasterPEPos = JSONDict["MasterPEPos"]        
        self.DataWidth = JSONDict["DataWidth"]        
        
        # DVFS params
        self.DVFSEnable = JSONDict["DVFSEnable"]
        self.DVFSServiceID = JSONDict["DVFSServiceID"]
        self.DVFSAmountOfVoltageLevels = JSONDict["DVFSAmountOfVoltageLevels"]
        self.DVFSCounterResolution = JSONDict["DVFSCounterResolution"]
        
        # Add Buses to Platform
        if JSONDict["AmountOfBuses"] > 0:

            for i, BusSize in enumerate(JSONDict["AmountOfPEsInBuses"]):

                #BaseNoCPos = (int(JSONDict["BusWrapperAddresses"][i] % self.BaseNoCDimensions[0]), int(JSONDict["BusWrapperAddresses"][i] / self.BaseNoCDimensions[0]))
                BaseNoCPos = int(JSONDict["BusWrapperAddresses"][i])
                self.addStructure(NewStructure = Bus(AmountOfPEs = BusSize), BaseNoCPos = BaseNoCPos, UpdateAtEnd = False)

        # Add Crossbars to Platform
        if JSONDict["AmountOfCrossbars"] > 0:

            for i, CrossbarSize in enumerate(JSONDict["AmountOfPEsInCrossbars"]):

                #BaseNoCPos = (int(JSONDict["CrossbarWrapperAddresses"][i] % self.BaseNoCDimensions[0]), int(JSONDict["CrossbarWrapperAddresses"][i] / self.BaseNoCDimensions[0]))
                BaseNoCPos = int(JSONDict["CrossbarWrapperAddresses"][i])
                self.addStructure(NewStructure = Crossbar(AmountOfPEs = CrossbarSize), BaseNoCPos = BaseNoCPos, UpdateAtEnd = False)

        self._update()

        return self
        
        
    # Loops through whole base NoC and update all parameters (called when adding or removing a struct from base NoC)
    def _update(self):
    
        self.AmountOfPEs = 0
        self.AmountOfWrappers = 0
        
        self.Buses = []
        self.AmountOfBuses = 0
        self.AmountOfPEsInBuses = []
        self.BusWrapperAddresses = []
        self.IsStandaloneBus = True if isinstance(self.BaseNoC[0][0], Bus) and self.BaseNoCDimensions == (1,1) else False 
        
        self.Crossbars = []
        self.AmountOfCrossbars = 0
        self.AmountOfPEsInCrossbars = []
        self.CrossbarWrapperAddresses = []
        self.IsStandaloneCrossbar = True if isinstance(self.BaseNoC[0][0], Crossbar) and self.BaseNoCDimensions == (1,1) else False 
    
        # Finds total amount of PEs, and struct-related parameters
        for y in self.BaseNoCDimensions[1]:
            for x in self.BaseNoCDimensions[0]:
            
                if isinstance(self.BaseNoC[x][y], PE):
                    self.AmountOfPEs += 1
                    
                elif isinstance(self.BaseNoC[x][y], Structure):
                
                    self.AmountOfPEs += self.BaseNoC[x][y].AmountOfPEs
                    self.AmountOfWrappers += 1
                    
                    if isinstance(self.BaseNoC[x][y], Bus):
                        
                        self.Buses.append(self.BaseNoC[x][y])
                        self.AmountOfBuses += 1
                        self.AmountOfPEsInBuses.append(self.BaseNoC[x][y].AmountOfPEs)
                        self.BusWrapperAddresses.append(CoordinateHelper.XYToSequential(x = x, y = y, xMax = self.BaseNoCDimensions[0]))
             
                    elif isinstance(self.BaseNoC[x][y], Crossbar):
                    
                        self.Crossbars.append(self.BaseNoC[x][y])
                        self.AmountOfCrossbars += 1
                        self.AmountOfPEsInCrossbars.append(self.BaseNoC[x][y].AmountOfPEs)
                        self.CrossbarWrapperAddresses.append(CoordinateHelper.XYToSequential(x = x, y = y, xMax = self.BaseNoCDimensions[0]))
        
        # Set SquareNoCBound for square NoC addressing algorithm
        squareNoCBound = int(math.ceil(math.sqrt(self.AmountOfPEs)))
        if self.BaseNoCDimensions[0] > squareNoCBound:
            self.SquareNoCBound = self.BaseNoCDimensions[0]
            
        elif self.BaseNoCDimensions[1] > squareNoCBound:
            self.SquareNoCBound = self.BaseNoCDimensions[1]
        
        else:
            self.SquareNoCBound = squareNoCBound   
            
        # Get stack of XY coordinates from square NoC algorithm from coordHelper
        coordHelper = CoordinateHelper(BaseNoCDimensions = self.BaseNoCDimensions, SquareNoCBound = self.SquareNoCBound)
           
        self.PEs = [None for PE in self.AmountOfPEs]
        self.WrapperAddresses = [None for PE in self.AmountOfPEs]
        
        # Update PEPos values for base NoC and first-of-struct PEs
        for y in self.BaseNoCDimensions[1]:
            for x in self.BaseNoCDimensions[0]:
                
                if isinstance(self.BaseNoC[x][y], PE):
                
                    PEPos = coordHelper.XYToSequential(x = x, y = y, xMax = self.SquareNoCBound)
                    BaseNoCPos = coordHelper.XYToSequential(x = x, y = y, xMax = self.BaseNoCDimensions[0])
                    
                    self.BaseNoC[x][y].PEPos = PEPos
                    
                    self.WrapperAddresses[PEPos] = BaseNoCPos
                    self.PEs[PEPos] = self.BaseNoC[x][y]
                    
                elif isinstance(self.BaseNoC[x][y], Structure):
                
                    PEPos = coordHelper.XYToSequential(x = x, y = y, xMax = self.SquareNoCBound)
                    BaseNoCPos = coordHelper.XYToSequential(x = x, y = y, xMax = self.BaseNoCDimensions[0])
                    
                    self.BaseNoC[x][y].PEs[0].PEPos = PEPos
                    
                    self.PEs[PEPos] = self.BaseNoC[x][y]
                    self.WrapperAddresses[PEPos] = BaseNoCPos
                
        # Update PEPos values for Bus
        for y in self.BaseNoCDimensions[1]:
            for x in self.BaseNoCDimensions[0]:
                if isinstance(self.BaseNoC[x][y], Bus):
                    for PE in self.BaseNoC[x][y].PEs[1:]:
                    
                        PEPos = coordHelper.popPEPos()
                        BaseNoCPos = coordHelper.XYToSequential(x = x, y = y, xMax = self.BaseNoCDimensions[0])
                        
                        PE.PEPos = PEPos
                        
                        self.PEs[PEPos] = self.BaseNoC[x][y]
                        self.WrapperAddresses[PEPos] = BaseNoCPos
        
        # Update PEPos values for Crossbar
        for y in self.BaseNoCDimensions[1]:
            for x in self.BaseNoCDimensions[0]:
                if isinstance(self.BaseNoC[x][y], Crossbar):
                    for PE in self.BaseNoC[x][y].PEs[1:]:
                    
                        PEPos = coordHelper.popPEPos()
                        BaseNoCPos = coordHelper.XYToSequential(x = x, y = y, xMax = self.BaseNoCDimensions[0])
                        
                        PE.PEPos = PEPos
                        
                        self.PEs[PEPos] = self.BaseNoC[x][y]
                        self.WrapperAddresses[PEPos] = BaseNoCPos
                        
        # Makes sure no default values are left
        for PEPos, PE in self.PEs:
            if PE is None:
                print("Error: Something went wrong in making PEs list, PEPos <" + str(PEPos) + "> is set as None")
                exit(1)
                
        for PEPos, PE in self.WrapperAddresses:
            if PE is None:
                print("Error: Something went wrong in making WrapperAddresses list, PEPos <" + str(PEPos) + "> is set as None")
                exit(1)
    
    
    # TODO: Print out info for debug
    def __str__(self):
    
        returnString = ""
        
        returnString += "Amount of PEs: " + str(self.AmountOfPEs) + "\n"
        returnString += "Base NoC Dimensions: " + str(self.BaseNoCDimensions) + "\n"
        #returnString += "ReferenceClock: " + str(self.ReferenceClock) + " MHz \n"
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
        
        
