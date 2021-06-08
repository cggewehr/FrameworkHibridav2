
import copy
import json
from Flows import *

class Thread:

    def __init__(self, ThreadName = "DefaultThreadName"):
    
        self.ThreadName = ThreadName
    
        # To be set when Application.addThread(self) is called
        self.ParentApplication = None
        self.ThreadID = None
        
        # To be set when Thread is allocated in parent Platform with setAllocationMap()
        self.BaseNoCPos = None
        self.PEPos = None
        self.StructPos = None

        self.OutgoingFlows = []
        #self.OutgoingBandwidth = 0
        
        self.IncomingFlows = []
        #self.IncomingBandwidth = 0
        

    @property 
    def OutgoingBandwidth(self):

        outgoingBandwidth = 0
        for OutgoingFlow in self.OutgoingFlows:
            if OutgoingFlow.FlowType == "CBR":
                outgoingBandwidth += OutgoingFlow.Bandwidth
        return outgoingBandwidth


    @property 
    def IncomingBandwidth(self):

        incomingBandwidth = 0
        for IncomingFlow in self.IncomingFlows:
            if IncomingFlow.FlowType == "CBR":
                incomingBandwidth += IncomingFlow.Bandwidth
        return incomingBandwidth


    def addFlow(self, Flow, autoAddTargetThread = True, autoSetStartStop = False):
        
        #print(Flow.SourceThread)
        #print(Flow)
        if (isinstance(Flow.SourceThread, Thread) and Flow.SourceThread is self) or Flow.SourceThread is None or (isinstance(Flow.SourceThread, str) and self.ThreadName == Flow.SourceThread):
        #if (isinstance(Flow.SourceThread, Thread) and Flow.SourceThread is self) or Flow.SourceThread is None:
            
            self.OutgoingFlows.append(Flow)
            #self.OutgoingBandwidth += Flow.Bandwidth
            
            if not isinstance(Flow.SourceThread, Thread):
                Flow.SourceThread = self
            
            if autoAddTargetThread:
            
                if isinstance(Flow.TargetThread, Thread):
                    Flow.TargetThread.addFlow(Flow)
                    
                else:  # Assumes Flow.TargetThread is of type string from now on
                
                    # Looks for thread in parent application and adds it
                    if self.ParentApplication == None:
                        print("Warning: Can't auto add Flow <" + str(Flow) + "> to Thread <" + self.ThreadName + ">, since " 
                              "Flow.TargetThread isn't a reference to a Thread object and ParentApplication hasn't been set, making ThreadName "
                              "lookup in ParentApplication impossible")
                    else:
                    
                        #print(Flow.TargetThread)
                        #print(Flow.SourceThread)
                        TargetThread = self.ParentApplication.getThread(ThreadName = Flow.TargetThread)
                        
                        if TargetThread is not None:
                            TargetThread.addFlow(Flow)
                        else:
                            print("Error: Given TargetThread.ThreadName <" + str(Flow.TargetThread) + "> doesnt exist in Application <" + str(self.ParentApplication.AppName) + ">")
                            exit(1)
                
        #elif Flow.TargetThread is self or str(Flow.TargetThread) == self.ThreadName:
        elif Flow.TargetThread is self or (isinstance(Flow.TargetThread, str) and self.ThreadName == Flow.TargetThread):
            
            Flow.TargetThread = self
            
            self.IncomingFlows.append(Flow)
            #self.IncomingBandwidth += Flow.Bandwidth
            
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
            return OutgoingFlows.remove(Flow)
            
        elif Flow in IncomingFlows:
            return IncomingFlows.remove(Flow)
            
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
    
        if Parameter in Flow.BaseFlowParameters:
            for OutgoingFlow in self.OutgoingFlows:
                setattr(OutgoingFlow, Parameter, Value)
                
        else:
            print("Error: Flow parameter <" + str(Parameter) + "> not recognized. Possible parameters: " + str(Flow.BaseFlowParameters))
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
        
        
    def toSerializableDict(self):

        threadDict = dict()
        
        threadDict["ThreadName"] = self.ThreadName
        threadDict["ThreadID"] = self.ThreadID
        #threadDict["OutgoingFlows"] = [OutgoingFlow.toJSON() for OutgoingFlow in self.OutgoingFlows]
        threadDict["OutgoingFlows"] = [OutgoingFlow.toSerializableDict() for OutgoingFlow in self.OutgoingFlows]
        threadDict["AmountOfOutgoingFlows"] = len(self.OutgoingFlows)
        threadDict["AmountOfIncomingFlows"] = len(self.IncomingFlows)

        return threadDict


    def toJSON(self):
        
        return json.dumps(toSerializableDict(), sort_keys = False, indent = 4)


    def fromJSON(self, JSONString):
        
        # Check if new Thread has a non-default ThreadID assigned
        if self.ThreadID is not None:
            print("Warning: Overriding ThreadID <" + str(self.ThreadID) + "> of Thread <" + str(self.ThreadName) + "> to <" + str(len(self.ParentApplication.Threads)) + "> (from JSON)")
            
        # Checks if dict conversion already happened, such as when called hierarchically from Application.fromJSON()
        if isinstance(JSONString, dict):
            JSONDict = JSONString
        else:
            JSONDict = JSON.loads(JSONString)
            
        self.ThreadName = JSONDict["ThreadName"]
        self.ThreadID = int(JSONDict["ThreadID"])
        
        # Add Flows to Thread
        self.OutgoingFlows = []
        self.IncomingFlows = []
        for FlowAsJSON in JSONDict["OutgoingFlows"]:
            self.addFlow(Flow().fromJSON(FlowAsJSON), autoAddTargetThread = False)

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
                    
    def toSerializableDict(self):

        appDict = dict()
        
        appDict["AppName"] = self.AppName
        appDict["AppID"] = self.AppID
        appDict["StartTime"] = self.StartTime
        appDict["StopTime"] = self.StopTime
        appDict["AmountOfThreads"] = len(self.Threads)
        #appDict["Threads"] = [ThreadInApp.toJSON() for ThreadInApp in self.Threads]
        appDict["Threads"] = [ThreadInApp.toSerializableDict() for ThreadInApp in self.Threads]

        return appDict


    def toJSON(self, SaveToFile = False, FileName = None):
        
        # Converts appDict to a JSON-formatted string (sort_keys must be False so ThreadIDs are the same in original and reconstructed-from-JSON objects)
        JSONString = json.dumps(self.toSerializableDict(), sort_keys=False, indent=4)
        
        if bool(SaveToFile):
            
            if FileName is not None:
                JSONFile = open(str(FileName) + ".json", "w")
            else:
                JSONFile = open(self.AppName + ".json", "w")
                
            JSONFile.write(JSONString)
            JSONFile.close()

        return JSONString
        

    def fromJSON(self, JSONString):

        # Checks if dict conversion already happened, such as when called hierarchically from Workload.fromJSON()
        if isinstance(JSONString, dict):
            JSONDict = JSONString
        else:
            JSONDict = json.loads(JSONString)
        
        # Check if new Application has a non-default AppID assigned
        if self.AppID is not None:
            print("Warning: Overriding AppID <" + str(Application.AppID) + "> of Application <" + str(Application.AppName) + "> to <" + JSONDict["AppID"] + "> (from JSON)")
        
        #print(JSONDict["AppName"])
        if JSONDict["AppID"] is not None:
            self.AppID = int(JSONDict["AppID"])
        else:
            self.AppID = None

        # To be set when Workload.addApplication(self) is called
        self.ParentWorkload = None

        self.AppName = JSONDict["AppName"]
        self.StartTime = JSONDict["StartTime"]
        self.StopTime = JSONDict["StopTime"]
        
        self.Threads = []
        for ThreadAsJSON in JSONDict["Threads"]:
            self.addThread(Thread().fromJSON(ThreadAsJSON))
            
        return self


    # Replace SourceThread, TargetThread names with reference to Thread objects in Flows for each Application
    def _resolveNames(self):

        for ThreadInApp in self.Threads:

            for OutgoingFlow in ThreadInApp.OutgoingFlows:

                if not isinstance(OutgoingFlow.SourceThread, Thread):

                    SourceThreadRef = self.getThread(ThreadName = OutgoingFlow.SourceThread)

                    if SourceThreadRef is None:
                        print("Error: SourceThread name lookup for Thread name <" + str(OutgoingFlow.SourceThread) + "> failed for Flow <" + str(OutgoingFlow))
                        exit(1)
                    else:
                        OutgoingFlow.SourceThread = SourceThreadRef
                    
                if not isinstance(OutgoingFlow.TargetThread, Thread):

                    TargetThreadRef = self.getThread(ThreadName = OutgoingFlow.TargetThread)

                    if TargetThreadRef is None:
                        print("Error: SourceThread name lookup for Thread name <" + str(OutgoingFlow.TargetThread) + "> failed for Flow <" + str(OutgoingFlow))
                        exit(1)
                    else:
                        
                        # Add Flow to IncomingFlows list in TargetThread
                        TargetThreadRef.addFlow(OutgoingFlow, autoAddTargetThread = True)


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
            AppByID = self.ApplicationsByID[AppID]
            
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
        #workloadDict["Applications"] = [AppInWorkload.toJSON() for AppInWorkload in self.Applications]
        workloadDict["Applications"] = [AppInWorkload.toSerializableDict() for AppInWorkload in self.Applications]
            
        # Converts workloadDict to a JSON-formatted string (sort_keys must be False so AppIDs are the same in original and reconstructed-from-JSON objects)
        JSONString = json.dumps(workloadDict, sort_keys = False, indent = 4)
        
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
        
        JSONDict = json.loads(JSONString)
        
        self.WorkloadName = JSONDict["WorkloadName"]
        
        # Add Applications and sort them by their AppID values. 
        self.Applications = []
        for AppAsJSON in JSONDict["Applications"]:
            self.addApplication(Application().fromJSON(AppAsJSON))
        
        # Replace SourceThread, TargetThread names with reference to Thread objects in Flows for each Application
        self._resolveNames()

        return self

    
    # Replace SourceThread, TargetThread names with reference to Thread objects in Flows for each Application
    def _resolveNames(self):

        for App in self.Applications:
            App._resolveNames()


    def __str__(self):
    
        returnString = ""
        
        returnString += "\tWorkload " + str(self.WorkloadName) + ":\n"
        returnString += "Amount of Applications: " + str(len(self.Applications)) + "\n"
        returnString += "Total Bandwidth: " + str(self.TotalBandwidth) + "\n"
        returnString += "Average Bandwidth: " + str(self.AverageBandwidth) + "\n"

        return returnString
        
        
