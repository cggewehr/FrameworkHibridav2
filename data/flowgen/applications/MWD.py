import AppComposer

# Make Application
MWD = AppComposer.Application(AppName = "MWD", StartTime = 0, StopTime = 0)

# Make Threads
IN = AppComposer.Thread(ThreadName = "IN")
NR = AppComposer.Thread(ThreadName = "NR")
MEM1 = AppComposer.Thread(ThreadName = "MEM1")
VS = AppComposer.Thread(ThreadName = "VS")
HS = AppComposer.Thread(ThreadName = "HS")
MEM2 = AppComposer.Thread(ThreadName = "MEM2")
HVS = AppComposer.Thread(ThreadName = "HVS")
JUG1 = AppComposer.Thread(ThreadName = "JUG1")
MEM3 = AppComposer.Thread(ThreadName = "MEM3")
JUG2 = AppComposer.Thread(ThreadName = "JUG2")
SE = AppComposer.Thread(ThreadName = "SE")
Blend = AppComposer.Thread(ThreadName = "Blend")

# Add Threads to applications
MWD.addThread(IN)
MWD.addThread(NR)
MWD.addThread(MEM1)
MWD.addThread(VS)
MWD.addThread(HS)
MWD.addThread(MEM2)
MWD.addThread(HVS)
MWD.addThread(JUG1)
MWD.addThread(MEM3)
MWD.addThread(JUG2)
MWD.addThread(SE)
MWD.addThread(Blend)

# Add Flows to Threads (Bandwidth must be in Megabytes/second) 
IN.addFlow(AppComposer.Flow(TargetThread = NR, Bandwidth = 64))
IN.addFlow(AppComposer.Flow(TargetThread = HS, Bandwidth = 128))
NR.addFlow(AppComposer.Flow(TargetThread = MEM1, Bandwidth = 64))
NR.addFlow(AppComposer.Flow(TargetThread = MEM2, Bandwidth = 96))
MEM1.addFlow(AppComposer.Flow(TargetThread = NR, Bandwidth = 64))
HS.addFlow(AppComposer.Flow(TargetThread = VS, Bandwidth = 96))
VS.addFlow(AppComposer.Flow(TargetThread = JUG1, Bandwidth = 96))
MEM2.addFlow(AppComposer.Flow(TargetThread = HVS, Bandwidth = 96))
HVS.addFlow(AppComposer.Flow(TargetThread = JUG2, Bandwidth = 96))
JUG1.addFlow(AppComposer.Flow(TargetThread = MEM3, Bandwidth = 96))
MEM3.addFlow(AppComposer.Flow(TargetThread = SE, Bandwidth = 64))
JUG2.addFlow(AppComposer.Flow(TargetThread = MEM3, Bandwidth = 96))
SE.addFlow(AppComposer.Flow(TargetThread = Blend, Bandwidth = 64))

# Save App to JSON
MWD.toJSON(SaveToFile = True, FileName = "MWD")
