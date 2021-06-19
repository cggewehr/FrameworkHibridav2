import json
import math
import os
import sys
import AppComposer
import PlatformComposer

# A generic Packet log entry should look like: (| Target PEPos | Payload Size | Service ID | <Service specific data> | Timestamp | Checksum |)
# Timestamp field will be filled by the time (in ns) the first flit leaves the PE for output logs, or the time the last flit comes into the PE for input logs
class Packet:

    DVFSServiceID = "0000FFFF"
    SyntheticTrafficServiceID = "FFFF0000"
    
    MinimumOutputTimestamp = 0
    MaximumOutputTimestamp = None

    def __init__(self, ParentLog, TargetPEPos, Size, Service, Timestamp, Checksum):

        self.ParentLog = ParentLog
        self.TargetPEPos = int(TargetPEPos)
        self.Service = Service
        self.Size = int(Size)
        self.Timestamp = int(Timestamp)
        self.Checksum = int(Checksum)

    # Overloads operator " == " (Compares 2 Packet objects, used for comparing an input Log entry to an output Log entry)
    def __eq__(self, other):
        if (self.TargetPEPos == other.TargetPEPos and self.Size == other.Size and self.Service == other.Service and self.Checksum == other.Checksum):
            return True
        else:
            return False
        
    # Factory design pattern method for generating service-specific Packet objects (DVFSPacket, SyntheticTrafficPacket, ...) 
    @staticmethod
    def makePacket(LogLine, ParentLog):
        
        try:
            
            lineList = LogLine.split()

            TargetPEPos = lineList[0]
            Size = lineList[1]
            ServiceID = lineList[2]
            Data = lineList[3:len(lineList) - 2]
            Timestamp = lineList[-2]
            Checksum = lineList[-1]

        except KeyError:
            print("Error: Incomplete message <" + line + "> in entry <" + str(i) + "> of input log of PE <" + str(PEPos) + ">")
            exit(1)
        
        # Make service-specific objects based on Service entry field
        if ServiceID == Packet.DVFSServiceID:
            return DVFSPacket(ParentLog = ParentLog, TargetPEPos = TargetPEPos, Size = Size, Service = ServiceID, Data = Data, Timestamp = Timestamp, Checksum = Checksum)
        elif ServiceID == Packet.SyntheticTrafficServiceID:
            return SyntheticTrafficPacket(ParentLog = ParentLog, TargetPEPos = TargetPEPos, Size = Size, Service = ServiceID, Data = Data, Timestamp = Timestamp, Checksum = Checksum)
        else:
            print("Error: ServiceID <" + str(ServiceID) + "> not recognized for entry <" + str(i) + ": " + line + "> in input log of PE <" + str(PEPos) + ">")
            exit(1)
         
    def __str__(self):
        return "Target PEPos <" + str(self.TargetPEPos) + "> Size <" + str(self.Size) + "> Timestamp <" + str(self.Timestamp) + "> Checksum <" + str(self.Checksum) + ">"


