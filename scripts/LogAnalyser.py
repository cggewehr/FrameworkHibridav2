import json
import os
import sys
import AppComposer
import PlatformComposer

# A generic Packet log entry should look like: (| Target PEPos | Payload Size | Service ID | <Service specific data> | Timestamp | Checksum |)
# Timestamp field will be filled by the time (in ns) the first flit leaves the PE for output logs, or the time the last flit comes into the PE for input logs
class Packet:

    DVFSServiceID = "0000FFFF"
    SyntheticTrafficServiceID = "FFFF0000"

    def __init__(self, ParentLog, TargetPEPos, Size, Service, Timestamp, Checksum):

        self.ParentLog = ParentLog
        self.TargetPEPos = TargetPEPos
        self.Service = Service
        self.Size = Size
        self.Timestamp = Timestamp
        self.Checksum = Checksum

    # Overloads operator " == " (Compares 2 Packet objects, used for comparing an input Log entry to an output Log entry)
    def __eq__(self, other):
        if (self.TargetPEPos == other.TargetPEPos and self.Size == other.Size and self.Service == other.Service and self.Checksum == other.Checksum):
            return True
        else:
            return False

    # def __str__(self):
        # try:
            # return ("\nTargetID = " + str(self.TargetID) +
                    # "\nSourceID = " + str(self.SourceID) +
                    # "\nMessageSize = " + str(self.MessageSize) +
                    # "\nOutputTimestamp = " + str(self.OutputTimestamp) +
                    # "\nInputTimestamp = " + str(self.InputTimestamp))

        # except AttributeError:  # No InputTimestamp attribute
            # return ("\nTargetID = " + str(self.TargetID) +
                    # "\nSourceID = " + str(self.SourceID) +
                    # "\nMessageSize = " + str(self.MessageSize) +
                    # "\nOutputTimestamp = " + str(self.OutputTimestamp))


# A DVFS Packet log entry should look like: (| Target PEPos | Payload Size | <DVFSServiceID> | <DVFS config flit> | Timestamp | Checksum |)
class DVFSPacket(Packet):

    # These class vars should be initialized as needed inside loganalyser()
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

    def __init__(self, ParentLog, TargetPEPos, Size, Service, Timestamp, Checksum, Data):
    
        super().__init__(ParentLog = ParentLog, TargetPEPos = TargetPEPos, Size = Size, Service = Packet.DVFSServiceID, Timestamp = Timestamp, Checksum = Checksum)
        ConfigFlit = Data[0]
        
        # TODO: Parse ConfigFlit
        #self.IsNoC = Data[0]
        #self.SupplySwitch = Data[1]
        #self.N = Data[2]
        #self.M = Data[3]
        #self.Timestamp = Data[4]   
        
    @staticmethod
    def action(outEntry, matchingInEntry):

        PE = DVFSPacket.PEs[matchingInEntry.ParentLog.PEPos]
        CommStruct = PE.CommStructure
        StructPos = PE.StructPos
        BaseNoCPos = PE.BaseNoCPos
        Frequency = (outEntry.N / outEntry.M) * ClusterClocks[BaseNoCPos]
        Latency = matchingInEntry.Timestamp - outEntry.Timestamp
            
        if CommStruct == "NoC" or outEntry.IsNoC == '1':
        
            DVFSPacket.RouterFreq[BaseNoCPos].append((outEntry.InputTimestamp, Frequency))
            
            DVFSPacket.RouterLatencyCounters[PE.PEPos] += 1
            DVFSPacket.RouterLatencies[PE.PEPos] += (Latency - DVFSPacket.RouterLatencies[PE.PEPos]) / DVFSPacket.RouterLatencyCounters[PE.PEPos]
            
        elif CommStruct == "Bus" and outEntry.IsNoC == '0':
            
            StructID = None
            for i, WrapperID in enumerate(DVFSPacket.BusWrapperAddresses):
                if WrapperID == BaseNoCPos:
                    StructID = i
                  
            if StructID is not None:
            
                DVFSPacket.BusFreq[StructID].append((outEntry.InputTimestamp, Frequency))
                    
                DVFSPacket.BusLatencyCounters[PE.PEPos] += 1
                DVFSPacket.BusLatencies[PE.PEPos] += (Latency - DVFSPacket.BusLatencies[PE.PEPos]) / DVFSPacket.BusLatencyCounters[PE.PEPos]
            
            else:
                print("Error: No StructID found for Bus in BaseNoCPos <" + str(BaseNoCPos) + ">")
                exit(1)
        
        elif CommStruct == "Crossbar" and outEntry.IsNoC == '0':
        
            StructID = None
            for i, WrapperID in enumerate(DVFSPacket.CrossbarWrapperAddresses):
                if WrapperID == BaseNoCPos:
                    StructID = i
                    
            if StructID is not None:
            
                DVFSPacket.CrossbarFreq[StructID].append((outEntry.InputTimestamp, Frequency))
                
                DVFSPacket.CrossbarLatencyCounters[PE.PEPos] += 1
                DVFSPacket.CrossbarLatencies[PE.PEPos] += (Latency - DVFSPacket.CrossbarLatencies[PE.PEPos]) / DVFSPacket.CrossbarLatencyCounters[PE.PEPos]
                
            else:
                print("Error: No StructID found for Crossbar in BaseNoCPos <" + str(BaseNoCPos) + ">")
                exit(1)
                
                            
