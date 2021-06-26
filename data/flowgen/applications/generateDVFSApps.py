import math
import AppComposer
import PlatformComposer
from fractions import Fraction

# This script generate DVFS AppComposer Applications for a given network topology and router-grained previously computed clock frequencies.
def generateDVFSApps(Platform, PlatformName, RouterClockFrequencies, BusClockFrequencies, CrossbarClockFrequencies, GenRouterGrained = True, GenStructGrained = True, GenGlobalGrained = True, GenStaticClocked = False, GenNoDVFS = True, DataWidth = 32, InputClockFrequency = 250, QuantumTime = 1000000, SaveToFile = True, ReturnAsJSON = False):
        
    if not isinstance(Platform, PlatformComposer.Platform):
        print("Error: Object given as Platform parameter is not of PlatformComposer.Platform class")
        exit(1)
        
    # Sets up return dict, containing all Application generated by this script
    AppDict = {"RouterGrained": None, "StructGrained": None, "GlobalGrained": None, "StaticClocked": None, "NoDVFS": None}
        
    # TODO: Check if not standalone struct
    
    # Extract base parameters from given Platform object. 
    AmountOfRouters = Platform.BaseNoCDimensions[0] * Platform.BaseNoCDimensions[1]
    AmountOfBuses = Platform.AmountOfBuses
    AmountOfCrossbars = Platform.AmountOfCrossbars
    AmountOfPEs = Platform.AmountOfPEs
    DVFSServiceID = Platform.DVFSServiceID  # 32 bit constant as hex
    DVFSCounterResolution = Platform.DVFSCounterResolution 
    DVFSAmountOfVoltageLevels = Platform.DVFSAmountOfVoltageLevels 
    MasterPEPos = Platform.MasterPEPos
    # TODO: Do search for BusID/CrossbarID of first PEPos in struct here
    
	# Info flit fields (field bit width below):
	# |        Voltage Level        | IsNoC | ... |         N         |         M         |
	#   log2(AmountOfVoltageLevels)     1           CounterResolution   CounterResolution
    VoltageLevelFieldSize = math.ceil(math.log2(DVFSAmountOfVoltageLevels))
    ZeroPadding = "0" * (DataWidth - VoltageLevelFieldSize - 1 - 2*DVFSCounterResolution)

    if DVFSAmountOfVoltageLevels != 2:
        print("Error: This scripts only supports a DVFS voltage level amount of 2, called with <" + str(DVFSAmountOfVoltageLevels) + ">")  
        exit(1)
    
    # Check if amount of Quantums is coherent for each clock frequency list
    if BusClockFrequencies is not None:

        if len(RouterClockFrequencies) == len(BusClockFrequencies):
            AmountOfQuantums = len(RouterClockFrequencies)
        else:
            print("Error: Incoherent amount of quantums: Per Router <" + str(len(RouterClockFrequencies)) + "> Per Bus <" + str(len(BusClockFrequencies))+ ">")
            exit(1)

    if CrossbarClockFrequencies is not None:

        if len(RouterClockFrequencies) == len(CrossbarClockFrequencies):
            AmountOfQuantums = len(RouterClockFrequencies)
        else:
            print("Error: Incoherent amount of quantums: Per Router <" + str(len(RouterClockFrequencies))+ "> Per Crossbar <" + str(len(CrossbarClockFrequencies)) + ">")
            exit(1)
    
    AmountOfQuantums = len(RouterClockFrequencies)
        
    # Check if amount of routers or PEs in Bus/Crossbars are coherent with info from Platform object
    for i, ClocksInQuantum in enumerate(RouterClockFrequencies):
        if len(ClocksInQuantum) != AmountOfRouters:
            print("Error: Amount of Routers <" + str(len(ClocksInQuantum)) + "> for Quantum <" + str(i) + "> differs from amount of Routers from Platform object <" + str(AmountOfRouters) + ">")
            exit(1)
            
    if BusClockFrequencies is not None: 
        for i, ClocksInQuantum in enumerate(BusClockFrequencies):
            if len(ClocksInQuantum) != AmountOfBuses:
                print("Error: Amount of Buses <" + str(len(ClocksInQuantum)) + "> for Quantum <" + str(i) + "> differs from amount of Buses from Platform object <" + str(AmountOfBuses) + ">")
                exit(1)

    if CrossbarClockFrequencies is not None:            
        for i, ClocksInQuantum in enumerate(CrossbarClockFrequencies):
            if len(ClocksInQuantum) != AmountOfCrossbars:
                print("Error: Amount of Crossbars <" + str(len(ClocksInQuantum)) + "> for Quantum <" + str(i) + "> differs from amount of Crossbars from Platform object <" + str(AmountOfCrossbars) + ">")
                exit(1)

    if GenRouterGrained:

        print("\nMaking Router-grained DVFS Application")
    
        # Make Application
        DVFSApp = AppComposer.Application(AppName = "DVFSApp", StartTime = 0, StopTime = 0)

        # Make Threads
        DVFSSink = AppComposer.Thread(ThreadName = "Sink")
        DVFSSources = [AppComposer.Thread(ThreadName = "Source" + str(i)) for i in range(0, AmountOfPEs)]

        # Add Threads to DVFS Application
        DVFSApp.addThread(DVFSSink)
        for DVFSSource in DVFSSources:
            DVFSApp.addThread(DVFSSource)
        
        # Determine VF-pair setup for each Router/Bus/Crossbar in each time window (quantum)
        for Quantum in range(AmountOfQuantums):
            for PEPos, PE in enumerate(Platform.PEs):
            
                # Only NoC and first-of-struct PEs are needed (no DVFS for PEs inside Bus/Crossbar)
                if PE.CommStructure != "NoC" and PE.StructPos != 0:
                    continue
                
                # Skip Master PE, since a PE cant send a message to itself
                if PEPos == MasterPEPos:
                    continue

                # Determines N and M (numerator and denominator) on config flit
                if PE.CommStructure == "NoC":
                
                    TargetFrequency = RouterClockFrequencies[Quantum][PE.BaseNoCPos]
                    DivRatio = Fraction(TargetFrequency / InputClockFrequency).limit_denominator((2**DVFSCounterResolution) - 1)
                    
                elif PE.CommStructure == "Bus":
                
                    # Finds which Bus this PE is in
                    BusID = None
                    for i, Bus in enumerate(Platform.Buses):
                        if Bus.PEs[0].PEPos == PEPos:
                            BusID = i
                            break
 
                    try:
                        TargetFrequency = BusClockFrequencies[Quantum][BusID]
                        DivRatio = Fraction(TargetFrequency / InputClockFrequency).limit_denominator((2**DVFSCounterResolution) - 1)
                    except TypeError:
                        print("Error: Cant find a BusID for PEPos <" + str(PEPos) + ">")
                        exit(1)
                        
                elif PE.CommStructure == "Crossbar":
                    
                    # Finds which Crossbar this PE is in    
                    CrossbarID = None    
                    for i, Crossbar in enumerate(Platform.Crossbars):
                        if Crossbar.PEs[0].PEPos == PEPos:
                            CrossbarID = i
                            break

                    try:
                        TargetFrequency = CrossbarClockFrequencies[Quantum][CrossbarID]
                        DivRatio = Fraction(TargetFrequency / InputClockFrequency).limit_denominator((2**DVFSCounterResolution) - 1)
                    except TypeError:
                        print("Error: Cant find a CrossbarID for PEPos <" + str(PEPos) + ">")
                        exit(1)
                        
                else:
                    print("Error: Invalid CommStructure value <" + str(PE.CommStructure) + "> for PE <" + str(PEPos) + ">. Acceptable values are [NoC, Bus, Crossbar].")
                    exit(1)
                
                # Checks if TargetFrequency < Input Frequency
                if TargetFrequency > InputClockFrequency:
                    print("Error: Target frequency <" + str(TargetFrequency) + " MHz> greater than input frequency <" + str(InputClockFrequency) + " MHz> for PEPos <" + str(PEPos) + "> Quantum <" + str(Quantum) + ">")  
                    exit(1)              

                # Ensures N/M fractional representation is rounded up
                if DivRatio * InputClockFrequency < TargetFrequency and DivRatio.numerator != 0:
                    print("Warning: Rounding computed N/M frequency of <" + str((DivRatio.numerator)/(DivRatio.denominator) * InputClockFrequency) + " MHz> up to <" + str((DivRatio.numerator + 1)/(DivRatio.denominator) * InputClockFrequency) + "MHz> for PE <" + str(PEPos) + ">, Quantum <" + str(Quantum) + ">.  Original frequency: " + str(TargetFrequency) + " MHz")
                    #DivRatio.numerator += 1  # Fraction.numerator is a @property method and cant be set directly
                    DivRatio = Fraction(numerator = DivRatio.numerator + 1, denominator = DivRatio.denominator)

                # Sets to minimum frequency if computed frequency = 0
                if DivRatio.numerator == 0:
                    print("Warning: Setting computed N/M frequency of 0 MHz to <" + str((1/((2**DVFSCounterResolution) - 1)) * InputClockFrequency) + " MHz> for PE <" + str(PEPos) + ">, Quantum <" + str(Quantum) + ">. Original frequency: " + str(TargetFrequency) + " MHz")
                    DivRatio = Fraction(numerator = 1, denominator = (2**DVFSCounterResolution) - 1)

                # Determines power switch enable signal on config flit
                SupplySwitchBit = '1' if DivRatio > Fraction(1, 2) else '0' 
                    
                # Determine IsNoC bit on config flit
                IsNoCBit = '1' if PE.CommStructure == "NoC" else '0'
                    
                # Determines config flit for DVFS Payload
                # Info flit fields (field bit width below):
                # |        Voltage Level        | IsNoC | ... |         N         |         M         |
                #   log2(AmountOfVoltageLevels)     1           CounterResolution   CounterResolution
                ConfigFlit = SupplySwitchBit + IsNoCBit + ZeroPadding + format(DivRatio.numerator, "0" + str(DVFSCounterResolution) + "b") + format(DivRatio.denominator, "0" + str(DVFSCounterResolution) + "b")
                ConfigFlit = '%0*X' % ((len(ConfigFlit) + 3) // 4, int(ConfigFlit, 2))  # Converts bit string to hex string "https://stackoverflow.com/questions/2072351/python-conversion-from-binary-string-to-hexadecimal"

                # DEBUG
                #print("PEPos: " + str(PEPos) + " Quantum: " + str(Quantum))
                #print("Ratio: " + str(DivRatio.numerator) + " by " + str(DivRatio.denominator))
                #print("N as binary: " + format(DivRatio.numerator, "0" + str(DVFSCounterResolution) + "b"))
                #print("M as binary: " + format(DivRatio.denominator, "0" + str(DVFSCounterResolution) + "b"))
                #print("N: " + str(DivRatio.numerator) + " M: " + str(DivRatio.denominator))
                #print("Target Frequency: " + str(TargetFrequency) + " Actual Frequency: " + str((DivRatio.numerator / DivRatio.denominator) * InputClockFrequency))           
                    
                # Adds Flow with custom Payload to master DVFS Thread
                #DVFSMaster.addFlow(AppComposer.CBRFlow(TargetThread = DVFSSources[PEPos], Bandwidth = 1000, StartTime = Quantum * QuantumTime, MSGAmount = 1, Payload = [DVFSServiceID, ConfigFlit]))
                DVFSSources[PEPos].addFlow(AppComposer.CBRFlow(TargetThread = DVFSSink, Bandwidth = 1000, StartTime = Quantum * QuantumTime, MSGAmount = 1, Payload = [DVFSServiceID, ConfigFlit]))
        
        # Add DVFS to AppDict
        if ReturnAsJSON:
            AppDict["RouterGrained"] = DVFSApp.toJSON() 
        else:
            AppDict["RouterGrained"] = DVFSApp
                    
        # Write Router-grained DVFS Application to a JSON file
        DVFSApp.toJSON(SaveToFile = True, FileName = PlatformName + "/DVFSAppRouterGrained" + str(PlatformName) + "Resolution" + str(DVFSCounterResolution))

    # Generates Struct-grained DVFS App (Whole NoC + All Buses + All Crossbars). Skipped if standalone NoC (no Bus/Crossbars)    
    if GenStructGrained and (AmountOfCrossbars > 0 or AmountOfBuses > 0):
        
        print("\nMaking Struct-grained DVFS Application")

        # Make Application
        if SaveToFile:
            DVFSApp = AppComposer.Application(AppName = "DVFSApp", StartTime = 0, StopTime = 0)

        # Make Threads
        DVFSSink = AppComposer.Thread(ThreadName = "Sink")
        DVFSSources = [AppComposer.Thread(ThreadName = "Source" + str(i)) for i in range(0, AmountOfPEs)]

        # Add Threads to DVFS Application
        DVFSApp.addThread(DVFSSink)
        for DVFSSource in DVFSSources:
            DVFSApp.addThread(DVFSSource)
        
        # Determine VF-pair setup for each Router/Bus/Crossbar in each time window (quantum)
        for Quantum in range(AmountOfQuantums):
            for PEPos, PE in enumerate(Platform.PEs):
            
                # Only NoC and first-of-struct PEs are needed (no DVFS for PEs inside Bus/Crossbar)
                if PE.CommStructure != "NoC" and PE.StructPos != 0:
                    continue
                
                # Skip Master PE, since a PE cant send a message to itself
                if PEPos == MasterPEPos:
                    continue

                # Determines N and M (numerator and denominator) on config flit
                if PE.CommStructure == "NoC":
                
                    # Max Router clock defines all other Routers'
                    DivRatio = Fraction(max(RouterClockFrequencies[Quantum]) / InputClockFrequency).limit_denominator((2**DVFSCounterResolution) - 1)
                    
                elif PE.CommStructure == "Bus":
                
                    BusID = None
                    
                    # Finds which Bus this PE is in
                    for i, Bus in enumerate(Platform.Buses):
                        if Bus.PEs[0].PEPos == PEPos:
                            BusID = i
                            
                    try:
                        DivRatio = Fraction(BusClockFrequencies[Quantum][BusID] / InputClockFrequency).limit_denominator((2**DVFSCounterResolution) - 1)
                    except TypeError:
                        print("Error: Cant find a BusID for PEPos <" + str(PEPos) + ">")
                        exit(1)
                        
                elif PE.CommStructure == "Crossbar":
                    
                    CrossbarID = None
                            
                    # Finds which Crossbar this PE is in        
                    for i, Crossbar in enumerate(Platform.Crossbars):
                        if Crossbar.PEs[0].PEPos == PEPos:
                            CrossbarID = i
                            
                    try:
                        DivRatio = Fraction(CrossbarClockFrequencies[Quantum][CrossbarID] / InputClockFrequency).limit_denominator((2**DVFSCounterResolution) - 1)
                    except TypeError:
                        print("Error: Cant find a BusID for PEPos <" + str(PEPos) + ">")
                        exit(1)
                        
                else:
                    print("Error: Invalid CommStructure value <" + str(PE.CommStructure) + "> for PE <" + str(PEPos) + ">. Acceptable values are [NoC, Bus, Crossbar].")

                # Checks if TargetFrequency < Input Frequency
                if TargetFrequency > InputClockFrequency:
                    print("Error: Target frequency <" + str(TargetFrequency) + " MHz> greater than input frequency <" + str(InputClockFrequency) + " MHz> for PEPos <" + str(PEPos) + "> Quantum <" + str(Quantum) + ">")  
                    exit(1)              

                # Ensures N/M fractional representation is rounded up
                if DivRatio * InputClockFrequency < TargetFrequency and DivRatio.numerator != 0:
                    print("Warning: Rounding computed N/M frequency of <" + str((DivRatio.numerator)/(DivRatio.denominator) * InputClockFrequency) + " MHz> up to <" + str((DivRatio.numerator + 1)/(DivRatio.denominator) * InputClockFrequency) + "MHz> for PE <" + str(PEPos) + ">, Quantum <" + str(Quantum) + ">.  Original frequency: " + str(TargetFrequency) + " MHz")
                    #DivRatio.numerator += 1  # Fraction.numerator is a @property method and cant be set directlyy
                    DivRatio = Fraction(numerator = DivRatio.numerator + 1, denominator = DivRatio.denominator)

                # Sets to minimum frequency if computed frequency = 0
                if DivRatio.numerator == 0:
                    print("Warning: Setting computed N/M frequency of 0 MHz to <" + str((1/((2**DVFSCounterResolution) - 1)) * InputClockFrequency) + " MHz> for PE <" + str(PEPos) + ">, Quantum <" + str(Quantum) + ">. Original frequency: " + str(TargetFrequency) + " MHz")
                    DivRatio = Fraction(numerator = 1, denominator = (2**DVFSCounterResolution) - 1)

                # Determines power switch enable signal on config flit
                SupplySwitchBit = '1' if DivRatio > Fraction(1, 2) else '0' 
                    
                # Determine IsNoC bit on config flit
                IsNoCBit = '1' if PE.CommStructure == "NoC" else '0'
                    
                # Determines config flit for DVFS Payload
                # Info flit fields (field bit width below):
                # |        Voltage Level        | IsNoC | ... |         N         |         M         |
                #   log2(AmountOfVoltageLevels)     1           CounterResolution   CounterResolution
                ConfigFlit = SupplySwitchBit + IsNoCBit + ZeroPadding + format(DivRatio.numerator, "0" + str(DVFSCounterResolution) + "b") + format(DivRatio.denominator, "0" + str(DVFSCounterResolution) + "b")
                ConfigFlit = '%0*X' % ((len(ConfigFlit) + 3) // 4, int(ConfigFlit, 2))  # Converts bit string to hex string "https://stackoverflow.com/questions/2072351/python-conversion-from-binary-string-to-hexadecimal"
                    
                # Adds Flow with custom Payload to master DVFS Thread
                #DVFSMaster.addFlow(AppComposer.CBRFlow(TargetThread = DVFSSources[PEPos], Bandwidth = 1000, StartTime = Quantum * QuantumTime, MSGAmount = 1, Payload = [DVFSServiceID, ConfigFlit]))
                DVFSSources[PEPos].addFlow(AppComposer.CBRFlow(TargetThread = DVFSSink, Bandwidth = 1000, StartTime = Quantum * QuantumTime, MSGAmount = 1, Payload = [DVFSServiceID, ConfigFlit]))
                
        # Add DVFS to AppDict
        if ReturnAsJSON:
            AppDict["StructGrained"] = DVFSApp.toJSON() 
        else:
            AppDict["StructGrained"] = DVFSApp
            
        # Write struct-grained DVFS Application to a JSON file
        if SaveToFile:
            DVFSApp.toJSON(SaveToFile = True, FileName = PlatformName + "/DVFSAppStructGrained" + str(PlatformName) + "Resolution" + str(DVFSCounterResolution))
        
    #   
    if GenGlobalGrained:
        
        print("\nMaking Global-grained DVFS Application")

        # Make Application
        DVFSApp = AppComposer.Application(AppName = "DVFSApp", StartTime = 0, StopTime = 0)

        # Make Threads
        DVFSSink = AppComposer.Thread(ThreadName = "Sink")
        DVFSSources = [AppComposer.Thread(ThreadName = "Source" + str(i)) for i in range(0, AmountOfPEs)]

        # Add Threads to DVFS Application
        DVFSApp.addThread(DVFSSink)
        for DVFSSource in DVFSSources:
            DVFSApp.addThread(DVFSSource)
        
        # Determine VF-pair setup for each Router/Bus/Crossbar in each time window (quantum)
        for Quantum in range(AmountOfQuantums):
            for PEPos, PE in enumerate(Platform.PEs):
            
                # Only NoC and first-of-struct PEs are needed (no DVFS for PEs inside Bus/Crossbar)
                if PE.CommStructure != "NoC" and PE.StructPos != 0:
                    continue
                
                # Skip Master PE, since a PE cant send a message to itself
                if PEPos == MasterPEPos:
                    continue

                # Determines N and M (numerator and denominator) on config flit
                NoCMaxFreq = max(RouterClockFrequencies[Quantum])
                try:
                    BusMaxFreq = max(BusClockFrequencies[Quantum])
                except (ValueError, TypeError):  # BusClockFrequencies is an empty list (ValueError) or None (TypeError)
                    BusMaxFreq = 0
                
                try:
                    CrossbarMaxFreq = max(CrossbarClockFrequencies[Quantum])
                except (ValueError, TypeError):  # CrossbarClockFrequencies is an empty list (ValueError) or None (TypeError)
                    CrossbarMaxFreq = 0
                    
                MaxClockFreq = max(NoCMaxFreq, BusMaxFreq, CrossbarMaxFreq)
                DivRatio = Fraction(MaxClockFreq / InputClockFrequency).limit_denominator((2**DVFSCounterResolution) - 1)

                # Checks if TargetFrequency < Input Frequency
                if TargetFrequency > InputClockFrequency:
                    print("Error: Target frequency <" + str(TargetFrequency) + " MHz> greater than input frequency <" + str(InputClockFrequency) + " MHz> for PEPos <" + str(PEPos) + "> Quantum <" + str(Quantum) + ">")  
                    exit(1)              

                # Ensures N/M fractional representation is rounded up
                if DivRatio * InputClockFrequency < TargetFrequency and DivRatio.numerator != 0:
                    print("Warning: Rounding computed N/M frequency of <" + str((DivRatio.numerator)/(DivRatio.denominator) * InputClockFrequency) + " MHz> up to <" + str((DivRatio.numerator + 1)/(DivRatio.denominator) * InputClockFrequency) + "MHz> for PE <" + str(PEPos) + ">, Quantum <" + str(Quantum) + ">.  Original frequency: " + str(TargetFrequency) + " MHz")
                    #DivRatio.numerator += 1  # Fraction.numerator is a @property method and cant be set directly
                    DivRatio = Fraction(numerator = DivRatio.numerator + 1, denominator = DivRatio.denominator)

                # Sets to minimum frequency if computed frequency = 0
                if DivRatio.numerator == 0:
                    print("Warning: Setting computed N/M frequency of 0 MHz to <" + str((1/((2**DVFSCounterResolution) - 1)) * InputClockFrequency) + " MHz> for PE <" + str(PEPos) + ">, Quantum <" + str(Quantum) + ">. Original frequency: " + str(TargetFrequency) + " MHz")
                    DivRatio = Fraction(numerator = 1, denominator = (2**DVFSCounterResolution) - 1)

                # Determines power switch enable signal on config flit
                SupplySwitchBit = '1' if DivRatio > Fraction(1, 2) else '0' 
                    
                # Determine IsNoC bit on config flit
                IsNoCBit = '1' if PE.CommStructure == "NoC" else '0'
                    
                # Determines config flit for DVFS Payload
                # Info flit fields (field bit width below):
                # |        Voltage Level        | IsNoC | ... |         N         |         M         |
                #   log2(AmountOfVoltageLevels)     1           CounterResolution   CounterResolution
                ConfigFlit = SupplySwitchBit + IsNoCBit + ZeroPadding + format(DivRatio.numerator, "0" + str(DVFSCounterResolution) + "b") + format(DivRatio.denominator, "0" + str(DVFSCounterResolution) + "b")
                ConfigFlit = '%0*X' % ((len(ConfigFlit) + 3) // 4, int(ConfigFlit, 2))  # Converts bit string to hex string "https://stackoverflow.com/questions/2072351/python-conversion-from-binary-string-to-hexadecimal"
                    
                # Adds Flow with custom Payload to master DVFS Thread
                #DVFSMaster.addFlow(AppComposer.CBRFlow(TargetThread = DVFSSources[PEPos], Bandwidth = 1000, StartTime = Quantum * QuantumTime, MSGAmount = 1, Payload = [DVFSServiceID, ConfigFlit]))
                DVFSSources[PEPos].addFlow(AppComposer.CBRFlow(TargetThread = DVFSSink, Bandwidth = 1000, StartTime = Quantum * QuantumTime, MSGAmount = 1, Payload = [DVFSServiceID, ConfigFlit]))
                
        # Add DVFS to AppDict
        if ReturnAsJSON:
            AppDict["GlobalGrained"] = DVFSApp.toJSON() 
        else:
            AppDict["GlobalGrained"] = DVFSApp
            
        # Write global-grained DVFS Application to a JSON file
        if SaveToFile:
            DVFSApp.toJSON(SaveToFile = True, FileName = PlatformName + "/DVFSAppGlobalGrained" + str(PlatformName) + "Resolution" + str(DVFSCounterResolution))    
         
    if GenStaticClocked:
        
        print("\nMaking static clocked DVFS Application")

        # Make Application
        DVFSApp = AppComposer.Application(AppName = "DVFSApp", StartTime = 0, StopTime = 0)

        # Make Threads
        DVFSSink = AppComposer.Thread(ThreadName = "Sink")
        DVFSSources = [AppComposer.Thread(ThreadName = "Source" + str(i)) for i in range(0, AmountOfPEs)]

        # Add Threads to DVFS Application
        DVFSApp.addThread(DVFSSink)
        for DVFSSource in DVFSSources:
            DVFSApp.addThread(DVFSSource)
        
        # Determine VF-pair setup for each Router/Bus/Crossbar in each time window (quantum)
        for Quantum in range(AmountOfQuantums):
            for PEPos, PE in enumerate(Platform.PEs):
            
                # Only NoC and first-of-struct PEs are needed (no DVFS for PEs inside Bus/Crossbar)
                if PE.CommStructure != "NoC" and PE.StructPos != 0:
                    continue
                
                # Skip Master PE, since a PE cant send a message to itself
                if PEPos == MasterPEPos:
                    continue

                # Determines N and M (numerator and denominator) on config flit
                #DivRatio = Fraction(MaxFrequency).limit_denominator(Resolution)
                DivRatio = Fraction(1, 1).limit_denominator((2**DVFSCounterResolution) - 1)
                
                # Checks if TargetFrequency < Input Frequency
                if TargetFrequency > InputClockFrequency:
                    print("Error: Target frequency <" + str(TargetFrequency) + " MHz> greater than input frequency <" + str(InputClockFrequency) + " MHz> for PEPos <" + str(PEPos) + "> Quantum <" + str(Quantum) + ">")  
                    exit(1)              

                # Ensures N/M fractional representation is rounded up
                if DivRatio * InputClockFrequency < TargetFrequency and DivRatio.numerator != 0:
                    print("Warning: Rounding computed N/M frequency of <" + str((DivRatio.numerator)/(DivRatio.denominator) * InputClockFrequency) + " MHz> up to <" + str((DivRatio.numerator + 1)/(DivRatio.denominator) * InputClockFrequency) + "MHz> for PE <" + str(PEPos) + ">, Quantum <" + str(Quantum) + ">. Original frequency: " + str(TargetFrequency) + " MHz")
                    #DivRatio.numerator += 1  # Fraction.numerator is a @property method and cant be set directly
                    DivRatio = Fraction(numerator = DivRatio.numerator + 1, denominator = DivRatio.denominator)

                # Sets to minimum frequency if computed frequency = 0
                if DivRatio.numerator == 0:
                    print("Warning: Setting computed N/M frequency of 0 MHz to <" + str((1/((2**DVFSCounterResolution) - 1)) * InputClockFrequency) + " MHz> for PE <" + str(PEPos) + ">, Quantum <" + str(Quantum) + ">. Original frequency: " + str(TargetFrequency) + " MHz")
                    DivRatio = Fraction(numerator = 1, denominator = (2**DVFSCounterResolution) - 1)

                # Determines power switch enable signal on config flit
                SupplySwitchBit = '1' if DivRatio > Fraction(1, 2) else '0' 
                    
                # Determine IsNoC bit on config flit
                IsNoCBit = '1' if PE.CommStructure == "NoC" else '0'
                    
                # Determines config flit for DVFS Payload
                # Info flit fields (field bit width below):
                # |        Voltage Level        | IsNoC | ... |         N         |         M         |
                #   log2(AmountOfVoltageLevels)     1           CounterResolution   CounterResolution
                ConfigFlit = SupplySwitchBit + IsNoCBit + ZeroPadding + format(DivRatio.numerator, "0" + str(DVFSCounterResolution) + "b") + format(DivRatio.denominator, "0" + str(DVFSCounterResolution) + "b")
                ConfigFlit = '%0*X' % ((len(ConfigFlit) + 3) // 4, int(ConfigFlit, 2))  # Converts bit string to hex string "https://stackoverflow.com/questions/2072351/python-conversion-from-binary-string-to-hexadecimal"
                    
                # Adds Flow with custom Payload to master DVFS Thread
                DVFSMaster.addFlow(AppComposer.CBRFlow(TargetThread = DVFSSources[PEPos], Bandwidth = 1000, StartTime = Quantum * QuantumTime, MSGAmount = 1, Payload = [DVFSServiceID, ConfigFlit]))
                
        # Add DVFS to AppDict
        if ReturnAsJSON:
            AppDict["StaticClocked"] = DVFSApp.toJSON() 
        else:
            AppDict["StaticClocked"] = DVFSApp
        
        # Write struct-grained DVFS Application to a JSON file
        if SaveToFile:
            DVFSApp.toJSON(SaveToFile = True, FileName = PlatformName + "/DVFSAppStaticClocked" + str(PlatformName)) 
    
    # Makes dummy DVFS app (Topology will keep maximum frequency value)
    if GenNoDVFS:

        print("\nMaking No-DVFS DVFS Application")

        # Make Application
        DVFSApp = AppComposer.Application(AppName = "DVFSApp", StartTime = 0, StopTime = 0)

        # Make Threads
        DVFSSink = AppComposer.Thread(ThreadName = "Sink")
        DVFSSources = [AppComposer.Thread(ThreadName = "Source" + str(i)) for i in range(0, AmountOfPEs)]

        # Add Threads to DVFS Application
        DVFSApp.addThread(DVFSSink)
        for DVFSSource in DVFSSources:
            DVFSApp.addThread(DVFSSource)
                
        # Add DVFS to AppDict
        if ReturnAsJSON:
            AppDict["NoDVFS"] = DVFSApp.toJSON() 
        else:
            AppDict["NoDVFS"] = DVFSApp
        
        # Write struct-grained DVFS Application to a JSON file
        if SaveToFile:
            DVFSApp.toJSON(SaveToFile = True, FileName = PlatformName + "/DVFSAppNoDVFS" + str(PlatformName)) 
        
    # Return Dict containing all apps     
    return AppDict    