# A DVFS Packet log entry should look like: (| Target PEPos | Payload Size | <DVFSServiceID> | <DVFS config flit> | Timestamp | Checksum |)
class DVFSPacket(Packet):

    # These class vars should be initialized as needed inside logparser()
    RouterFreq = None
    BusFreq = None
    CrossbarFreq = None
    
    RouterLatencies = None
    RouterLatencyCounters = None
    BusLatencies = None
    BusLatencyCounters = None
    CrossbarLatencies = None
    CrossbarLatencyCounters = None
    
    BusWrapperAddresses = None
    CrossbarWrapperAddresses = None
    PEs = None

    # Topology DVFS parameters
    DataWidth = None
    VoltageLevelFieldSize = None
    CounterResolution = None
    
    EnableParsing = False

    def __init__(self, ParentLog, TargetPEPos, Size, Service, Timestamp, Checksum, Data):
    
        # Do nothing if parsing of DVFS service packets is not enabled through the command line
        if not DVFSPacket.EnableParsing:
            return None
    
        super().__init__(ParentLog = ParentLog, TargetPEPos = TargetPEPos, Size = Size, Service = Packet.DVFSServiceID, Timestamp = Timestamp, Checksum = Checksum)
        
        # Parse ConfigFlit into DVFSController expected fields
        #ConfigFlit = str(Data[0])[::-1]  # Get string as VHDL slv (highest order bit at lowest index)
        ConfigFlit = str(Data[0])  # Get string as VHDL slv (highest order bit at lowest index)
        print(ConfigFlit)
        print(len(ConfigFlit))
        ConfigFlit = "".join(format(int(FlitHexChar, 16), "04b") for FlitHexChar in ConfigFlit)  # Converts Hex string, as saved in log txt, to binary string
        ConfigFlit = ConfigFlit[::-1]
        print(ConfigFlit)
        print(len(ConfigFlit))
        # TODO: Turn hex string into binary
        self.SupplySwitch = int(ConfigFlit[DVFSPacket.DataWidth - 1 : DVFSPacket.VoltageLevelFieldSize : -1], 2)
        #print(DVFSPacket.CounterResolution)
        self.IsNoC = ConfigFlit[DVFSPacket.VoltageLevelFieldSize]
        print("N Bit Field: " + ConfigFlit[2*DVFSPacket.CounterResolution - 1: DVFSPacket.CounterResolution - 1: -1])
        print("N Bit Field Length: " + str(len(ConfigFlit[2*DVFSPacket.CounterResolution - 1: DVFSPacket.CounterResolution - 1: -1])))
        self.N = int(ConfigFlit[2*DVFSPacket.CounterResolution - 1: DVFSPacket.CounterResolution - 1: -1], 2)
        print("N: " + str(self.N))
        #self.M = int(ConfigFlit[DVFSPacket.CounterResolution : -1 : -1], 2)
        print("M Bit Field: " + ConfigFlit[DVFSPacket.CounterResolution - 1: : -1])
        print("M length: " + str(len(ConfigFlit[DVFSPacket.CounterResolution - 1: : -1])))
        self.M = int(ConfigFlit[DVFSPacket.CounterResolution - 1: : -1], 2)
        print("M: " + str(self.M))

    @staticmethod
    def action(outEntry, matchingInEntry):

        # Check if current packet is within defined time bounds
        if outEntry.Timestamp < Packet.MinimumOutputTimestamp:
            return
        elif Packet.MaximumOutputTimestamp is not None and outEntry.Timestamp > Packet.MaximumOutputTimestamp:
            return
            
        #PE = DVFSPacket.PEs[matchingInEntry.ParentLog.PEPos]
        PE = DVFSPacket.PEs[outEntry.ParentLog.PEPos]
        CommStruct = PE.CommStructure
        StructPos = PE.StructPos
        BaseNoCPos = PE.BaseNoCPos
        baseFreq = 1000 / DVFSPacket.ClusterClocks[BaseNoCPos]
        Frequency = (outEntry.N / outEntry.M) * baseFreq
        #print("Frequency: " + str(Frequency))
        Latency = matchingInEntry.Timestamp - outEntry.Timestamp
            
        if CommStruct == "NoC" or outEntry.IsNoC == '1':
        
            DVFSPacket.RouterFreq[BaseNoCPos].append((outEntry.Timestamp, Frequency))
            
            DVFSPacket.RouterLatencyCounters[PE.PEPos] += 1
            DVFSPacket.RouterLatencies[PE.PEPos] += (Latency - DVFSPacket.RouterLatencies[PE.PEPos]) / DVFSPacket.RouterLatencyCounters[PE.PEPos]
            
        elif CommStruct == "Bus" and outEntry.IsNoC == '0':
            
            for i, WrapperID in enumerate(DVFSPacket.BusWrapperAddresses):

                if WrapperID == BaseNoCPos:

                    StructID = i

                    DVFSPacket.BusFreq[StructID].append((outEntry.Timestamp, Frequency))
                        
                    DVFSPacket.BusLatencyCounters[PE.PEPos] += 1
                    DVFSPacket.BusLatencies[PE.PEPos] += (Latency - DVFSPacket.BusLatencies[PE.PEPos]) / DVFSPacket.BusLatencyCounters[PE.PEPos]

                    break

            else:

                print("Error: No StructID found for Bus in BaseNoCPos <" + str(BaseNoCPos) + ">")
                exit(1)
        
        elif CommStruct == "Crossbar" and outEntry.IsNoC == '0':
        
            for i, WrapperID in enumerate(DVFSPacket.CrossbarWrapperAddresses):

                if WrapperID == BaseNoCPos:

                    StructID = i
            
                    DVFSPacket.CrossbarFreq[StructID].append((outEntry.Timestamp, Frequency))
                    
                    DVFSPacket.CrossbarLatencyCounters[PE.PEPos] += 1
                    DVFSPacket.CrossbarLatencies[PE.PEPos] += (Latency - DVFSPacket.CrossbarLatencies[PE.PEPos]) / DVFSPacket.CrossbarLatencyCounters[PE.PEPos]

                    break
                
            else:
                print("Error: No StructID found for Crossbar in BaseNoCPos <" + str(BaseNoCPos) + ">")
                exit(1)
                
                            
