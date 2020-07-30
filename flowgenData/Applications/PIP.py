import AppComposer

# Make Application
PIP = AppComposer.Application(AppName = "PIP")

# Make Threads
InpMemA = AppComposer.Thread(ThreadName = "InpMemA")
HS = AppComposer.Thread(ThreadName = "HS")
VS = AppComposer.Thread(ThreadName = "VS")
JUG1 = AppComposer.Thread(ThreadName = "JUG1")
InpMemB = AppComposer.Thread(ThreadName = "InpMemB")
JUG2 = AppComposer.Thread(ThreadName = "JUG2")
MEM = AppComposer.Thread(ThreadName = "MEM")
OpDisp = AppComposer.Thread(ThreadName = "OpDisp")

# Add Threads to applications
PIP.addThread(InpMemA)
PIP.addThread(HS)
PIP.addThread(VS)
PIP.addThread(JUG1)
PIP.addThread(InpMemB)
PIP.addThread(JUG2)
PIP.addThread(MEM)
PIP.addThread(OpDisp)

# Add Flows to Threads (Bandwidth parameter must be in Megabytes/second)
InpMemA.addFlow(AppComposer.Flow(TargetThread = HS, Bandwidth = 128))       # InpMemA -- 128 -> HS
InpMemA.addFlow(AppComposer.Flow(TargetThread = InpMemB, Bandwidth = 64))   # InpMemA -- 64 -> InpMemB
HS.addFlow(AppComposer.Flow(TargetThread = VS, Bandwidth = 64))             # HS -- 64 -> VS
VS.addFlow(AppComposer.Flow(TargetThread = JUG1, Bandwidth = 64))           # VS -- 64 -> JUG1
JUG1.addFlow(AppComposer.Flow(TargetThread = MEM, Bandwidth = 64))          # JUG1 -- 64 -> MEM
InpMemB.addFlow(AppComposer.Flow(TargetThread = JUG2, Bandwidth = 64))      # InpMemB -- 64 -> JUG2
JUG2.addFlow(AppComposer.Flow(TargetThread = MEM, Bandwidth = 64))          # JUG2 -- 64 -> MEM
MEM.addFlow(AppComposer.Flow(TargetThread = OpDisp, Bandwidth = 64))        # MEM -- 64 -> OpDisp

# print(str(PIP))

# Save App to JSON
PIP.toJSON(SaveToFile = True, FileName = "PIP")

# # Opens file and build App from JSON
# JSONFile = open("PIP.json", "r")

# PIPFromJSON = AppComposer.Application(AppName = "PIPFromJSON")
# PIPFromJSON.fromJSON(JSONFile.read())

# print(str(PIPFromJSON))

# PIPFromJSON.toJSON(SaveToFile = True, FileName = "PIPFromJSON")

# Saves Workload
# PIP_WL = AppComposer.Workload(WorkloadName = "PIP_WL")
# PIP_WL.addApplication(PIP)

# print(str(PIP_WL))

# PIP_WL.toJSON(SaveToFile = True, FileName = "PIP_WL")

# WL_JSONFile = open("PIP_WL.json", "r")
# PIP_WL_FromJSON = AppComposer.Workload(WorkloadName = "PIP_WL_FromJSON")
# PIP_WL_FromJSON.fromJSON(WL_JSONFile.read())

# print(str(PIP_WL_FromJSON))

