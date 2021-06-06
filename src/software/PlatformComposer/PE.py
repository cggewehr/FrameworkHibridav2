
import AppComposer

class PE:

    def __init__(self, PEPos, BaseNoCPos, StructPos = None, ThreadSet = None, CommStructure = "NoC", DataWidth = 32, BridgeBufferSize = 4, BusArbiter = "RR"):

        self.PEPos = PEPos
        self.CommStructure = CommStructure
        self.BaseNoCPos = BaseNoCPos
        self.StructPos = StructPos
        
        self.BridgeBufferSize = BridgeBufferSize
        self.BusArbiter = BusArbiter
        
        if isinstance(ThreadSet, list) or isinstance(ThreadSet, dict):
            self.AmountOfThreads = len(ThreadSet)
            import functools
            self.AmountOfFlows = functools.reduce(lambda a,b : a+b, [len(Thread.OutgoingFlows) for Thread in ThreadSet])
            self.AmountOfFlowsInThread = [len(Thread.OutgoingFlows) for Thread in ThreadSet]
            self.LargestAmountOfFlows = max([len(Thread.OutgoingFlows) for Thread in ThreadSet])
            
        elif isinstance(ThreadSet, AppComposer.Thread):
            self.AmountOfThreads = 1
            self.AmountOfFlows = len(ThreadSet.OutgoingFlows)
            self.AmountOfFlowsInThread = [self.AmountOfFlows]
            self.LargestAmountOfFlows = self.AmountOfFlows
        
        elif ThreadSet is None:
        
            #print("Warning: PE <" + str(PEPos) + "> instantiated with no associated Thread object. This is to be expected if no Workload has been defined, or PE.__init__() is called from Platform.__init().")
            
            self.AmountOfThreads = 1
            self.AmountOfFlows = 1
            self.AmountOfFlowsInThread = [0]
            self.LargestAmountOfFlows = 1
            self.AppID = [0]
            self.AppName = ["IDLE"]
            self.ThreadID = [0]
            self.ThreadName = ["IDLE"]
            self.WorkloadName = ["IDLE"]
            
            return
        
        else:
            
            print("Error: Unrecognized type <" + str(type(ThreadSet)) + "> for argument ThreadSet")
            exit(1)
        
        # Determines each injector's clock frequency so that emulated bandwidth matches Flow bandwidth
        # Bandwidth (in MBps) = DataWidth (in bytes) / Period (in seconds)
        # Period (in nanoseconds) = (DataWidth (in bits) / 8) / (Bandwidth * 1000) (in GBps)
        #self.InjectorClockPeriods = [[(DataWidth / 8) / (OutgoingFlow.Bandwidth * 1000) for OutgoingFlow in Thread.OutgoingFlows] for Thread in ThreadSet] if isinstance(ThreadSet, list) else [(DataWidth / 8) / (OutgoingFlow.Bandwidth * 1000) for OutgoingFlow in ThreadSet.OutgoingFlows] # in nanoseconds
        #self.InjectorClockPeriods = [[(DataWidth / 8) / (OutgoingFlow.Bandwidth / 1000) for OutgoingFlow in Thread.OutgoingFlows] for Thread in ThreadSet] if isinstance(ThreadSet, list) else [(DataWidth / 8) / (OutgoingFlow.Bandwidth / 1000) for OutgoingFlow in ThreadSet.OutgoingFlows] # in nanoseconds

        #self.StartTimes = [[OutgoingFlow.StartTime for OutgoingFlow in ExistingThread.OutgoingFlows] for Thread in ThreadSet] if isinstance(ThreadSet, list) or isinstance(ThreadSet, dict) else [None]
        #self.StopTimes = [OutgoingFlow.StopTime for OutgoingFlow in Thread.OutgoingFlows]
        #self.StopTimes = [[OutgoingFlow.StopTime for OutgoingFlow in ExistingThread.OutgoingFlows] for Thread in ThreadSet] if isinstance(ThreadSet, list) or isinstance(ThreadSet, dict) else [None]
        
        # Workload attributes from given Thread object (at this point, ThreadSet is of type List/Dict or AppComposer.Thread)
        self.AppID = [ThreadSet.ParentApplication.AppID] if isinstance(ThreadSet, AppComposer.Thread) else [Thread.ParentApplication.AppID for Thread in ThreadSet]
        self.AppName = [ThreadSet.ParentApplication.AppName] if isinstance(ThreadSet, AppComposer.Thread) else [Thread.ParentApplication.AppName for Thread in ThreadSet]
        self.ThreadID = [ThreadSet.ThreadID] if isinstance(ThreadSet, AppComposer.Thread) else [Thread.ThreadID for Thread in ThreadSet]
        self.ThreadName = [ThreadSet.ThreadName] if isinstance(ThreadSet, AppComposer.Thread) else [Thread.ThreadName for Thread in ThreadSet]
        self.WorkloadName = [ThreadSet.ParentApplication.ParentWorkload.WorkloadName] if isinstance(ThreadSet, AppComposer.Thread) else [Thread.ParentApplication.ParentWorkload.WorkloadName for Thread in ThreadSet]
        
    
    def updateWorkloadInfo(self, ThreadSet, DataWidth = 32):
    
        if isinstance(ThreadSet, list) or isinstance(ThreadSet, dict):
            self.AmountOfThreads = len(ThreadSet)
            import functools
            self.AmountOfFlows = functools.reduce(lambda a,b : a+b, [len(Thread.OutgoingFlows) for Thread in ThreadSet])
            self.AmountOfFlowsInThread = [len(Thread.OutgoingFlows) for Thread in ThreadSet]
            self.LargestAmountOfFlows = max([len(Thread.OutgoingFlows) for Thread in ThreadSet])
            
        elif isinstance(ThreadSet, AppComposer.Thread):
            self.AmountOfThreads = 1
            self.AmountOfFlows = len(ThreadSet.OutgoingFlows)
            self.AmountOfFlowsInThread = [self.AmountOfFlows]
            self.LargestAmountOfFlows = self.AmountOfFlows
        
        elif ThreadSet is None:
        
            #print("Warning: PE <" + str(self.PEPos) + "> instantiated with no associated Thread object. This is to be expected if no Workload has been defined, or PE.__init__() is called from Platform.__init().")
            
            self.AmountOfThreads = 1
            self.AmountOfFlows = 1
            self.AmountOfFlowsInThread = [0]
            self.LargestAmountOfFlows = 1
            self.AppID = [0]
            self.AppName = ["IDLE"]
            self.ThreadID = [0]
            self.ThreadName = ["IDLE"]
            self.WorkloadName = ["IDLE"]
            
            return
        
        else:
            
            print("Error: Unrecognized type <" + str(type(ThreadSet)) + "> for argument ThreadSet")
            exit(1)
        
        # DEBUG
        #print(str(ThreadSet))
        #print(str(Thread.ParentApplication)) if Thread is not None

        # Determines each injector's clock frequency so that emulated bandwidth matches Flow bandwidth
        # Bandwidth (in MBps) = DataWidth (in bytes) / Period (in seconds)
        # Period (in nanoseconds) = (DataWidth (in bits) / 8) / (Bandwidth * 1000) (in GBps)
        #self.InjectorClockPeriods = [[(DataWidth / 8) / (OutgoingFlow.Bandwidth * 1000) for OutgoingFlow in Thread.OutgoingFlows] for Thread in ThreadSet] if isinstance(ThreadSet, list) else [(DataWidth / 8) / (OutgoingFlow.Bandwidth * 1000) for OutgoingFlow in ThreadSet.OutgoingFlows] # in nanoseconds
        #self.InjectorClockPeriods = [[(DataWidth / 8) / (OutgoingFlow.Bandwidth / 1000) for OutgoingFlow in Thread.OutgoingFlows] for Thread in ThreadSet] if isinstance(ThreadSet, list) else [(DataWidth / 8) / (OutgoingFlow.Bandwidth / 1000) for OutgoingFlow in ThreadSet.OutgoingFlows] # in nanoseconds
        
        #self.StartTimes = [[OutgoingFlow.StartTime for OutgoingFlow in ExistingThread.OutgoingFlows] for Thread in ThreadSet] if isinstance(ThreadSet, list) or isinstance(ThreadSet, dict) else [None]
        #self.StopTimes = [OutgoingFlow.StopTime for OutgoingFlow in Thread.OutgoingFlows]
        #self.StopTimes = [[OutgoingFlow.StopTime for OutgoingFlow in ExistingThread.OutgoingFlows] for Thread in ThreadSet] if isinstance(ThreadSet, list) or isinstance(ThreadSet, dict) else [None]
        
        # Workload attributes from given Thread object (at this point, ThreadSet is of type List/Dict or AppComposer.Thread)
        self.AppID = [ThreadSet.ParentApplication.AppID] if isinstance(ThreadSet, AppComposer.Thread) else [Thread.ParentApplication.AppID for Thread in ThreadSet]
        self.AppName = [ThreadSet.ParentApplication.AppName] if isinstance(ThreadSet, AppComposer.Thread) else [Thread.ParentApplication.AppName for Thread in ThreadSet]
        self.ThreadID = [ThreadSet.ThreadID] if isinstance(ThreadSet, AppComposer.Thread) else [Thread.ThreadID for Thread in ThreadSet]
        self.ThreadName = [ThreadSet.ThreadName] if isinstance(ThreadSet, AppComposer.Thread) else [Thread.ThreadName for Thread in ThreadSet]
        self.WorkloadName = [ThreadSet.ParentApplication.ParentWorkload.WorkloadName] if isinstance(ThreadSet, AppComposer.Thread) else [Thread.ParentApplication.ParentWorkload.WorkloadName for Thread in ThreadSet]
        
        return self
        
    
    def toJSON(self):

        import json

        return json.dumps(self.__dict__, sort_keys = True, indent = 4)

