
import AppComposer

# Implements (in hardware) an AppComposer.Flow object
class Injector:

    def __init__(self, Flow, SourcePEPos, SourceBaseNoCPos, TargetPEPos, TargetBaseNoCPos, DataWidth = 32):
        
        # Checks if Flow argument is of AppComposser.Flow class
        if not isinstance(Flow, AppComposer.Flow):
            print("Error: Given Flow argument is not of class AppComposer.Flow")
            exit(1)
        
        # Checks if SourceThread has been defined in associated Flow object
        if isinstance(Flow.SourceThread, AppComposer.Thread):
            SourceThread = Flow.SourceThread
        else:
            print("Error: Given Flow <" + str(Flow) + "> SourceThread is not a AppComposer.Thread object")
            exit(1)
            
        # Checks if TargetThread has been defined in associated Flow object
        if isinstance(Flow.TargetThread, AppComposer.Thread):
            TargetThread = Flow.TargetThread
        else:
            print("Error: Given Flow <" + str(Flow) + "> TargetThread is not a AppComposer.Thread object")
            exit(1)
        
        # Thread info
        self.SourcePEPos = SourcePEPos
        self.SourceBaseNoCPos = SourceBaseNoCPos
        self.TargetPEPos = TargetPEPos
        self.TargetBaseNoCPos = TargetBaseNoCPos

        # TODO: Adjust clock period definition so that bandwidth value represents payload flits only
        # Flow info
        self.FlowType = Flow.FlowType  # Default = "CBR"
        self.Bandwidth = float(Flow.Bandwidth)  # in MBps
        #self.InjectorClockPeriod = (DataWidth / 8) / (Flow.Bandwidth * 1000)  # in nanoseconds
        self.InjectorClockPeriod = float((1000 * DataWidth / 8) / (Flow.Bandwidth)) if Flow.Bandwidth != 0 else float(9999999) # in nanoseconds
        self.StartTime = float(Flow.StartTime)  # in nanoseconds
        self.StopTime = float(Flow.StopTime)  # in nanoseconds
        self.Periodic = Flow.Periodic
        self.MSGAmount = Flow.MSGAmount
        
        # Workload Info
        self.SourceThreadID = SourceThread.ThreadID
        self.SourceThreadName = SourceThread.ThreadName
        self.TargetThreadID = TargetThread.ThreadID
        self.TargetThreadName = TargetThread.ThreadName
        self.AppID = SourceThread.ParentApplication.AppID
        self.AppName = SourceThread.ParentApplication.AppName
        self.WorkloadName = SourceThread.ParentApplication.ParentWorkload.WorkloadName

        # Message info
        # TODO: 
        self.Header = Flow.Header  # Default = ["ADDR", "SIZE"]
        #self.Payload = Flow.Payload  # Default = ["PEPOS", "TMSTP"] + (["RANDO"] * 126 - 2)
        self.Payload = [flit.ljust(int(DataWidth / 4), " ") for flit in Flow.Payload]  # Pad each flit description to <DataWidth/4> chars
        self.HeaderSize = len(self.Header)
        self.PayloadSize = len(self.Payload)
        self.MessageSize = len(self.Header) + len(self.Payload)
        
        # Payload Real Time Flags
        self.TimestampFlag = 2147483643  # Default
        self.AmountOfMessagesSentFlag = 2147483644  # Default
        
        import random
        self.RNGSeed1 = random.randint(0, 2147483646)  # Random Value [0, (2**32) - 2]
        self.RNGSeed2 = random.randint(0, 2147483646)  # Random Value [0, (2**32) - 2]
        
        # Header filts can be : 
        # "ADDR" (Address of target PE in network)
        # "SIZE" (Size of payload in this message)
        # "TIME" (Timestamp (in clock cycles) of when first flit of message leaves the injector)
        # "BLNK" (Fills with zeroes)
        
        #  Payload flits can be:
        # "PEPOS": (PE position in network), 
        # "APPID": (ID of app being emulated by this injector), 
        # "THDID": (ID of thread of the app being emulated in this PE),
        # <UNSUPPORTED> "AVGPT": (Average processing time of a message received by the app being emulated by this PE),  
        # "TMSTP": (Timestamp of message being sent (to be set in real time, not in this function)),
        # "AMMSG": (Amount of messages sent by this PE (also to be se in real time)),
        # "RANDO": (Randomize every bit)
        # "BLANK": (Fills with zeroes)


    def __str__(self):
    
        NotImplementedError
        
        returnString = ""
        return returnString
    
    
    def toJSON(self):
        
        import json
        return json.dumps(self.__dict__, sort_keys=True, indent=4)

