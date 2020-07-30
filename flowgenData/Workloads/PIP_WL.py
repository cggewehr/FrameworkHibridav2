import AppComposer

PIP_WL = AppComposer.Workload(WorkloadName = "PIP_WL")

import os

with open(os.getenv("FLOWGEN_APPLICATIONS_PATH") + "/PIP.json") as PIP_JSON:

    PIP = AppComposer.Application(AppName = "PIP")
    print("Making App")
    #print(PIP_JSON.read())
    PIP.fromJSON(PIP_JSON.read())
    print("App made")

    PIP_WL.addApplication(PIP)

print(str(PIP_WL))

PIP_WL.toJSON(SaveToFile = True, FileName = "PIP_WL")

# WL_JSONFile = open("PIP_WL.json", "r")
# PIP_WL_FromJSON = AppComposer.Workload(WorkloadName = "PIP_WL_FromJSON")
# PIP_WL_FromJSON.fromJSON(WL_JSONFile.read())

# print(str(PIP_WL_FromJSON))