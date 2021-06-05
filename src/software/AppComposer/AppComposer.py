
import copy
import json as JSON

# TODO: Make Unrelated flow exception
# TODO: Merge identical Flows when they are added to a Thread
# TODO: Extend Flow class to support many types of flows (not only CBR), such as Markov chains and Pareto chains

class Flow:

    FlowParameters = ["StartTime", "StopTime", "Periodic", "MSGAmount", "ControlFlowFlag"]

    #def __init__(self, Bandwidth, TargetThread, SourceThread = None, FlowType = "CBR", StartTime = 0, StopTime = -1, Periodic = False, MSGAmount = 0, ControlFlowFlag = False):
    #def __init__(self, Bandwidth, TargetThread, SourceThread = None, FlowType = "CBR", StartTime = 0, StopTime = 0, Periodic = False, MSGAmount = 0, ControlFlowFlag = False, Header = ["ADDR", "SIZE"], Payload = ["PEPOS", "TMSTP"] + (["RANDO"] * (126 - 2))):
    def __init__(self, Bandwidth, TargetThread, SourceThread = None, FlowType = "CBR", StartTime = 0, StopTime = 0, Periodic = False, MSGAmount = 0, ControlFlowFlag = False, Header = ["ADDR", "SIZE"], Payload = ["FFFF0000", "APPID", "TGTID", "SRCID"] + (["RANDO"] * (126 - 4))):

        # SourceThread must be a Thread object
        if isinstance(SourceThread, Thread) or SourceThread is None:
            self.SourceThread = SourceThread
            
        else:
            print("Error: Given <SourceThread: " + str(SourceThread) + "> is not a Thread object")
            exit(1)
            
        # TargetThread must be a Thread object
        if isinstance(TargetThread, Thread):
            self.TargetThread = TargetThread
            
        else:
            print("Error: Given <TargetThread: " + str(TargetThread) + "> is not a Thread object")
            exit(1)
            
        # Index in SourceThread.OutgoingFlows[]. To be set when SourceThread.addFlow() is called
        #self.FlowID = None 
        
        # Only CBR type currently supported
        self.FlowType = FlowType  # Only CBR type currently supported
        
        # CBR Flow type parameters
        self.Bandwidth = Bandwidth  # In MBps
        
        # Dynamic parameters
        self.StartTime = StartTime
        self.StopTime = StopTime
        self.Periodic = Periodic  # WIP, doesnt do anything
        self.MSGAmount = MSGAmount
        self.ControlFlowFlag = ControlFlowFlag  # WIP, doesnt do anything

        # Injector parameters
        self.Header = Header
        self.Payload = Payload


    def toJSON(self):
    
        flowDict = dict()
        
        flowDict["SourceThread"] = OutgoingFlow.SourceThread.ThreadName
        flowDict["TargetThread"] = OutgoingFlow.TargetThread.ThreadName
        flowDict["Bandwidth"] = OutgoingFlow.Bandwidth
        flowDict["StartTime"] = OutgoingFlow.StartTime
        flowDict["StopTime"] = OutgoingFlow.StopTime
        flowDict["Periodic"] = OutgoingFlow.Periodic  # WIP, doesnt do anything
        flowDict["MSGAmount"] = OutgoingFlow.MSGAmount
        flowDict["ControlFlowFlag"] = OutgoingFlow.ControlFlowFlag  # WIP, doesnt do anything

        flowDict["Header"] = OutgoingFlow.Header
        flowDict["Payload"] = OutgoingFlow.Payload
        
        return json.dumps(flowDict, sort_keys=False, indent=4))
    
    
    def __str__(self):
    
        returnString = ""
        
        if self.SourceThread.ParentApplication is not None:
            returnString += self.SourceThread.ParentApplication.AppName + "."
            
        returnString += self.SourceThread.ThreadName
        returnString += " -- " + str(self.Bandwidth) + " MBps -> "
        
        if self.TargetThread.ParentApplication is not None:
            returnString += self.TargetThread.ParentApplication.AppName + "."
            
        returnString += self.TargetThread.ThreadName
        
        return returnString
    

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
    

