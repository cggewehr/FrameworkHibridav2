
import copy
import json as JSON

# TODO: Make Unrelated flow exception
# TODO: Merge identical Flows when they are added to a Thread
# TODO: Extend Flow class to support many types of flows (not only CBR), such as Markov chains and Pareto chains

class Flow:

    def __init__(self, Bandwidth, TargetThread, SourceThread = None, FlowType = "CBR", StartTime = 0, StopTime = -1, Periodic = False, MSGAmount = 0, ControlFlowFlag = False):

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
           
        self.Bandwidth = Bandwidth  # In MBps
        self.FlowType = FlowType  # Only CBR type currently supported
        
        # Dynamic parameters
        self.StartTime = StartTime
        self.StopTime = StopTime
        self.Periodic = Periodic
        self.MSGAmount = MSGAmount
        self.ControlFlowFlag = ControlFlowFlag


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
            
            print("Warning : Flow with SourceThread <" + str(SourceThread.ThreadName) + "> and TargetThread <" + str(TargetThread.ThreadName) + "> doesnt exist in Thread <" + str(self.ThreadName) + ">")
            return None  # Returns None as default
            
            
    def renameThread(self, ThreadName):
        
        try:
            if isinstance(ThreadName, str):
                self.ThreadName = ThreadName
            else:
                print("Warning: New given Thread name is not a string, maintaining old Thread name")
                
        except NameError:
            if isinstance(ThreadName, basestring):
                self.ThreadName = ThreadName
            else:
                print("Warning: New given Thread name is not a string, maintaining old Thread name")
                
                
    # Merges ThreadToMerge into self
    def mergeThread(self, ThreadToMerge):
    
        if ThreadToMerge == self:
            print("Warning: Thread:\n" + str(self) + "\n is equivalent to Thread:\n" + str(ThreadToMerge) + "\n. Aborting mergeThreads().")
            return self
    
        # Appends ThreadToMerge Flows to self's
        self.OutgoingFlows += ThreadToMerge.OutgoingFlows
        
        if ThreadA.ParentApplication is None:
        
            print("Warning: Thread:\n" + str(ThreadA) + "has no ParentApplication. Aborting mergeThreads().")
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

    def __init__(self, AppName = "DefaultAppName", StartTime = 0, StopTime = -1):
    
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
        
        for ThreadInApp in enumerate(self.Threads):
            ThreadsByID[ThreadInApp.ThreadID] = ThreadInApp
            
        return ThreadsByID
        

    def addThread(self, Thread, autoSetStartStop = True):
        
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
        
            if isinstance(ThreadName, basestring):
                self.AppName = AppName
            else:
                print("New given Application name is not a string, maintaining old Application name")
                
    
    # Returns a Thread object associated with a given ThreadName or ThreadID. If there is no ThreadName or ThreadID associated, returns None
    def getThread(self, ThreadName = None, ThreadID = None):  # TODO: Check if ThreadName is a string and throw error if not so
    
        if ThreadName is None and ThreadID is None:
            print("Warning: Both arguments <ThreadName> and <ThreadID> were not given. getThread() does nothing.")
            return None
        
        elif ThreadName is not None and ThreadID is None:
            
            ReturnThread = self.ThreadsByName.get(ThreadName)
            
            if ReturnThread is None:
                print("Warning: ThreadName <" + str(ThreadName) + "> doesnt correspond to any Thread in App <" + str(self.AppName) + ">, returning None")
                
            return self.ThreadsByName.get(ThreadName)
            
        elif ThreadName is None and ThreadID is not None:
        
            ReturnThread = self.ThreadsByID.get(ThreadID)

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
        
        for Thread in self.Threads:
        
            threadDict = dict()
            
            #threadDict["ThreadName"] = Thread.ThreadName
            
            # Write to JSON only flows that have this Thread as source. Flows that have this Thread as target will update this Thread when they are added in their source Thread
            OutgoingFlows = []
            for OutgoingFlow in Thread.OutgoingFlows:
                
                flowDict = dict()
                
                flowDict["SourceThread"] = OutgoingFlow.SourceThread.ThreadName
                flowDict["TargetThread"] = OutgoingFlow.TargetThread.ThreadName
                flowDict["Bandwidth"] = OutgoingFlow.Bandwidth
                flowDict["StartTime"] = OutgoingFlow.StartTime
                flowDict["StopTime"] = OutgoingFlow.StopTime
                flowDict["Periodic"] = OutgoingFlow.Periodic
                flowDict["MSGAmount"] = OutgoingFlow.MSGAmount
                flowDict["ControlFlowFlag"] = OutgoingFlow.ControlFlowFlag
                
                OutgoingFlows.append(flowDict)

            threadDict["Flows"] = OutgoingFlows
            
            appDict[Thread.ThreadName] = threadDict
            
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
    
        JSONDict = JSON.loads(JSONString)
        
        self.AppName = JSONDict["AppName"]
        self.StartTime = JSONDict["StartTime"]
        self.StopTime = JSONDict["StopTime"]
        
        self.Threads = []
        #self.ThreadsByName = dict()
        
        # To be set when Workload.addApplication(self) is called
        self.AppID = None
        self.ParentWorkload = None
        
        # Remove keys that arent associated with thread names
        JSONDict.pop("AppName", None)
        JSONDict.pop("StartTime", None)
        JSONDict.pop("StopTime", None)
        
        # Create Threads
        for ThreadName in JSONDict:
            self.addThread(Thread(ThreadName))
            
        # Add Flows to Threads
        for ThreadInApp in self.Threads:
        
            # Creates Flow with SourceThread and TargetThread as strings
            for FlowInThread in JSONDict[ThreadInApp.ThreadName]["Flows"]:
            
                #ThreadInApp.addFlow(Flow(Bandwidth = FlowInThread["Bandwidth"], SourceThread = FlowInThread["SourceThread"], TargetThread = FlowInThread["TargetThread"]))

                SourceThread = self.getThread(ThreadName = FlowInThread["SourceThread"])
                TargetThread = self.getThread(ThreadName = FlowInThread["TargetThread"])
                ThreadInApp.addFlow(Flow(Bandwidth = FlowInThread["Bandwidth"], SourceThread = SourceThread, TargetThread = TargetThread, StartTime = FlowInThread["StartTime"], StopTime = FlowInThread["StopTime"], Periodic = FlowInThread["Periodic"], MSGAmount = FlowInThread["MSGAmount"], ControlFlowFlag = FlowInThread["ControlFlowFlag"]))


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
        
            AppByID = self.ApplicationsByID.get(AppID)
            
            if AppByID is None:
                print("Warning: AppID <" + str(ThreadName) + "> doesnt correspond to any Application in Workload <" + str(self.WorkloadName) + ">, returning None")
            
            return AppByID
            
        elif AppName is not None and AppID is not None:
        
            AppByName = self.ApplicationsByName.get(AppName)
            AppByID = self.ApplicationsByID.get(AppID)
            
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

            App, Thrd = ThreadName.split(".", 1)

            return self.getThread(AppName = App, ThreadName = Thrd)

        # Looks by App and Thread IDs
        elif AppName is None and ThreadName is None and AppID is not None and ThreadID is not None:

            App = self.getApplication(AppID = AppID)

            if App is None:
                return None

            return App.getThread(ThreadID = ThreadID)

        # Looks only by given ThreadID with AppID and ThreadID separated by "."
        elif AppName is None and ThreadName is None and AppID is None and ThreadID is not None:

            App, Thrd = str(ThreadID).split(".", 1)

            return self.getThread(AppID = App, ThreadID = Thrd)

        else:

            NotImplementedError 


    def toJSON(self, SaveToFile = False, FileName = None):
    
        workloadDict = dict()
        
        workloadDict["WorkloadName"] = self.WorkloadName
        
        for App in self.Applications:
            workloadDict[App.AppName] = JSON.loads(App.toJSON())
            
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
    
        JSONDict = JSON.loads(JSONString)
        
        self.WorkloadName = JSONDict["WorkloadName"]
        
        self.Applications = []
        #self.ApplicationsByName = dict()
        
        # To be set when Platform.setWorkload(self) is called
        self.ParentPlatform = None

        # Pop keys unrelated to App names
        JSONDict.pop("WorkloadName")
        
        for AppName in JSONDict:
            #self.addApplication(Application(AppName = AppName).fromJSON(JSON.dumps(JSONDict[AppName])))
            newApp = Application(AppName = AppName)
            appJSONString = JSON.dumps(JSONDict[AppName], sort_keys=False, indent=4)
            newApp.fromJSON(appJSONString)
            self.addApplication(newApp)

    
    def __str__(self):
    
        returnString = ""
        
        returnString += "\tWorkload " + str(self.WorkloadName) + ":\n"
        returnString += "Amount of Applications: " + str(len(self.Applications)) + "\n"
        returnString += "Total Bandwidth: " + str(self.TotalBandwidth) + "\n"
        returnString += "Average Bandwidth: " + str(self.AverageBandwidth) + "\n"

        return returnString
        
        