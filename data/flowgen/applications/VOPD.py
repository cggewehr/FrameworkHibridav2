import AppComposer

# Make Application
VOPD = AppComposer.Application(AppName = "VOPD", StartTime = 0, StopTime = 0)

# Make Threads
VLD = AppComposer.Thread(ThreadName = "VLD")
RunLeDec = AppComposer.Thread(ThreadName = "RunLeDec")
InvScan = AppComposer.Thread(ThreadName = "InvScan")
AcdcPred = AppComposer.Thread(ThreadName = "AcdcPred")
Iquan = AppComposer.Thread(ThreadName = "IQuan")
IDCT = AppComposer.Thread(ThreadName = "IDCT")
ARM = AppComposer.Thread(ThreadName = "ARM")
UpSamp = AppComposer.Thread(ThreadName = "UpSamp")
VopRec = AppComposer.Thread(ThreadName = "VopRec")
Pad = AppComposer.Thread(ThreadName = "Pad")
VopMem = AppComposer.Thread(ThreadName = "VopMem")
StripeMem = AppComposer.Thread(ThreadName = "StripeMem")

# Add Threads to applications
VOPD.addThread(VLD)
VOPD.addThread(RunLeDec)
VOPD.addThread(InvScan)
VOPD.addThread(AcdcPred)
VOPD.addThread(Iquan)
VOPD.addThread(IDCT)
VOPD.addThread(ARM)
VOPD.addThread(UpSamp)
VOPD.addThread(VopRec)
VOPD.addThread(Pad)
VOPD.addThread(VopMem)
VOPD.addThread(StripeMem)

# Add Flows to Threads (Bandwidth must be in Megabytes/second)
VLD.addFlow(AppComposer.CBRFlow(TargetThread = RunLeDec, Bandwidth = 70))
RunLeDec.addFlow(AppComposer.CBRFlow(TargetThread = InvScan, Bandwidth = 362))
InvScan.addFlow(AppComposer.CBRFlow(TargetThread = AcdcPred, Bandwidth = 362))
AcdcPred.addFlow(AppComposer.CBRFlow(TargetThread = Iquan, Bandwidth = 362))
AcdcPred.addFlow(AppComposer.CBRFlow(TargetThread = StripeMem, Bandwidth = 49))
StripeMem.addFlow(AppComposer.CBRFlow(TargetThread = Iquan, Bandwidth = 27))
Iquan.addFlow(AppComposer.CBRFlow(TargetThread = IDCT, Bandwidth = 357))
IDCT.addFlow(AppComposer.CBRFlow(TargetThread = UpSamp, Bandwidth = 353))
ARM.addFlow(AppComposer.CBRFlow(TargetThread = IDCT, Bandwidth = 16))
ARM.addFlow(AppComposer.CBRFlow(TargetThread = Pad, Bandwidth = 16))
UpSamp.addFlow(AppComposer.CBRFlow(TargetThread = VopRec, Bandwidth = 300))
VopRec.addFlow(AppComposer.CBRFlow(TargetThread = Pad, Bandwidth = 313))
Pad.addFlow(AppComposer.CBRFlow(TargetThread = VopMem, Bandwidth = 313))
VopMem.addFlow(AppComposer.CBRFlow(TargetThread = Pad, Bandwidth = 94))

# Save App to JSON
VOPD.toJSON(SaveToFile = True, FileName = "VOPD")