class Thread:

    def __init__(self, ThreadName):
    
        self.ThreadName = ThreadName
    
        # To be set when Application.addThread(self) is called
        self.ParentApplication = None
        self.ThreadID = None
        
        # To be set when Thread is allocated in parent Platform with setAllocationMap()
        self.BaseNoCPos = None
        self.PEPos = None
        self.StructPos = None

        self.OutgoingFlows = []
        self.OutgoingBandwidth = 0
        
        self.IncomingFlows = []
        self.IncomingBandwidth = 0
        

    def addFlow(self, Flow, autoAddTargetThread = True, autoSetStartStop = False):

        if (isinstance(Flow.SourceThread, Thread) and Flow.SourceThread is self) or Flow.SourceThread is None or str(Flow.SourceThread) == self.ThreadName:
            
            self.OutgoingFlows.append(Flow)
            self.OutgoingBandwidth += Flow.Bandwidth
            
            if not isinstance(Flow.SourceThread, Thread):
                Flow.SourceThread = self
            
            if bool(autoAddTargetThread):
            
                if isinstance(Flow.TargetThread, Thread):
                    Flow.TargetThread.addFlow(Flow)
                    
                else:  # Assumes Flow.TargetThread is of type string from now on
                
                    # Looks for thread in parent application and adds it
                    if self.ParentApplication == None:
                        print("Warning: Auto Adding Flow\n  " + str(Flow) + "\n to Thread " + self.ThreadName + " is impossible, since " 
                              "Flow.TargetThread isnt a reference to a Thread object and ParentApplication hasnt been set, making ThreadName "
                              "lookup in ParentApplication impossible")
                    else:
                    
                        TargetThread = self.ParentApplication.getThreadByName(Flow.TargetThread)
                        
                        if TargetThread is not None:
                            TargetThread.addFlow(Flow)
                        else:
                            print("Error: Given TargetThread.ThreadName " + Flow.TargetThread + " doesnt exist in App " + self.ParentApplication.AppName)
                            exit(1)
                
        elif Flow.TargetThread is self or str(Flow.TargetThread) == self.ThreadName:
            
            Flow.TargetThread = self
            
            self.IncomingFlows.append(Flow)
            self.IncomingBandwidth += Flow.Bandwidth
            
        else:
            
            print("Error: Given Flow unrelated to this Thread")
            print("Thread: " + self.ThreadName)
            print("Flow: " + str(Flow))
            exit(1)
        
        # WIP: Set new Flow's start & stop times based on Thread's default values
        if autoSetStartStop:
            
            if Flow.StartTime != self.StartTime or Flow.StopTime != self.StopTime:
                print("Warning: Overriding Flow <StartTime, StopTime> values <" + str(Flow.StartTime) + ", " + str(Flow.StopTime) + "> with Thread " + self.ThreadName + " 's values <" + str(self.StartTime) + ", " + str(self.StopTime) + ">")
            
            Flow.StartTime = self.StartTime
            Flow.StopTime = self.StopTime
            
            
    def removeFlow(self, Flow):

        if Flow in OutgoingFlows:
            return OutgoingFlows.pop(Flow)
            
        elif Flow in IncomingFlows:
            return IncomingFlows.pop(Flow)
            
        else:
            print("Warning: Flow <" + str(Flow) + "> doesnt exist in Thread " + str(self.ThreadName))
            return None 
            
            
    def getFlow(self, SourceThread = None, TargetThread = None):
        
        # Checks for all null arguments
        if SourceThread is None and TargetThread is None:
            print("Warning: All getFlow() arguments are None, returning full set of Flows (Incoming + Outgoing) for Thread " + str(self.ThreadName))
            return self.IncomingFlows + self.OutgoingFlows
        
        # Gets set of Flows that have self as Target Thread
        if SourceThread is None and TargetThread is self:
            return self.IncomingFlows
            
        # Gets set of Flows that have self as Source Thread
        if SourceThread is self and TargetThread is None:   
            return self.OutgoingFlows
            
        # Gets specific Flow from given SourceThread and TargetThread
        if SourceThread is not None and TargetThread is not None:

            for IncomingFlow in self.IncomingFlows:
                if IncomingFlow.SourceThread is SourceThread and IncomingFlow.TargetThread is TargetThread:
                    return IncomingFlow
            
            for OutgoingFlow in self.OutgoingFlows:
                if OutgoingFlow.SourceThread is SourceThread and OutgoingFlow.TargetThread is TargetThread:
                    return OutgoingFlow
            
            print("Warning: Flow with SourceThread <" + str(SourceThread.ThreadName) + "> and TargetThread <" + str(TargetThread.ThreadName) + "> doesnt exist in Thread <" + str(self.ThreadName) + ">")
            return None  # Returns None as default
            
    
    # Sets a common value for a parameter in all outgoing Flows (this Thread as SourceThread)
    def setFlowParameter(self, Parameter, Value):
    
        if Parameter in Flow.FlowParameters:
            for OutgoingFlow in self.OutgoingFlows:
                setattr(OutgoingFlow, Parameter, Value)
                
        else:
            print("Error: Flow parameter <" + str(Parameter) + "> not recognized. Possible parameters: " + str(Flow.FlowParameters))
            exit(1)
    
    
    def renameThread(self, ThreadName):
        
        if isinstance(ThreadName, str):
            self.ThreadName = ThreadName
        else:
            print("Warning: New given Thread name is not a string, maintaining old Thread name")
                
                
    # WIP: Merges ThreadToMerge into self
    def mergeThread(self, ThreadToMerge):
    
        if ThreadToMerge == self:
            print("Warning: Thread:\n" + str(self) + "\n is equivalent to Thread:\n" + str(ThreadToMerge) + "\n. Aborting mergeThreads().")
            return self
    
        # Appends ThreadToMerge Flows to self's
        self.OutgoingFlows += ThreadToMerge.OutgoingFlows
        
        if ThreadToMerge.ParentApplication is None:
        
            print("Warning: Thread:\n" + str(ThreadToMerge) + "has no ParentApplication. Aborting mergeThreads().")
            return self
        
        # Updates ThreadToMerge references to self
        for ExistingThread in ThreadToMerge.ParentApplication.Threads:
            
            if ExistingThread is ThreadToMerge:
                continue
            
            for IncomingFlow in ExistingThread.IncomingFlows:
                if IncomingFlow.SourceThread == ThreadToMerge:
                    IncomingFlow.SourceThread = self
            
            for OutgoingFlow in ExistingThread.OutgoingFlows:
                if IncomingFlow.TargetThread == ThreadToMerge:
                    IncomingFlow.TargetThread = self
        
        return self
        
        
    def toJSON(self):
    
        threadDict = dict()
        
        threadDict["ThreadName"] = self.ThreadName
        threadDict["ThreadID"] = self.ThreadID
        threadDict["OutgoingFlows"] = [OutgoingFlow.toJSON() for OutgoingFlow in self.OutgoingFlows]
        threadDict["AmountOfOutgoingFlows"] = len(self.OutgoingFlows)
        threadDict["AmountOfIncomingFlows"] = len(self.IncomingFlows)
        
        return json.dumps(threadDict, sort_keys = False, indent = 4)


    def fromJSON(self, JSONString):
        
        # Check if new Thread has a non-default ThreadID assigned
        if Thread.ThreadID is not None:
            print("Warning: Overriding ThreadID <" + str(Application.ThreadID) + "> of Application <" + str(Application.ThreadName) + "> to <" + str(len(self.Threads)) + "> (from JSON)")
            
        # Checks if dict conversion already happened, such as when called hierarchically from Application.fromJSON()
        if isinstance(JSONString, dict):
            JSONDict = JSONString
        else:
            JSONDict = JSON.loads(JSONString)
            
        self.ThreadName = JSONDict["ThreadName"]
        self.ThreadID = int(JSONDict["ThreadID"])
        
        # Add Flows to Thread
        for FlowAsJSON in JSONDict["OutgoingFlows"]:
            
            SourceThread = self.getThread(ThreadName = FlowAsJSON["SourceThread"])
            if SourceThread is not self:
                print("Error: Mismatching SourceThread while adding Flow from JSON")
                exit(1)
                
            TargetThread = self.getThread(ThreadName = FlowAsJSON["TargetThread"])
            
            # Ignores Periodic and ControlFlowFlag attributes, currently unsupported
            self.addFlow(Flow(SourceThread = SourceThread, TargetThread = TargetThread, Bandwidth = FlowAsJSON["Bandwidth"], StartTime = FlowAsJSON["StartTime"], StopTime = FlowAsJSON["StopTime"], MSGAmount = FlowAsJSON["MSGAmount"], Header = FlowAsJSON["Header"], Payload = FlowAsJSON["Payload"]))
        
    
    def __str__(self):

        returnString = ""
        
        returnString += ("\t " + self.ThreadName + " Targets\n")
        for OutgoingFlow in self.OutgoingFlows:
            returnString += (str(OutgoingFlow) + "\n")
            
        returnString += ("\n\t " + self.ThreadName + " Sources\n")
        for IncomingFlow in self.IncomingFlows:
            returnString += (str(IncomingFlow) + "\n")
            
        returnString += ("\n" + self.ThreadName + " Total Outgoing Bandwidth: " + str(self.OutgoingBandwidth))
        returnString += ("\n" + self.ThreadName + " Total Incoming Bandwidth: " + str(self.IncomingBandwidth))
        returnString += ("\n PEPos: " + str(self.PEPos) + "\n")
        
        return returnString
        
    
    def __eq__(self, other):
    
        # Directly compares two Thread objects
        if self is other:
            return True
            
        # Thread objects may be different but equivalent, such as when comparing 2 Threads in 2 different Workloads built from the same JSON file
        elif self.OutgoingFlows == other.OutgoingFlows and self.IncomingFlows == other.IncomingFlows:
            return True
            
        else:
            return False
            
    
