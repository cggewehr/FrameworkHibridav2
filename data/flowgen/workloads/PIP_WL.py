import os
import AppComposer

# Makes Workload object
PIP_WL = AppComposer.Workload(WorkloadName = "PIP_WL")

# Opens PIP App json file
with open(os.getenv("FLOWGEN_APPLICATIONS_PATH") + "/PIP.json") as PIP_JSON:
    
    # Builds 3 PIP Apps from json and adds them to PIP_WL Workload
    for i in range(3):
        
        PIP = AppComposer.Application()
        PIP.fromJSON(PIP_JSON.read())
        PIP_WL.addApplication(PIP)
        PIP_JSON.seek(0)

# Exports Workload to json format
PIP_WL.toJSON(SaveToFile = True, FileName = "PIP_WL")

#print(str(PIP_WL))

# WL_JSONFile = open("PIP_WL.json", "r")
# PIP_WL_FromJSON = AppComposer.Workload(WorkloadName = "PIP_WL_FromJSON")
# PIP_WL_FromJSON.fromJSON(WL_JSONFile.read())

# print(str(PIP_WL_FromJSON))
