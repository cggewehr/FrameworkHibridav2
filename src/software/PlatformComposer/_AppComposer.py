
import copy
import json as JSON

# TODO: Make Unrelated flow exception
# TODO: Merge identical Flows when they are added to a Thread
# TODO: Extende Flow class to support many types of flows (not only CBR), such as Markov chains and Pareto chains

class Flow:

    def __init__(self, Bandwidth, TargetThread, SourceThread = None, FlowType = "CBR"):

        self.FlowType = FlowType
        self.SourceThread = SourceThread  # Thread object
        self.TargetThread = TargetThread  # Thread object
        self.Bandwidth = Bandwidth  # In MBps


    def __str__(self):
        
        try:
            return (str(self.SourceThread.ParentApplication.AppName) + "." + self.SourceThread.ThreadName + " --" + str(self.Bandwidth) + "MBps-> " + str(self.TargetThread.ParentApplication.AppName) + "." + self.TargetThread.ThreadName)
        except AttributeError:
            return ""
    
    
    def __eq__(self, other):
    
        if self.SourceThread is other.SourceThread and self.TargetThread is other.TargetThread and self.Bandwidth == other.Bandwidth:
            return True
        else:
            return False
    

class Thread:

    def __init__(self, ThreadName):
    
        self.ThreadName = ThreadName
    
        # To be set when Application.addThread(self) is called
        self.ParentApplication = None
        self.ThreadID = None

        self.OutgoingFlows = []
        self.OutgoingBandwidth = 0
        
        self.IncomingFlows = []
        self.IncomingBandwidth = 0
        

    def addFlow(self, Flow, autoAddTargetThread = True):

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
                
    
    def __str__(self):

        returnString = ""
        
        returnString += ("\t " + self.ThreadName + " Targets\n")
        for OutgoingFlow in self.OutgoingFlows:
            returnString += (str(OutgoingFlow) + "\n")
            
        returnString += ("\n\t " + self.ThreadName + " Sources\n")
        for IncomingFlow in self.IncomingFlows:
            returnString += (str(IncomingFlow) + "\n")
            
        returnString += ("\n" + self.ThreadName + "Total Outgoing Bandwidth: " + str(self.OutgoingBandwidth))
        returnString += ("\n" + self.ThreadName + "Total Incoming Bandwidth: " + str(self.IncomingBandwidth))
        
        return returnString
        

class Application:

    def __init__(self, AppName):
    
        self.AppName = str(AppName)
        
        self.Threads = []
        
        # To be set when Workload.addApplication(self) is called
        self.AppID = None
        self.ParentWorkload = None
        
        
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
        

    def addThread(self, Thread):
        
        # If in this App there already is a Thread with given Thread's name, rename it, else, add it to App
        if Thread.ThreadName in self.ThreadsByName.keys():
        
            newName = Thread.ThreadName + "_A"
            
            while(True):
            
                if newName in self.ThreadsByName.keys():
                    
                    # Increments last char on "newName" and tries to add Thread to App again
                    newName = newName[:-1] + chr(int(newName[-1:]) + 1)
                
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
                
    
    # Returns a Thread object associated with a given ThreadName. If there is no ThreadName associated, returns None
    def getThreadByName(self, ThreadName):
    
        return self.ThreadsByName.get(ThreadName)

    
    def toJSON(self, SaveToFile = False, FileName = None):
    
        appDict = dict()
        appDict["AppName"] = self.AppName
        
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
        
        self.Threads = []
        self.ThreadsByName = dict()
        
        # To be set when Workload.addApplication(self) is called
        self.AppID = None
        self.ParentWorkload = None
        
        # Remove keys that arent associated with thread names
        JSONDict.pop("AppName", None)
        
        # Create Threads
        for ThreadName in JSONDict:
            self.addThread(Thread(ThreadName))
            
        # Add Flows to Threads
        for ThreadInApp in self.Threads:
        
            # Creates Flow with SourceThread and TargetThread as strings
            for FlowInThread in JSONDict[ThreadInApp.ThreadName]["Flows"]:
            
                ThreadInApp.addFlow(Flow(Bandwidth = FlowInThread["Bandwidth"], SourceThread = FlowInThread["SourceThread"], TargetThread = FlowInThread["TargetThread"]))


    def __str__(self):
    
        returnString = ""
        
        returnString += ("Amount of Threads: " + str(len(self.Threads)) + "\n")
        returnString += ("Total Bandwidth: " + str(self.TotalBandwidth) + "\n")
        
        try:
            returnString += ("Average Bandwidth: " + str(self.TotalBandwidth / len(self.Threads)) + "\n")
        except ZeroDivisionError:
            returnString += ("Average Bandwidth: 0\n")
            pass
        
        return returnString
        
        
class Workload:

    def __init__(self, WorkloadName):
    
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
    
    
    def addApplication(self, Application):
    
        # If in this Workload there already is an App with given App's name, rename it, else, add it to Workload
        if Application.AppName in self.ApplicationsByName.keys():
        
            newName = Application.ApplicationName + "_A"
            
            while(True):
            
                if newName in self.ApplicationsByName.keys():
                    
                    # Increments last char on "newName" and tries to add Thread to App again
                    newName = newName[:-1] + chr(int(newName[-1:]) + 1)
                
                # Renames thread and adds it to App
                else:
                
                    Application.renameApplication(newName)
                
                    Application.AppID = len(self.Applications)
                    Application.ParentApplication = self
                    self.Applications.append(Application)
                    
                    break
            
        else:
        
            Application.AppID = len(self.Applications)
            Application.ParentApplication = self
            self.Applications.append(Application)
            
    
    def removeApplication(self, Application):
    
        if Application in self.Applications:
            return self.Applications.pop(Application)
        else:
            print("Warning: Given App <" + str(Application.AppName) + "> doesnt exist in Workload " + str(self.WorkloadName))
            return None
    
    
    def toJSON(self, SaveToFile = False, FileName = None):
    
        workloadDict = dict()
        
        workloadDict["WorkloadName"] = self.WorkloadName
        
        for App in self.Applications:
            workloadDict[App.AppName] = JSON.loads(App.toJSON())
            
        # Converts workloadDict to a JSON-formatted string (sort_keys must be False so AppIDs are the same in original and reconstructed-from-JSON objects)
        JSONString = JSON.dumps(workloadDict, sort_keys=False, indent=4)
        
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
        self.ApplicationsByName = dict()
        
        # To be set when Platform.setWorkload(self) is called
        self.ParentPlatform = None

        # Pop keys unrelated to App names
        JSONDict.pop("WorkloadName")
        
        for AppName in JSONDict:
            newApp = Application(AppName = AppName)
            appJSONString = JSON.dumps(JSONDict[AppName], sort_keys=False, indent=4)
            newApp.fromJSON(appJSONString)
            self.addApplication(newApp)
            #self.addApplication(Application(AppName = AppName).fromJSON(JSON.dumps(JSONDict[AppName])))
            
    
    def __str__(self):
    
        returnString = ""
        
        returnString += "\tWorkload " + str(self.WorkloadName) + "\n"
        returnString += "Amount of Applications: " + str(len(self.Applications)) + "\n"
        returnString += "Total Bandwidth: " + str(self.TotalBandwidth) + "\n"
        returnString += "Average Bandwidth: " + str(self.AverageBandwidth) + "\n"

        return returnString
        