class Application:

    def __init__(self, AppName = "DefaultAppName", StartTime = 0, StopTime = 0):
    
        self.AppName = str(AppName)
        
        self.Threads = []
        
        # To be set when Workload.addApplication(self) is called
        self.AppID = None
        self.ParentWorkload = None
        
        self.StartTime = StartTime
        self.StopTime = StopTime
        
        
    @property
    def TotalBandwidth(self):
        
        TotalBandwidth = 0
        
        for Thread in self.Threads:
            TotalBandwidth += Thread.OutgoingBandwidth
            
        return TotalBandwidth
        
        
    @property
    def AverageBandwidth(self):
    
        return self.TotalBandwidth / len(self.Threads)
        
        
    @property
    def ThreadsByName(self):
    
        ThreadsByNameDict = dict()
        
        for Thread in self.Threads:
            ThreadsByNameDict[str(Thread.ThreadName)] = Thread
            
        return ThreadsByNameDict
        
        
    @property
    def ThreadsByID(self):
    
        ThreadsByID = [None] * len(self.Threads)
        
        for ThreadInApp in self.Threads:
            ThreadsByID[ThreadInApp.ThreadID] = ThreadInApp
            
        return ThreadsByID
        

    def addThread(self, Thread, autoSetStartStop = True):
        
        # Check if new Thread has a non-default ThreadID assigned
        if Thread.ThreadID is not None and Thread.ThreadID != len(self.Threads):
            print("Warning: Overriding ThreadID <" + str(Application.ThreadID) + "> of Application <" + str(Application.ThreadName) + "> to <" + str(len(self.Threads)) + ">")
            
        # If in this App there already is a Thread with given Thread's name, rename it, else, add it to App
        if Thread.ThreadName in self.ThreadsByName.keys():
        
            newName = Thread.ThreadName + "_A"
            
            while(True):
            
                if newName in self.ThreadsByName.keys():
                    
                    # Increments last char on "newName" and tries to add Thread to App again
                    #newName = newName[:-1] + chr(int(newName[-1:]) + 1)
                    newName = newName[:-1] + chr(ord(newName[-1:]) + 1)
                
                # Renames thread and adds it to App
                else:
                
                    Thread.renameThread(newName)
                
                    Thread.ThreadID = len(self.Threads)
                    Thread.ParentApplication = self
                    self.Threads.append(Thread)
                    
                    break
            
        else:
        
            Thread.ThreadID = len(self.Threads)
            Thread.ParentApplication = self
            self.Threads.append(Thread)
        
        # TODO: Set all StartTime and StopTime for all Flows of added Thread 
        #if autoSetStartStop:
            
            #if Thread.StartTime != self.StartTime or Thread.StopTime != self.StopTime:
                #print("Warning: Overriding Thread <StartTime, StopTime> values with App " + self.AppName + " 's values <" + str(self.StartTime) + ", " + str(self.StopTime) + ">")
            
            #Thread.StartTime = self.StartTime
            #Thread.StopTime = self.StopTime
            
            
    # Remove a given Thread from this Application
    def removeThread(self, Thread):
        
        if Thread in self.Threads:
            
            for ExistingThread in self.Threads:
            
                for OutgoingFlow in ExistingThread.OutgoingFlows:
                    if OutgoingFlow.SourceThread is Thread or OutgoingFlow.TargetThread is Thread:
                        ExistingThread.OutgoingFlows.pop(OutgoingFlow)
                        
                for IncomingFlow in ExistingThread.IncomingFlows:
                    if IncomingFlow.SourceThread is Thread or IncomingFlow.TargetThread is Thread:
                        ExistingThread.IncomingFlows.pop(IncomingFlow)
            
            return self.Threads.pop(Thread)
            
        else:
        
            print("Warning: Given Thread <" + str(Thread.ThreadName) + "> doesnt exist in App " + str(self.AppName))
            return None
            
    
    # Sets a new AppName
    def renameApplication(self, AppName):
    
        try:
            if isinstance(AppName, str):
                self.AppName = AppName
            else:
                print("New given Application name is not a string, maintaining old Application name")
                
        except NameError:
        
            if isinstance(AppName, basestring):
                self.AppName = AppName
            else:
                print("New given Application name is not a string, maintaining old Application name")
                
                
    # Sets a common value for a parameter in all outgoing Flows in all Threads
    def setFlowParameter(self, Parameter, Value):
    
        for ThreadInApp in self.Threads:
            ThreadInApp.setFlowParameter(Parameter, Value)
            
            
    # Returns a Thread object associated with a given ThreadName or ThreadID. If there is no ThreadName or ThreadID associated, returns None
    def getThread(self, ThreadName = None, ThreadID = None):  # TODO: Check if ThreadName is a string and throw error if not so
    
        if ThreadName is None and ThreadID is None:
            print("Warning: Both arguments <ThreadName> and <ThreadID> were not given. getThread() does nothing.")
            return None
        
        elif ThreadName is not None and ThreadID is None:
            
            ReturnThread = self.ThreadsByName.get(ThreadName)
            
            if ReturnThread is None:
                print("Warning: ThreadName <" + str(ThreadName) + "> doesnt correspond to any Thread in App <" + str(self.AppName) + ">, returning None")
                
            return ReturnThread
            
        elif ThreadName is None and ThreadID is not None:
        
            #ReturnThread = self.ThreadsByID.get(ThreadID)
            ReturnThread = self.ThreadsByID[ThreadID]

            if ReturnThread is None:
                print("Warning: ThreadID <" + str(ThreadID) + "> doesnt correspond to any Thread in App <" + str(self.AppName) + ">, returning None")
                
            return ReturnThread
            
        elif ThreadName is not None and ThreadID is not None:
        
            ThreadByName = self.ThreadsByName.get(ThreadName)
            ThreadByID = self.ThreadsByName.get(ThreadByID)
            
            if ThreadByName is ThreadByID:
                return ThreadByID
                
            else:
                print("Error: <ThreadID: " + str(ThreadID) + "> and <ThreadName: " + str(ThreadName) + "> correspond to different Threads")
                exit(1)
                    
    
    def toJSON(self, SaveToFile = False, FileName = None):
    
        appDict = dict()
        
        appDict["AppName"] = self.AppName
        appDict["StartTime"] = self.StartTime
        appDict["StopTime"] = self.StopTime
        appDict["AmountOfThreads"] = len(self.Threads)
        appDict["Threads"] = [ThreadInApp.toJSON() for ThreadInApp in self.Threads]
        
        #print(appDict)
        
        # Converts appDict to a JSON-formatted string (sort_keys must be False so ThreadIDs are the same in original and reconstructed-from-JSON objects)
        JSONString = JSON.dumps(appDict, sort_keys=False, indent=4)
        
        if bool(SaveToFile):
            
            if FileName is not None:
                JSONFile = open(str(FileName) + ".json", "w")
            else:
                JSONFile = open(self.AppName + ".json", "w")
                
            JSONFile.write(JSONString)
            JSONFile.close()

        return JSONString
        

    def fromJSON(self, JSONString):
    
        # To be set when Workload.addApplication(self) is called
        self.ParentWorkload = None
        
        # Check if new Application has a non-default AppID assigned
        if self.AppID is not None:
            print("Warning: Overriding AppID <" + str(Application.AppID) + "> of Application <" + str(Application.AppName) + "> to <" + JSONDict["AppID"] + "> (from JSON)")
        
        # Checks if dict conversion already happened, such as when called hierarchically from Workload.fromJSON()
        if isinstance(JSONString, dict):
            JSONDict = JSONString
        else:
            JSONDict = JSON.loads(JSONString)
        
        self.AppName = JSONDict["AppName"]
        self.AppID = int(JSONDict["AppID"]) 
        self.StartTime = JSONDict["StartTime"]
        self.StopTime = JSONDict["StopTime"]
        
        self.Threads = []
        for ThreadAsJSON in JSONDict["Threads"]:
            newThread = Thread()
            self.addThread(newThread)
            newThread.fromJSON(ThreadAsJSON)
            
        return self


    def __str__(self):
    
        returnString = ""
        
        returnString += ("Parent Workload: " + str(self.ParentWorkload.WorkloadName) + "\n")
        returnString += ("Amount of Threads: " + str(len(self.Threads)) + "\n")
        returnString += ("Total Bandwidth: " + str(self.TotalBandwidth) + "\n")
        
        try:
            returnString += ("Average Bandwidth: " + str(self.TotalBandwidth / len(self.Threads)) + "\n")
        except ZeroDivisionError:
            returnString += ("Average Bandwidth: 0\n")
            pass
        
        return returnString


    def __eq__(self, other):

        return NotImplemented
        
        