# A SyntheticTraffic Packet log entry should look like: (| Target PEPos | Payload Size | <SyntheticTrafficServiceID> | <AppID> | <TargetThreadID> | <SourceThreadID> | Timestamp | Checksum |)
class SyntheticTrafficPacket(Packet):
  
    # These class vars should be initialized as needed inside loganalyser()
    AvgLatenciesByThread = None
    #avgLatenciesCountersByFlow = None
    MissCountByThread = None
    HitCountByThread = None
    
    AvgLatenciesByPE = None
    #avgLatenciesCountersByPE = None
    MissCountByPE = None
    HitCountByPE = None   
        
    def __init__(self, ParentLog, TargetPEPos, Size, Service, Timestamp, Checksum, Data):
    
        super().__init__(ParentLog = ParentLog, TargetPEPos = TargetPEPos, Size = Size, Service = Packet.SyntheticTrafficServiceID, Timestamp = Timestamp, Checksum = Checksum)
        self.AppID = int(Data[0])
        self.TargetThreadID = int(Data[1])
        self.SourceThreadID = int(Data[2])
        
    @staticmethod
    def action(outEntry, matchingInEntry):
        
        if matchingInEntry is not None:
        
            latency = matchingInEntry.Timestamp - outEntry.Timestamp
    
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
        else:
            
            print("Warning: No matching in log entry found for out log entry <" + str(outEntry) + "> of PE <" + outEntry.ParentLog.PEPos + ">")
        
            SyntheticTrafficPacket.MissCountByPE[outEntry.ParentLog.PEPos][outEntry.TargetPEPos] += 1
            SyntheticTrafficPacket.MissCountByThread[outEntry.AppID][outEntry.SourceThreadID][outEntry.TargetThreadID] += 1
           

class Log:

    def __init__(self, PEPos, LogType):
    
        self.Entries = []
        self.PEPos = PEPos
        self.LogType = LogType  # "Input" or "Output"

    # Adds a Packet object to Entries array
    def addEntry(self, Packet):
    
        self.Entries.append(Packet)
        Packet.ParentLog = self
        

    def __str__(self):
    
        tempString = ""

        tempString += ("\t" + self.LogType + " log of PE " + str(self.PEPos) + ":\n")

        for i, Entry in enumerate(self.Entries):
            tempString += (str(i) + ": " + str(Entry) + "\n")

        return tempString


