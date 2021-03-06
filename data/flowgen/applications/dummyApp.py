import AppComposer

# Make Application
dummyApp = AppComposer.Application(AppName = "DummyApp", StartTime = 0, StopTime = 0)

# Make Threads
dummyThreadA = AppComposer.Thread(ThreadName = "DummyThreadA")
dummyThreadB = AppComposer.Thread(ThreadName = "DummyThreadB")

# Add Threads to applications
dummyApp.addThread(dummyThreadA)
dummyApp.addThread(dummyThreadB)

# Add Flows to Threads (Bandwidth parameter must be in Megabytes/second)
dummyThreadA.addFlow(AppComposer.Flow(TargetThread = dummyThreadB, Bandwidth = 0))
dummyThreadB.addFlow(AppComposer.Flow(TargetThread = dummyThreadA, Bandwidth = 0))

# Save App to JSON
dummyApp.toJSON(SaveToFile = True, FileName = "dummyApp")