# A SyntheticTraffic Packet log entry should look like: (| Target PEPos | Payload Size | <SyntheticTrafficServiceID> | <AppID> | <TargetThreadID> | <SourceThreadID> | Timestamp | Checksum |)
class SyntheticTrafficPacket(Packet):
  
    # These class vars should be initialized as needed inside logparser()
    AvgLatenciesByThread = None
    #avgLatenciesCountersByFlow = None
    MissCountByThread = None
    HitCountByThread = None
    
    AvgLatenciesByPE = None
    #avgLatenciesCountersByPE = None
    MissCountByPE = None
    HitCountByPE = None   

    DataWidth = None
    
    EnableParsing = False
        
    def __init__(self, ParentLog, TargetPEPos, Size, Service, Timestamp, Checksum, Data):
    
        # Do nothing if parsing of DVFS service packets is not enabled through the command line
        if not SyntheticTrafficPacket.EnableParsing:
            return None
            
        super().__init__(ParentLog = ParentLog, TargetPEPos = TargetPEPos, Size = Size, Service = Packet.SyntheticTrafficServiceID, Timestamp = Timestamp, Checksum = Checksum)
        
        self.AppID = int(Data[0])
        self.TargetThreadID = int(Data[1])
        self.SourceThreadID = int(Data[2])
        
    @staticmethod
    def action(outEntry, matchingInEntry):
            
        if matchingInEntry is not None:
        
            latency = matchingInEntry.Timestamp - outEntry.Timestamp
            #print("Latency: " + str(latency) + " = " + str(matchingInEntry.Timestamp) + " - " + str(outEntry.Timestamp))
    
            # Incrementally updates average latency value for PE (https://blog.demofox.org/2016/08/23/incremental-averaging/)
            SourcePEPos = outEntry.ParentLog.PEPos
            TargetPEPos = outEntry.TargetPEPos
            #avgLatenciesCounters[src][tgt] += 1
            SyntheticTrafficPacket.HitCountByPE[SourcePEPos][TargetPEPos] += 1
            #avgLatenciesByPE[SourcePE][TargetPEPos] += (currentLatency - avgLatenciesByPE[SourcePEPos][TargetPEPos]) / avgLatenciesCountersByPE[SourcePEPos][TargetPEPos]
            SyntheticTrafficPacket.AvgLatenciesByPE[SourcePEPos][TargetPEPos] += (latency - SyntheticTrafficPacket.AvgLatenciesByPE[SourcePEPos][TargetPEPos]) \
                                                                                       / SyntheticTrafficPacket.HitCountByPE[SourcePEPos][TargetPEPos]
            #hitCount[src][tgt] += 1
            
            # Incrementally updates average latency value for Thread
            AppID = outEntry.AppID
            SourceThreadID = outEntry.SourceThreadID
            TargetThreadID = outEntry.TargetThreadID
            SyntheticTrafficPacket.HitCountByThread[AppID][SourceThreadID][TargetThreadID] += 1
            SyntheticTrafficPacket.AvgLatenciesByThread[AppID][SourceThreadID][TargetThreadID] += (latency - SyntheticTrafficPacket.AvgLatenciesByThread[AppID][SourceThreadID][TargetThreadID]) \
                                                                                                         / SyntheticTrafficPacket.HitCountByThread[AppID][SourceThreadID][TargetThreadID]
            # Increment PE total data count (in bytes)
            outEntry.ParentLog.TotalAmountOfData += (SyntheticTrafficPacket.DataWidth / 8) * outEntry.Size
            matchingInEntry.ParentLog.TotalAmountOfData += (SyntheticTrafficPacket.DataWidth / 8) * outEntry.Size
            
        else:
            
            print("Warning: No matching in log entry found for out log entry <" + str(outEntry) + "> of PE <" + str(outEntry.ParentLog.PEPos) + ">")
            
            print(str(outEntry.AppID))
            print(str(outEntry.SourceThreadID))
            print(str(outEntry.TargetThreadID))
            SyntheticTrafficPacket.MissCountByPE[outEntry.ParentLog.PEPos][outEntry.TargetPEPos] += 1
            SyntheticTrafficPacket.MissCountByThread[outEntry.AppID][outEntry.SourceThreadID][outEntry.TargetThreadID] += 1
  

