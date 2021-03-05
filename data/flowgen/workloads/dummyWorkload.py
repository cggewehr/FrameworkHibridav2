import os
import AppComposer

# Makes Workload object
DummyWorkload = AppComposer.Workload(WorkloadName = "DummyWorkload")

# Opens PIP App json file
with open("/home/usr/cgewehr/Desktop/FrameworkHibrida/data/flowgen/applications/dummyApp.json") as dummyAppFile:
    
    # Builds 3 PIP Apps from json and adds them to PIP_WL Workload
    dummyApp = AppComposer.Application()
    dummyApp.fromJSON(dummyAppFile.read())
    DummyWorkload.addApplication(dummyApp)

# Exports Workload to json format
DummyWorkload.toJSON(SaveToFile = True, FileName = "DummyWorkload")