def loganalyser(args):

    # Gets framework & project info
    ConfigFile = open(os.getenv("HIBRIDA_CONFIG_FILE"), "r")
    ConfigDict = json.loads(ConfigFile.read())
    ProjectDir = ConfigDict["Projects"][args.ProjectName]["ProjectDir"]
    LogDir = ProjectDir + "/logs/"
    WorkloadFile = open(ProjectDir + "/src_json/Workload.json", "r")
    Workload = AppComposer.Workload().fromJSON(WorkloadFile.read())
    ClusterClocksFile = open(ProjectDir + "/src_json/ClusterClocks.json", "r")
    ClusterClocks = json.loads(ClusterClocksFile.read())
    TopologyFile = open(ProjectDir + "/src_json/Topology.json", "r")
    Topology = PlatformComposer.Platform().fromJSON(TopologyFile.read())
    TopologiesPECache = Topology.PEs
    AmountOfPEs = Topology.AmountOfPEs
    AmountOfRouters = Topology.BaseNoCDimensions[0] * Topology.BaseNoCDimensions[1]
    AmountOfBuses = Topology.AmountOfBuses
    AmountOfCrossbars = Topology.AmountOfCrossbars
    
    # Inits computation variables for DVFS service
    if args.DVFS:
        
        DVFSPacket.RouterFreq = [[(0, ClusterClocks[Router])] for Router in range(AmountOfRouters)]
        DVFSPacket.BusFreq = [[(0, ClusterClocks[Topology.Buses[Bus].BaseNoCPos])] for Bus in range(AmountOfBuses)]
        DVFSPacket.CrossbarFreq = [[(0, ClusterClocks[Topology.Crossbars[Crossbar].BaseNoCPos])] for Crossbar in range(AmountOfCrossbars)]
        
        DVFSPacket.Latencies = [0 for PE in range(AmountOfPEs)]
        DVFSPacket.LatencyCounters = [0 for PE in range(AmountOfPEs)]
    
    # Inits computation variables for synthetic traffic service
    if args.PE or args.Thread:
    
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

    # Starts script execution
    print("Parsing log files")
    print("Looking for log files at " + LogDir)

    # Inits Log objects
    InLogs = [Log(PEPos = PEPos, LogType = "Input") for PEPos in range(0, AmountOfPEs)]
    OutLogs = [Log(PEPos = PEPos, LogType = "Output") for PEPos in range(0, AmountOfPEs)]

    # Parse log files into Log and Packet objects
    for PEPos in range(0, AmountOfPEs):

        with open(LogDir + "InLog" + str(PEPos) + "/", "r") as InLogFile:
        
            InLog = InLogs[PEPos]
            
            for i, line in enumerate(InLogFile.read().splitlines()):
            
                lineList = line.split()
                
                try:
                    TargetPEPos = lineList[0]
                    Size = lineList[1]
                    ServiceID = lineList[2]
                    Data = lineList[3:len(lineList) - 2]
                    Timestamp = lineList[-2]
                    Checksum = lineList[-1]
                except KeyError:
                    print("Warning: Incomplete message <" + line + "> in entry <" + str(i) + "> of input log of PE <" + str(PEPos) + ">")
                
                if ServiceID == Packet.DVFSServiceID:
                    InLog.addEntry(DVFSPacket(ParentLog = InLog, TargetPEPos = TargetPEPos, Size = Size, Service = ServiceID, Data = Data, Timestamp = Timestamp, Checksum = Checksum))
                elif ServiceID == Packet.SyntheticTrafficServiceID:
                    InLog.addEntry(SyntheticTrafficPacket(ParentLog = InLog, TargetPEPos = TargetPEPos, Size = Size, Service = ServiceID, Data = Data, Timestamp = Timestamp, Checksum = Checksum))
                else:
                    print("Error: ServiceID <" + str(ServiceID) + "> not recognized for entry <" + str(i) + ": " + line + "> in input log of PE <" + str(PEPos) + ">")
                    exit(1)
                    
        with open(LogDir + "OutLog" + str(PEPos) + "/", "r") as OutLogFile:
        
            OutLog = OutLogs[PEPos]
            
            for i, line in enumerate(InLogFile.read().splitlines()):
            
                lineList = line.split()
                
                try:
                    TargetPEPos = lineList[0]
                    Size = lineList[1]
                    ServiceID = lineList[2]
                    Data = lineList[3:len(lineList) - 2]
                    Timestamp = lineList[-2]
                    Checksum = lineList[-1]
                except KeyError:
                    print("Warning: Incomplete message <" + line + "> in entry <" + str(i) + "> of output log of PE <" + str(PEPos) + ">")
                
                if ServiceID == Packet.DVFSServiceID:
                    OutLog.addEntry(DVFSPacket(ParentLog = OutLog, TargetPEPos = TargetPEPos, Size = Size, Service = ServiceID, Data = Data, Timestamp = Timestamp, Checksum = Checksum))
                elif ServiceID == Packet.SyntheticTrafficServiceID:
                    OutLog.addEntry(SyntheticTrafficPacket(ParentLog = OutLog, TargetPEPos = TargetPEPos, Size = Size, Service = ServiceID, Data = Data, Timestamp = Timestamp, Checksum = Checksum))
                else:
                    print("Error: ServiceID <" + str(ServiceID) + "> not recognized for entry <" + str(i) + ": " + line + "> in output log of PE <" + str(PEPos) + ">")
                    exit(1)
    
    print("Done parsing log files")

    # Tries to find an In log entry match for every Out log entry
    for SourcePEPos, currentOutLog in enumerate(OutLogs):

        print("Working on out log of PE " + str(SourcePEPos))

        # Loop through all entries in current Out log
        for outEntryNumber, currentOutEntry in enumerate(currentOutLog.Entries):
            
            # Check if current packet is within defined time bounds
            if currentOutEntry.Timestamp < args.MinimumOutputTimestamp:
                continue
            elif args.MaximumOutputTimestamp is not None and currentOutEntry.Timestamp > args.MaximumOutputTimestamp:
                break
                
            # Check if current packet is being sent to a PE that exists (TargetPEPos < Topology.AmountOfPEs)
            try:
                currentInLog = InLogs[currentOutEntry.TargetPEPos]
            except KeyError:
                print("Error: Out Log for PE <" + str(SourcePEPos) + "> entry <" + str(outEntryNumber) + "> defines a message to PEPos <" + str(currentOutEntry.TargetPEPos) + ">, which doesn't exist")
                exit(1)

            # Loop through all entries of current In log, compares each of them to current message in current Out log
            matchingInEntry = None
            for currentInEntry in currentInLog.Entries:
                if currentOutEntry == currentInEntry:
                    matchingInEntry = currentInEntry
                    break
            
            currentOutEntry.action(currentOutEntry, matchingInEntry)
                
        print("Done working on out log of PE " + str(SourcePEPos))
        
    # Prints out amount of successfully delivered messages
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
        for AppID, Application in enumerate(Workload):
            for SourceThreadID, SourceThread in enumerate(Application):
                #for TargetThreadID, TargetThread in enumerate(hitCountByThread[AppID][SourceThreadID]):
                for TargetThreadID, TargetThread in enumerate(Application):
                
                    AppName = Application.AppName
                    SourceThreadName = SourceThread.ThreadName
                    TargetThreadName = TargetThread.ThreadName
                    
                    if hitCountByThread[AppID][SourceThreadID][TargetThreadID] + missCountByThread[AppID][SourceThreadID][TargetThreadID] > 0:
                        print("Messages successfully delivered from Thread <" + str(SourceThreadName) + "> to Thread <" + str(TargetThreadName) + ">: " +
                              str(hitCountByThread[AppID][SourceThreadID][TargetThreadID]) + "/" + str(hitCountByThread[AppID][SourceThreadID][TargetThreadID] + missCountByThread[AppID][SourceThreadID][TargetThreadID]))

    # Prints out average latency values
    print("\n\tAverage Latency Values:")
    if args.PE:
    
        avgLatenciesByPE = SyntheticTrafficPacket.AvgLatenciesByPE
        
        for source in range(amountOfPEs):
            for target in range(amountOfPEs):
                if avgLatenciesByPE[source][target] != 0:
                    print("Average latency from PE <" + str(source) + "> to PE <" + str(target) + ">: " + str(avgLatenciesByPE[source][target]) + " ns")
         
    if args.Thread:
    
        avgLatenciesByThread = SyntheticTrafficPacket.AvgLatenciesByThread
        
        #for AppID, Application in enumerate(hitCountByThread):
        for AppID, Application in enumerate(Workload):
            for SourceThreadID, SourceThread in enumerate(Application):
                #for TargetThreadID, TargetThread in enumerate(hitCountByThread[AppID][SourceThreadID]):
                for TargetThreadID, TargetThread in enumerate(Application):
                
                    AppName = Application.AppName
                    SourceThreadName = SourceThread.ThreadName
                    TargetThreadName = TargetThread.ThreadName
                    
                    if avgLatenciesByThread[source][target] != 0:
                            print("Average latency from Thread <" + str(SourceThreadName) + "> to Thread <" + str(TargetThreadName) + ">: " +
                                  str(avgLatenciesByThread[source][target]) + " ns")

    # Print out frequency info for Router/Bus/Crossbar from DVFS service packets
    if args.DVFS:
        print("\n\tRouter Clock Frequencies:")
        for i, router in enumerate(routerFreq):
            print("\nRouter " + str(i) + ":")
            for freqTuple in router:
                print("Frequency set to <" + str(freqTuple[1]) + "> MHz @ <" + str(freqTuple[0]) + "> ns")
                
        print("\n\tBus Clock Frequencies:")
        for bus in busFreq:
            print("\nBus " + str(i) + ":")
            for freqTuple in bus:
                print("Frequency set to <" + str(freqTuple[1]) + "> MHz @ <" + str(freqTuple[0]) + "> ns")
            
        print("\n\tCrossbar Clock Frequencies:")
        for crossbar in crossbarFreq:
            print("\nCrossbar " + str(i) + ":")
            for freqTuple in crossbar:
                print("Frequency set to <" + str(freqTuple[1]) + "> MHz @ <" + str(freqTuple[0]) + "> ns")
                
        # TODO: Latencies for DVFS messages
    
    print("loganalyser ran successfully!")
