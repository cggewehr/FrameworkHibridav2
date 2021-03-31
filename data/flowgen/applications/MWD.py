import AppComposer

# Make Application
MWD = AppComposer.Application(AppName = "MWD")
Applications = [MWD]

# Make Threads
IN = AppComposer.Thread()
NR = AppComposer.Thread()
MEM1 = AppComposer.Thread()
VS = AppComposer.Thread()
HS = AppComposer.Thread()
MEM2 = AppComposer.Thread()
HVS = AppComposer.Thread()
JUG1 = AppComposer.Thread()
MEM3 = AppComposer.Thread()
JUG2 = AppComposer.Thread()
SE = AppComposer.Thread()
Blend = AppComposer.Thread()

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

# Add targets to Threads (Bandwidth must be in Megabits/second)
IN.addTarget(AppComposer.Target(TargetThread = NR, Bandwidth = 64))
IN.addTarget(AppComposer.Target(TargetThread = HS, Bandwidth = 128))
NR.addTarget(AppComposer.Target(TargetThread = MEM1, Bandwidth = 64))
NR.addTarget(AppComposer.Target(TargetThread = MEM2, Bandwidth = 96))
MEM1.addTarget(AppComposer.Target(TargetThread = NR, Bandwidth = 64))
HS.addTarget(AppComposer.Target(TargetThread = VS, Bandwidth = 96))
VS.addTarget(AppComposer.Target(TargetThread = JUG1, Bandwidth = 96))
MEM2.addTarget(AppComposer.Target(TargetThread = HVS, Bandwidth = 96))
HVS.addTarget(AppComposer.Target(TargetThread = JUG2, Bandwidth = 96))
JUG1.addTarget(AppComposer.Target(TargetThread = MEM3, Bandwidth = 96))
MEM3.addTarget(AppComposer.Target(TargetThread = SE, Bandwidth = 64))
JUG2.addTarget(AppComposer.Target(TargetThread = MEM3, Bandwidth = 96))
SE.addTarget(AppComposer.Target(TargetThread = Blend, Bandwidth = 64))

