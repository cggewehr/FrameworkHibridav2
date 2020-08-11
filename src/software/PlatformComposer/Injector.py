
class Injector:

    def __init__(self, PEPos, Thread, InjectorClockFrequency):

        # Gets position value from AllocationTable dictionary
        
        #self.AppID = Thread.ParentApplication.AppID if Thread.ParentApplication is not None else 99
        #self.ThreadID = Thread.ThreadID if Thread.ThreadID is not None else 99
        
        self.PEPos = int(PEPos)
        self.InjectorClockFrequency = InjectorClockFrequency
        
        # Workload Info
        self.AppID = Thread.ParentApplication.AppID if Thread is not None else -1
        self.AppName = Thread.ParentApplication.AppName if Thread is not None else "IDLE"
        self.ThreadID = Thread.ThreadID if Thread is not None else -1
        self.ThreadName = Thread.ThreadName if Thread is not None else "IDLE"
        self.WorkloadName = Thread.ParentApplication.ParentWorkload.WorkloadName if Thread is not None else "IDLE"

        # Checks for a dummy injector (PE is idle or doesnt send messages)
        #if Thread.OutgoingBandwidth is not None:
        if Thread is not None:

            # LinkBandwidth = DataWidth (in bits) / 8 * ClockFrequency (of out buffer write port) (in bytes/second)
            # Consumed Bandwidth = LinkBandwidth * InjectionRate
            # InjectionRate = ConsumedBandwidth/(DataWidth * ClockFrequency)
            #self.InjectionRate = int((Thread.TotalBandwidth * 100) / (32 * InjectorClockFrequency))

            #print("ThreadInInj:" + str(Thread))
            print("PE: " + str(self.PEPos))
            print("Out buffer clock frequency: " + str(InjectorClockFrequency))
            LinkBandwidth = 4 * InjectorClockFrequency
            print("Link bandwidth: " + str(LinkBandwidth))
            self.InjectionRate = int((Thread.OutgoingBandwidth * 100) / ((32 / 8) * InjectorClockFrequency))
            print("Injection Rate: " + str(self.InjectionRate))
            print("Consumed bandwidth (outgoing): " + str(LinkBandwidth * self.InjectionRate / 100) + "\n")

            if self.InjectionRate == 0 and Thread.OutgoingBandwidth != 0:

                print("Warning: Injection rate = 0% at injector <" + str(self.PEPos) + ">, setting it to 1%")
                self.InjectionRate = 1

            if self.InjectionRate > 100:

                print("Warning: Injection rate > 100% (" + str(self.InjectionRate) + "%) at injector <" + str(self.PEPos) + ">, setting it to 100%")
                self.InjectionRate = 100

        else:

            self.InjectionRate = 0

        self.TargetPEs = []
        self.AmountOfMessagesInBurst = []

        if Thread is not None and Thread.OutgoingBandwidth != 0:

            # Determines TargetPEs and AmountOfMessagesInBurst arrays based on required bandwidth
            #for i in range(len(Thread.Targets)):

                # #self.TargetPEs.append(Thread.ParentApplication.ParentWorkload.ParentPlatform.getPEPos(Thread.Targets[i].TargetThread))
                # self.TargetPEs.append(Thread.ParentApplication.ParentWorkload.ParentPlatform.getPEPos(Thread.OutgoingFlows[i].TargetThread))
                # #self.AmountOfMessagesInBurst.append(Thread.Targets[i].Bandwidth)
                # self.AmountOfMessagesInBurst.append(Thread.OutgoingFlows[i].Bandwidth)

            for OutgoingFlow in Thread.OutgoingFlows:
                self.TargetPEs.append(OutgoingFlow.TargetThread.PEPos)
                self.AmountOfMessagesInBurst.append(OutgoingFlow.Bandwidth)
            
            # WIP: Find greatest common divider for all AmountOfMessagesInBursts (maintains proportion but allows
            # switching between targets without sending a large amount of messages
            from fractions import gcd
            from functools import reduce
            GreatestCommonDivisor = reduce(gcd, self.AmountOfMessagesInBurst)
            MinimalValue = min(self.AmountOfMessagesInBurst)
            #print("GCD = " + str(GreatestCommonDivisor))
            #print("MinVal = " + str(MinimalValue))
            #print(self.AmountOfMessagesInBurst)

            if MinimalValue < 1:
                
                try:

                    # Finds a new minimal value > 1
                    MinimalValue = min(i for i in self.AmountOfMessagesInBurst if i > 1)

                    #  Reduces new minimal value (which will divide all elements of array) in order to 
                    # maintain proportion (Values < 1, will be set to 1, but so will be any values ~= to new MinVal,
                    # resulting in a equal perceived bandwidth in RTL simulation, even though their bandwidth
                    # requirements as set in given application script may be very different). >10 and /2 are arbitrary 
                    if MinimalValue > 10:
                        MinimalValue = MinimalValue / 2

                    #print("MinVal = " + str(MinimalValue))
                
                except ValueError:  # Thrown when an empty list is given as argument to min()
                    
                    # No value < 1 in AmountOfMessagesinBurst
                    #for i in range(len(self.AmountOfMessagesInBurst)):
                        #self.AmountOfMessagesInBurst[i] = int(round(self.AmountOfMessagesInBurst[i] / float(MinimalValue)))
                    pass
                # Sets all elements < 1 to new minimal value
                for i in range(len(self.AmountOfMessagesInBurst)):
                    self.AmountOfMessagesInBurst[i] = int(round(self.AmountOfMessagesInBurst[i] / float(MinimalValue)))
                    #print(self.AmountOfMessagesInBurst[i])

                for i in range(len(self.AmountOfMessagesInBurst)):
                    if self.AmountOfMessagesInBurst[i] == 0:
                        self.AmountOfMessagesInBurst[i] = 1

            else:

                # Divide all elements by either GreatestCommonDivisor or MinimalValue, whichever is the greatest
                for i in range(len(self.AmountOfMessagesInBurst)):

                    if GreatestCommonDivisor > 2:
                        self.AmountOfMessagesInBurst[i] = int(round(self.AmountOfMessagesInBurst[i] / GreatestCommonDivisor))
       
                    else:
                        self.AmountOfMessagesInBurst[i] = int(round(self.AmountOfMessagesInBurst[i] / MinimalValue))

            #print("GCD = " + str(GreatestCommonDivisor))
            #print(self.AmountOfMessagesInBurst)
            #print("\n")

        else:

            # Set dummy values
            self.TargetPEs.append(0)
            self.AmountOfMessagesInBurst.append(99)

        self.TargetPayloadSize = [126] * len(self.TargetPEs)

        self.SourcePEs = [0]  # Default
        self.SourcePayloadSize = 32  # Default
        self.AmountOfSourcePEs = len(self.SourcePEs)
        self.AmountOfTargetPEs = len(self.TargetPEs)
        self.AverageProcessingTimeInClockPulses = 1  # Default, not used in current injector
        self.InjectorType = "FXD"  # Default
        self.FlowType = "RND"  # Default
        self.HeaderSize = 2  # Default
        self.timestampFlag = 1984626850  # Default
        self.amountOfMessagesSentFlag = 2101596287  # Default
        
        import random
        self.RNGSeed1 = random.randint(0, 2147483646)  # Random Value
        self.RNGSeed2 = random.randint(0, 2147483646)  # Random Value

        self.Headers = dict()
        self.Payloads = dict()

        for i in range(len(self.TargetPEs)):

            payloads_aux = [  # Default
                "PEPOS",
                "TMSTP",
                "RANDO",
                "RANDO",
                "RANDO",
                "RANDO",
            ]

            for j in range(int(self.TargetPayloadSize[i]) - 6):
                payloads_aux.append("RANDO")  # Preenche com RANDO #Default

            self.Headers["Header" + str(self.TargetPEs[i])] = ["ADDR", "SIZE"]  # Default
            self.Payloads["Payload" + str(self.TargetPEs[i])] = payloads_aux


    def toJSON(self):
        
        import json
        return json.dumps(self.__dict__, sort_keys=True, indent=4)