class Workload:

    def __init__(self, WorkloadName = "HibridaWorkload"):
    
        self.WorkloadName = str(WorkloadName)
        
        self.Applications = []
        
        # To be set when Platform.setWorkload(self) is called
        self.ParentPlatform = None
        
        
    @property
    def TotalBandwidth(self):
    
        totalBandwidth = 0
        
        for App in self.Applications:
            totalBandwidth += App.TotalBandwidth
            
        return totalBandwidth
        
        
    @property
    def AverageBandwidth(self):
    
        amountOfThreads = 0
        
        for App in self.Applications:
            amountOfThreads += len(App.Threads)
            
        try:
            return self.TotalBandwidth / amountOfThreads
        except ZeroDivisionError:
            return 0
        
        
    @property
    def ApplicationsByName(self):
    
        ApplicationsByNameDict = dict()
        
        for App in self.Applications:
            ApplicationsByNameDict[str(App.AppName)] = App
            
        return ApplicationsByNameDict
    
    
    @property
    def ApplicationsByID(self):
    
        applicationsByID = [None] * len(self.Applications)

        for App in self.Applications:  # TODO: List comprehension maybe?
            applicationsByID[App.AppID] = App
        
        return applicationsByID
        
        
    def addApplication(self, Application):
        
        # Check if new Application has a non-default AppID assigned
        if Application.AppID is not None and Application.AppID != len(self.Applications):
            print("Warning: Overriding AppID <" + str(Application.AppID) + "> of Application <" + str(Application.AppName) + "> to <" + str(len(self.Applications)) + ">")
        
        # If in this Workload there already is an App with given App's name, rename it, else, add it to Workload
        if Application.AppName in self.ApplicationsByName.keys():
        
            newName = Application.AppName + "_A"
            
            while(True):
            
                if newName in self.ApplicationsByName.keys():
                    
                    # Increments last char on "newName" and tries to add Thread to App again
                    #newName = newName[:-1] + chr(int(newName[-1:]) + 1)
                    newName = newName[:-1] + chr(ord(newName[-1:]) + 1)
                
                # Renames thread and adds it to App
                else:
                
                    Application.renameApplication(newName)
                
                    Application.AppID = len(self.Applications)
                    #Application.ParentApplication = self
                    Application.ParentWorkload = self
                    self.Applications.append(Application)
                    
                    break
            
        else:
        
            Application.AppID = len(self.Applications)
            #Application.ParentApplication = self
            Application.ParentWorkload = self
            self.Applications.append(Application)
            
    
    def removeApplication(self, Application):
    
        if Application in self.Applications:
            return self.Applications.pop(Application)
        else:
            print("Warning: Given App <" + str(Application.AppName) + "> doesnt exist in Workload " + str(self.WorkloadName))
            return None
    
    
    def getApplication(self, AppName = None, AppID = None):
    
        if AppName is None and AppID is None:
            print("Warning: Both <AppName> and <AppID> were not given. getApplication() does nothing")
            return None
        
        elif AppName is not None and AppID is None:
            
            AppByName = self.ApplicationsByName.get(AppName)
            
            if AppByName is None:
                print("Warning: AppName <" + str(ThreadName) + "> doesnt correspond to any Application in Workload <" + str(self.WorkloadName) + ">, returning None")
            
            return AppByName
            
        elif AppName is None and AppID is not None:
        
            #AppByID = self.ApplicationsByID.get(AppID)
            AppByID = self.ApplicationsByID[AppID]
            
            if AppByID is None:
                print("Warning: AppID <" + str(ThreadName) + "> doesnt correspond to any Application in Workload <" + str(self.WorkloadName) + ">, returning None")
            
            return AppByID
            
        elif AppName is not None and AppID is not None:
        
            AppByName = self.ApplicationsByName.get(AppName)
            AppByID = self.ApplicationsByID.[AppID]
            
            if AppByName is not AppByID:
                print("Error: <AppID: " + str(ThreadID) + "> and <AppName: " + str(ThreadName) + "> correspond to different Applications")
                exit(1)
            
            return AppByName
            
        
    # TODO: Test for more arg combinations and display warning if they dont make sense (e.g AppName and AppID)
    def getThread(self, AppName = None, ThreadName = None, AppID = None, ThreadID = None):

        # No args given
        if AppName is None and ThreadName is None and AppID is None and ThreadID is None:
            print("Warning: Neither <AppName>, <ThreadName>, <AppID> and <ThreadID> were not given. getThread() does nothing")
            return None

        # Looks by App and Thread name
        elif AppName is not None and ThreadName is not None and AppID is None and ThreadID is None:

            App = self.getApplication(AppName = AppName)

            if App is None:
                return None

            return App.getThread(ThreadName = ThreadName)

        # Looks only by given ThreadName with AppName and ThreadName separated by "."
        elif AppName is None and ThreadName is not None and AppID is None and ThreadID is None:
            
            try:
                App, Thrd = ThreadName.split(".", 1)
            except ValueError:
                print("Warning: No \".\" char found on given ThreadName string <" + str(ThreadName) + ">. Include Application name on AllocMap list.")
                exit(1)

            return self.getThread(AppName = App, ThreadName = Thrd)

        # Looks by App and Thread IDs
        elif AppName is None and ThreadName is None and AppID is not None and ThreadID is not None:

            App = self.getApplication(AppID = AppID)

            if App is None:
                return None

            return App.getThread(ThreadID = ThreadID)

        # Looks only by given ThreadID with AppID and ThreadID separated by "."
        elif AppName is None and ThreadName is None and AppID is None and ThreadID is not None:
            
            try:
                App, Thrd = str(ThreadID).split(".", 1)
            except ValueError:
                print("Warning: No \".\" char found on given ThreadID string <" + str(ThreadName) + ">. Include Application ID on AllocMap list.")
                exit(1)

            return self.getThread(AppID = App, ThreadID = Thrd)

        else:
            NotImplementedError 


    def toJSON(self, SaveToFile = False, FileName = None):
    
        workloadDict = dict()
        
        workloadDict["WorkloadName"] = self.WorkloadName
        workloadDict["AmountOfApplications"] = len(self.Applications)
        workloadDict["Applications"] = [AppInWorkload.toJSON() for AppInWorkload in self.Applications]
            
        # Converts workloadDict to a JSON-formatted string (sort_keys must be False so AppIDs are the same in original and reconstructed-from-JSON objects)
        JSONString = JSON.dumps(workloadDict, sort_keys = False, indent = 4)
        
        if bool(SaveToFile):
        
            if FileName is not None:
                JSONFile = open(FileName + ".json", "w")
            else:
                JSONFile = open(self.WorkloadName + ".json", "w")
                
            JSONFile.write(JSONString)
            JSONFile.close()
            
        return JSONString
    
    
    def fromJSON(self, JSONString):
    
        # To be set when Platform.setWorkload(self) is called
        self.ParentPlatform = None
        
        JSONDict = JSON.loads(JSONString)
        
        self.WorkloadName = JSONDict["WorkloadName"]
        
        # Add Applications and sort them by their AppID values. 
        self.Applications = []
        for AppAsJSON in JSONDict["Applications"]:
            newApp = Application()
            self.addApplication(newApp)
            newApp.fromJSON(AppAsJSON)

        return self

    
    def __str__(self):
    
        returnString = ""
        
        returnString += "\tWorkload " + str(self.WorkloadName) + ":\n"
        returnString += "Amount of Applications: " + str(len(self.Applications)) + "\n"
        returnString += "Total Bandwidth: " + str(self.TotalBandwidth) + "\n"
        returnString += "Average Bandwidth: " + str(self.AverageBandwidth) + "\n"

        return returnString
        
        