class Log:

    def __init__(self, PEPos, LogType):
    
        self.Entries = []
        self.PEPos = PEPos
        self.LogType = LogType  # "Input" or "Output"
        self.TotalAmountOfData = 0  # in bytes, updated when SyntheticTrafficPacket.action() is called

    # Adds a Packet object to Entries array
    def addEntry(self, Packet):
    
        self.Entries.append(Packet)
        Packet.ParentLog = self

    @property
    def Throughput(self):
        
        if len(self.Entries) != 0:
            return 1000 * self.TotalAmountOfData / self.Entries[-1].Timestamp  # In MBps
        else:
            return 0

    def __str__(self):
    
        tempString = ""

        tempString += ("\t" + self.LogType + " log of PE " + str(self.PEPos) + ":\n")

        for i, Entry in enumerate(self.Entries):
            tempString += (str(i) + ": " + str(Entry) + "\n")

        return tempString


def logparser(args):

    # Gets framework configs
    with open(os.getenv("HIBRIDA_CONFIG_FILE"), "r") as ConfigFile:
        ConfigDict = json.loads(ConfigFile.read())
        
    # Gets framework project index
    with open(ConfigDict["HibridaPath"] + "/data/projectIndex.json", "r") as ProjectIndexFile:
        ProjectIndexDict = json.loads(ProjectIndexFile.read())
    
    # Sets default project as MRU project
    if args.ProjectName is None:
        print("Warning: No project passed as target, using <" + ConfigDict["MostRecentProject"] + "> as default")
        args.ProjectName = ConfigDict["MostRecentProject"]
        
    # Checks if project exists
    if args.ProjectName not in ProjectIndexDict.keys():
        print("Error: Project <" + args.ProjectName + "> doesnt exist")
        exit(1)
        
    # Gets project dir
    ProjectDir = ProjectIndexDict[args.ProjectName]
    
    LogDir = ProjectDir + "/log/"
    WorkloadFile = open(ProjectDir + "/src_json/Workload.json", "r")
    Workload = AppComposer.Workload().fromJSON(WorkloadFile.read())
    ClusterClocksFile = open(ProjectDir + "/src_json/ClusterClocks.json", "r")
    ClusterClocks = json.loads(ClusterClocksFile.read())
    TopologyFile = open(ProjectDir + "/src_json/Topology.json", "r")

    # Rebuilds Platform object
    print("Building Platform object")
    Topology = PlatformComposer.Platform().fromJSON(TopologyFile.read())
    TopologiesPECache = Topology.PEs
    AmountOfPEs = Topology.AmountOfPEs
    AmountOfRouters = Topology.BaseNoCDimensions[0] * Topology.BaseNoCDimensions[1]
    AmountOfBuses = Topology.AmountOfBuses
    AmountOfCrossbars = Topology.AmountOfCrossbars
    
    # Get time bounds from command line
    Packet.MinimumOutputTimestamp = args.MinimumOutputTimestamp
    Packet.MaximumOutputTimestamp = args.MaximumOutputTimestamp
    
    # TODO: Move these initializations into a service-specific class method
    # Inits class variables for DVFS service
    if args.DVFS:
    
        DVFSPacket.EnableParsing = True
        
        # Tuple = (Timestamp (in ns), Clock Frequency (in MHz))
        DVFSPacket.RouterFreq = [[(0, 1000/ClusterClocks[Router])] for Router in range(AmountOfRouters)]
        DVFSPacket.BusFreq = [[(0, 1000/ClusterClocks[Topology.Buses[Bus].BaseNoCPos])] for Bus in range(AmountOfBuses)]
        DVFSPacket.CrossbarFreq = [[(0, 1000/ClusterClocks[Topology.Crossbars[Crossbar].BaseNoCPos])] for Crossbar in range(AmountOfCrossbars)]

        DVFSPacket.RouterLatencies = [0 for Router in range(AmountOfRouters)]
        DVFSPacket.RouterLatencyCounters = [0 for Router in range(AmountOfRouters)]
        DVFSPacket.BusLatencies = [0 for Bus in range(AmountOfBuses)]
        DVFSPacket.BusLatencyCounters = [0 for Bus in range(AmountOfBuses)]
        DVFSPacket.CrossbarLatencies = [0 for Crossbar in range(AmountOfCrossbars)]
        DVFSPacket.CrossbarLatencyCounters = [0 for Crossbar in range(AmountOfCrossbars)]

        DVFSPacket.DataWidth = int(Topology.DataWidth)
        DVFSPacket.VoltageLevelFieldSize = int(math.ceil(math.log2(Topology.DVFSAmountOfVoltageLevels)))
        DVFSPacket.CounterResolution = int(Topology.DVFSCounterResolution)

        DVFSPacket.BusWrapperAddresses = Topology.BusWrapperAddresses
        DVFSPacket.CrossbarWrapperAddresses = Topology.CrossbarWrapperAddresses
        DVFSPacket.PEs = Topology.PEs

        DVFSPacket.ClusterClocks = ClusterClocks
    
    # Inits class variables for synthetic traffic service
    if args.PE or args.Thread:
    
        SyntheticTrafficPacket.EnableParsing = True
    
        SyntheticTrafficPacket.AvgLatenciesByThread = [[[0 for TargetThread in Application.Threads] for SourceThread in Application.Threads] for Application in Workload.Applications]
        #avgLatenciesCountersByFlow = [[[0 for OutgoingFlow in TargetThread.OutgoingFlows] for SourceThread in Application.Threads] for Application in Workload.Applications]
        SyntheticTrafficPacket.MissCountByThread = [[[0 for TargetThread in Application.Threads] for SourceThread in Application.Threads] for Application in Workload.Applications]
        SyntheticTrafficPacket.HitCountByThread = [[[0 for TargetThread in Application.Threads] for SourceThread in Application.Threads] for Application in Workload.Applications]
        
        SyntheticTrafficPacket.AvgLatenciesByPE = [[0 for TargetPE in range(AmountOfPEs)] for SourcePE in range(AmountOfPEs)]
        #avgLatenciesCountersByPE = [[0 for TargetPE in range(AmountOfPEs)] for SourcePE in range(AmountOfPEs)]
        SyntheticTrafficPacket.MissCountByPE = [[0 for TargetPE in range(AmountOfPEs)] for SourcePE in range(AmountOfPEs)]
        SyntheticTrafficPacket.HitCountByPE = [[0 for TargetPE in range(AmountOfPEs)] for SourcePE in range(AmountOfPEs)]   
        
        SyntheticTrafficPacket.BusWrapperAddresses = Topology.BusWrapperAddresses
        SyntheticTrafficPacket.CrossbarWrapperAddresses = Topology.CrossbarWrapperAddresses
        SyntheticTrafficPacket.PEs = Topology.PEs

        SyntheticTrafficPacket.DataWidth = int(Topology.DataWidth)
        SyntheticTrafficPacket.VoltageLevelFieldSize = int(math.ceil(math.log2(Topology.DVFSAmountOfVoltageLevels)))
        SyntheticTrafficPacket.CounterResolution = int(Topology.DVFSCounterResolution)

    # Starts script execution
    print("Parsing log files")
    print("Looking for log files at " + LogDir)

    # Inits Log objects
    InLogs = [Log(PEPos = PEPos, LogType = "Input") for PEPos in range(0, AmountOfPEs)]
    OutLogs = [Log(PEPos = PEPos, LogType = "Output") for PEPos in range(0, AmountOfPEs)]

    # Parse log files into Log and Packet objects
    for PEPos in range(0, AmountOfPEs):

        with open(LogDir + "PE " + str(PEPos) + "/InLog" + str(PEPos) + ".txt", "r") as InLogFile:

            print("Parsing in log of PE " + str(PEPos))
            
            for i, line in enumerate(InLogFile.read().splitlines()):
                InEntry = Packet.makePacket(LogLine = line, ParentLog = InLogs[PEPos])
                if InEntry is not None:
                    InLogs[PEPos].addEntry(InEntry)
                    
        with open(LogDir + "PE " + str(PEPos) + "/OutLog" + str(PEPos) + ".txt", "r") as OutLogFile:
        
            print("Parsing out log of PE " + str(PEPos))

            for i, line in enumerate(OutLogFile.read().splitlines()):
                OutEntry = Packet.makePacket(LogLine = line, ParentLog = OutLogs[PEPos])
                if OutEntry is not None:
                    OutLogs[PEPos].addEntry(OutEntry)
    
    print("Done parsing log files")

    # Tries to find an In log entry match for every Out log entry
    for SourcePEPos, currentOutLog in enumerate(OutLogs):

        print("Working on out log of PE " + str(SourcePEPos))

        # Loop through all entries in current Out log
        for outEntryNumber, currentOutEntry in enumerate(currentOutLog.Entries):
                
            # Check if current packet is being sent to a PE that exists (TargetPEPos < Topology.AmountOfPEs)
            try:
                currentInLog = InLogs[currentOutEntry.TargetPEPos]
            except KeyError:
                print("Error: Out Log for PE <" + str(SourcePEPos) + "> entry <" + str(outEntryNumber) + "> defines a message to PEPos <" + str(currentOutEntry.TargetPEPos) + ">, which doesn't exist in given Topology")
                exit(1)

            # Loop through all entries of current In log, compares each of them to current message in current Out log (compares checksum of Out entry to checksum of In entry in Packet.__eq__())
            matchingInEntry = None
            for currentInEntry in currentInLog.Entries:
                if currentOutEntry == currentInEntry:
                    matchingInEntry = currentInEntry
                    #print("Found match for entry " + str(outEntryNumber))
                    #print(str(currentOutEntry))
                    #print(str(matchingInEntry))
                    currentInLog.Entries.remove(currentOutEntry)
                    break
            
            # Calls service-specific action()
            currentOutEntry.action(currentOutEntry, matchingInEntry)
                
        print("Done working on out log of PE " + str(SourcePEPos))

    # Checks if there are any unprocessed entries left on In logs
    print("Checking for unprocessed In log entries")
    for InLog in InLogs:
        print("Found " + str(len(InLog.Entries)) + " unprocessed entries in In log of PE " + str(InLog.PEPos))
    print("Done checking for unprocessed In log entries")
        
    # Prints out amount of successfully delivered messages
    if args.PE or args.Thread:
        print("\n\tSuccessfully Delivered Messages:")

    if args.PE:
    
        hitCountByPE = SyntheticTrafficPacket.HitCountByPE
        missCountByPE = SyntheticTrafficPacket.MissCountByPE
    
        for source in range(AmountOfPEs):
            for target in range(AmountOfPEs):
                if hitCountByPE[source][target] + missCountByPE[source][target] > 0:
                    print("Messages successfully delivered from PE <" + str(source) + "> to PE <" + str(target) + ">: " +
                          str(hitCountByPE[source][target]) + "/" + str(hitCountByPE[source][target] + missCountByPE[source][target]))
                          
    if args.Thread:
    
        hitCountByThread = SyntheticTrafficPacket.HitCountByThread
        missCountByThread = SyntheticTrafficPacket.MissCountByThread
    
        #for AppID, Application in enumerate(hitCountByThread):
        for AppID, Application in enumerate(Workload.ApplicationsByID):
            for SourceThreadID, SourceThread in enumerate(Application.ThreadsByID):
                #for TargetThreadID, TargetThread in enumerate(hitCountByThread[AppID][SourceThreadID]):
                for TargetThreadID, TargetThread in enumerate(Application.ThreadsByID):
                
                    AppName = Application.AppName
                    SourceThreadName = SourceThread.ThreadName
                    TargetThreadName = TargetThread.ThreadName
                    
                    if hitCountByThread[AppID][SourceThreadID][TargetThreadID] + missCountByThread[AppID][SourceThreadID][TargetThreadID] > 0:
                        print("Messages successfully delivered from Thread <" + AppName + "." + str(SourceThreadName) + "> to Thread <" + AppName + "." + str(TargetThreadName) + ">: " +
                              str(hitCountByThread[AppID][SourceThreadID][TargetThreadID]) + "/" + str(hitCountByThread[AppID][SourceThreadID][TargetThreadID] + missCountByThread[AppID][SourceThreadID][TargetThreadID]))

    # Prints out average latency values
    if args.PE or args.Thread:
        print("\n\tAverage Network Latency Values:")

    if args.PE:
    
        avgLatenciesByPE = SyntheticTrafficPacket.AvgLatenciesByPE
        
        for source in range(AmountOfPEs):
            for target in range(AmountOfPEs):
                if avgLatenciesByPE[source][target] != 0:
                    print("Average network latency from PE <" + str(source) + "> to PE <" + str(target) + ">: " + str(avgLatenciesByPE[source][target]) + " ns")
         
    if args.Thread:
    
        avgLatenciesByThread = SyntheticTrafficPacket.AvgLatenciesByThread
        
        for Application in Workload.Applications:
            for SourceThread in Application.Threads:
                for TargetThread in Application.Threads:
                
                    AppName = Application.AppName
                    AppID = Application.AppID
                    SourceThreadName = SourceThread.ThreadName
                    SourceThreadID = SourceThread.ThreadID
                    TargetThreadName = TargetThread.ThreadName
                    TargetThreadID = TargetThread.ThreadID
                    
                    #if avgLatenciesByThread[source][target] != 0:
                    if avgLatenciesByThread[AppID][SourceThreadID][TargetThreadID] != 0:
                            print("Average network latency from Thread <" + AppName + "." + SourceThreadName + "> to Thread <" + AppName + "." + str(TargetThreadName) + ">: " +
                                  str(avgLatenciesByThread[AppID][SourceThreadID][TargetThreadID]) + " ns")

    # Prints out throughput. TODO: Throughput by Thread
    if args.PE:

        print("\n\tThroughput by PE:")

        for PEPos in range(AmountOfPEs):
            print("PE <" + str(PEPos) + "> output throughput: " + str(OutLogs[PEPos].Throughput) + " MBps")

            # TODO: Input throughput 
            #print("PE <" + str(PEPos) + "> input throughput: " + str(InLogs[PEPos].Throughput) + " MBps")

    # Prints out frequency info for Router/Bus/Crossbar from DVFS service packets
    if args.DVFS:

        print("\n\tRouter Clock Frequencies:")

        routerFreq = DVFSPacket.RouterFreq

        for i, router in enumerate(routerFreq):
            print("\nRouter " + str(i) + ":")
            for freqTuple in router:
                print("Frequency set to <" + str(freqTuple[1]) + "> MHz @ <" + str(freqTuple[0]) + "> ns")
        
        if AmountOfBuses != 0:     
   
            print("\n\tBus Clock Frequencies:")

            busFreq = DVFSPacket.BusFreq

            for i, bus in enumerate(busFreq):
                print("\nBus " + str(i) + ":")
                for freqTuple in bus:
                    print("Frequency set to <" + str(freqTuple[1]) + "> MHz @ <" + str(freqTuple[0]) + "> ns")
            
        if AmountOfCrossbars != 0:  

            print("\n\tCrossbar Clock Frequencies:")

            crossbarFreq = DVFSPacket.CrossbarFreq

            for i, crossbar in enumerate(crossbarFreq):
                print("\nCrossbar " + str(i) + ":")
                for freqTuple in crossbar:
                    print("Frequency set to <" + str(freqTuple[1]) + "> MHz @ <" + str(freqTuple[0]) + "> ns")
                
        # TODO: Latencies for DVFS messages

    with open(os.getenv("HIBRIDA_CONFIG_FILE"), "w") as ConfigFile:
        ConfigDict["MostRecentProject"] = args.ProjectName
        ConfigFile.write(json.dumps(ConfigDict, sort_keys = False, indent = 4))
    
    print("\nlogparser executed successfully!")
