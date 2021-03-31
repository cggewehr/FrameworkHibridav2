import AppComposer

# Make Application
VOPD = AppComposer.Application(AppName = "VOPD")
Applications = [VOPD]

# Make Threads
VLD = AppComposer.Thread()
RunLeDec = AppComposer.Thread()
InvScan = AppComposer.Thread()
AcdcPred = AppComposer.Thread()
Iquan = AppComposer.Thread()
IDCT = AppComposer.Thread()
ARM = AppComposer.Thread()
UpSamp = AppComposer.Thread()
VopRec = AppComposer.Thread()
Pad = AppComposer.Thread()
VopMem = AppComposer.Thread()
StripeMem = AppComposer.Thread()

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

# Add targets to Threads (Bandwidth must be in Megabits/second)
VLD.addTarget(AppComposer.Target(TargetThread = RunLeDec, Bandwidth = 70))
RunLeDec.addTarget(AppComposer.Target(TargetThread = InvScan, Bandwidth = 362))
InvScan.addTarget(AppComposer.Target(TargetThread = AcdcPred, Bandwidth = 362))
AcdcPred.addTarget(AppComposer.Target(TargetThread = Iquan, Bandwidth = 362))
AcdcPred.addTarget(AppComposer.Target(TargetThread = StripeMem, Bandwidth = 49))
StripeMem.addTarget(AppComposer.Target(TargetThread = Iquan, Bandwidth = 27))
Iquan.addTarget(AppComposer.Target(TargetThread = IDCT, Bandwidth = 357))
IDCT.addTarget(AppComposer.Target(TargetThread = UpSamp, Bandwidth = 353))
ARM.addTarget(AppComposer.Target(TargetThread = IDCT, Bandwidth = 16))
ARM.addTarget(AppComposer.Target(TargetThread = Pad, Bandwidth = 16))
UpSamp.addTarget(AppComposer.Target(TargetThread = VopRec, Bandwidth = 300))
VopRec.addTarget(AppComposer.Target(TargetThread = Pad, Bandwidth = 313))
Pad.addTarget(AppComposer.Target(TargetThread = VopMem, Bandwidth = 313))
VopMem.addTarget(AppComposer.Target(TargetThread = Pad, Bandwidth = 94))
