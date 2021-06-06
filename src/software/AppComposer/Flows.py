
import json

# TODO: Make Unrelated flow exception
# TODO: Merge identical Flows when they are added to a Thread
# TODO: Extend Flow class to support many types of flows (not only CBR), such as Markov chains and Pareto chains

class Flow:
    
    FlowTypes = ["CBR"]

    BaseFlowParameters = ["StartTime", "StopTime", "Periodic", "MSGAmount"]
    CBRFlowParameters = ["Bandwidth"]

    def __init__(self, TargetThread = None, SourceThread = None, FlowType = "CBR", StartTime = 0, StopTime = 0, Periodic = False, MSGAmount = 0, Header = ["ADDR", "SIZE"], Payload = ["FFFF0000", "APPID", "TGTID", "SRCID"] + (["RANDO"] * (126 - 4))):

        # Can be either a reference to a Thread object or a thread name, to be resolved to a reference when Application.resolveNames() is called
        self.SourceThread = SourceThread
        self.TargetThread = TargetThread
            
        # Index in SourceThread.OutgoingFlows[]. To be set when SourceThread.addFlow() is called
        #self.FlowID = None 
        
        # Only CBR type currently supported
        self.FlowType = FlowType
        
        # Dynamic parameters
        self.StartTime = StartTime
        self.StopTime = StopTime
        self.Periodic = Periodic  # WIP, doesnt do anything
        self.MSGAmount = MSGAmount

        # Injector parameters
        self.Header = Header
        self.Payload = Payload


    def toSerializableDict(self):

        flowDict = dict()
        
        #flowDict["SourceThread"] = self.SourceThread.ThreadName if isinstance(self.SourceThread, Thread) else self.SourceThread
        #flowDict["TargetThread"] = self.TargetThread.ThreadName if isinstance(self.TargetThread, Thread) else self.TargetThread
        flowDict["SourceThread"] = self.SourceThread if isinstance(self.SourceThread, str) else self.SourceThread.ThreadName
        flowDict["TargetThread"] = self.TargetThread if isinstance(self.TargetThread, str) else self.TargetThread.ThreadName
        #flowDict["Bandwidth"] = self.Bandwidth
        flowDict["FlowType"] = self.FlowType
        flowDict["StartTime"] = self.StartTime
        flowDict["StopTime"] = self.StopTime
        flowDict["Periodic"] = self.Periodic  # WIP, doesnt do anything (unused by Trigger.vhd)
        flowDict["MSGAmount"] = self.MSGAmount

        flowDict["Header"] = self.Header
        flowDict["Payload"] = self.Payload

        return flowDict


    def toJSON(self):
        return json.dumps(self.toSerializableDict(), sort_keys=False, indent=4)
    
    
    def fromJSON(self, JSONString):

        # Checks if to-dict conversion already happened, such as when called hierarchically from Thread.fromJSON()
        if isinstance(JSONString, dict):
            JSONDict = JSONString
        else:
            JSONDict = JSON.loads(JSONString)
        
        if self.FlowType in Flow.FlowTypes:

            if JSONDict["FlowType"] == "CBR":
                return CBRFlow(Bandwidth = JSONDict["Bandwidth"], TargetThread = JSONDict["TargetThread"], SourceThread = JSONDict["SourceThread"], StartTime = JSONDict["StartTime"], StopTime = JSONDict["StopTime"], 
                               Periodic = JSONDict["Periodic"], MSGAmount = JSONDict["MSGAmount"], Header = JSONDict["Header"], Payload = JSONDict["Payload"])

            # Other Flow types go here

        else:
            print("Error: FlowType <" + self.FlowType + "> not recognized")
            exit(1)
    

    def __eq__(self, other):
        
        # Directly compares 2 Thread objects
        if self.SourceThread is other.SourceThread and self.TargetThread is other.TargetThread and self.Bandwidth == other.Bandwidth:
            return True
        
        # Thread objects may be different but equivalent, such as when comparing 2 Threads in 2 different Workloads built from the same JSON file
        elif (self.SourceThread.AppName == other.SourceThread.AppName and self.TargetThread.AppName == other.TargetThread.AppName and 
              self.SourceThread.ThreadName == other.SourceThread.ThreadName and self.TargetThread.ThreadName == other.TargetThread.ThreadName and
              self.Bandwidth == other.Bandwidth):
            return True
            
        else:
            return False
    

class CBRFlow(Flow):

    def __init__(self, Bandwidth, TargetThread = None, SourceThread = None, StartTime = 0, StopTime = 0, Periodic = False, MSGAmount = 0, Header = ["ADDR", "SIZE"], Payload = ["FFFF0000", "APPID", "TGTID", "SRCID"] + (["RANDO"] * (126 - 4))):

        super().__init__(TargetThread = TargetThread, SourceThread = SourceThread, FlowType = "CBR", StartTime = StartTime, StopTime = StopTime, Periodic = Periodic, MSGAmount = MSGAmount, Header = Header, Payload = Payload)
        self.Bandwidth = Bandwidth  # In MBps


    def toSerializableDict(self):

        flowDict = super().toSerializableDict()
        flowDict["Bandwidth"] = self.Bandwidth

        return flowDict


    def toJSON(self):
        return json.dumps(self.toSerializableDict(), sort_keys=False, indent=4)


    def __str__(self):
    
        returnString = ""
        
        # SourceThread name
        if not isinstance(self.SourceThread, str) and self.SourceThread.ParentApplication is not None:
            returnString += self.SourceThread.ParentApplication.AppName + "."
            returnString += self.SourceThread.ThreadName
        else:
            returnString += self.SourceThread
            
        # Separator
        returnString += " -- " + str(self.Bandwidth) + " MBps -> "
        
        # TargetThread name
        if not isinstance(self.TargetThread, str) and self.TargetThread.ParentApplication is not None:
            returnString += self.TargetThread.ParentApplication.AppName + "."
            returnString += self.TargetThread.ThreadName
        else:
            returnString += self.TargetThread
        
        return returnString

