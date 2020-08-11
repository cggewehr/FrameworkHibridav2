
class PE:

    #def __init__(self, PEPos, AppID = None, ThreadID = None, InjectorClockFrequency = None, InjectorType = "FXD", InBufferSize = 128, OutBufferSize = 128):
    def __init__(self, PEPos, CommStructure, AddressInBaseNoC, PosInStruct = None, Thread = None, InjectorClockFrequency = None, InjectorType = "FXD", InBufferSize = 128, OutBufferSize = 128):

        self.PEPos = PEPos
        self.CommStructure = CommStructure
        self.AddressInBaseNoC = AddressInBaseNoC
        self.PosInStruct = PosInStruct
        self.InjectorType = InjectorType

        if InjectorClockFrequency is None:
            self.InjectorClockPeriod = None
        else:
            # Period in ns, Freq in MHz
            self.InjectorClockPeriod = float(1000/InjectorClockFrequency)        
        
        # Workload attributes from given Thread object
        self.AppID = Thread.ParentApplication.AppID if Thread is not None else -1
        self.AppName = Thread.ParentApplication.AppName if Thread is not None else "IDLE"
        self.ThreadID = Thread.ThreadID if Thread is not None else -1
        self.ThreadName = Thread.ThreadName if Thread is not None else "IDLE"
        self.WorkloadName = Thread.ParentApplication.ParentWorkload.WorkloadName if Thread is not None else "IDLE"
        
        self.InBufferSize = InBufferSize
        self.OutBufferSize = OutBufferSize
        self.AverageProcessingTimeInClockPulses = 1  # Default, not currently used in injector

    
    def updateWorkloadInfo(self, Thread):
        
        # DEBUG
        print(str(Thread))
        #print(str(Thread.ParentApplication)) if Thread is not None

        # Workload attributes from given Thread object
        self.AppID = Thread.ParentApplication.AppID if Thread is not None else -1
        self.AppName = Thread.ParentApplication.AppName if Thread is not None else "IDLE"
        self.ThreadID = Thread.ThreadID if Thread is not None else -1
        self.ThreadName = Thread.ThreadName if Thread is not None else "IDLE"
        self.WorkloadName = Thread.ParentApplication.ParentWorkload.WorkloadName if Thread is not None else "IDLE"
        
    
    def toJSON(self):

        import json

        return json.dumps(self.__dict__, sort_keys = True, indent = 4)

