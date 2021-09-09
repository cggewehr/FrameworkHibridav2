import os
import AppComposer

# Makes Workload object
WorkloadBB = AppComposer.Workload(WorkloadName = "WorkloadBB")

# Open Application JSON files
PIPFile = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/PIP.json")
MWDFile = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/MWD.json")
H264_30File = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/H264_30.json")

# Get Application files content
PIPJSONContent = PIPFile.read()
MWDJSONContent = MWDFile.read()
H264_30JSONContent = H264_30File.read()

# Build Workload BB Applications
BB_PIP = AppComposer.Application()
BB_PIP.fromJSON(PIPJSONContent)
BB_PIP.AppName = "BB_PIP"

BB_MWD = AppComposer.Application()
BB_MWD.fromJSON(MWDJSONContent)
BB_MWD.AppName = "BB_MWD"

BB_H264_30 = AppComposer.Application()
BB_H264_30.fromJSON(H264_30JSONContent)
BB_H264_30.AppName = "BB_H264_30"

# Add Applications to Workload
WorkloadBB.addApplication(BB_PIP)
WorkloadBB.addApplication(BB_MWD)
WorkloadBB.addApplication(BB_H264_30)

# Export WorkloadBB to JSON format
WorkloadBB.toJSON(SaveToFile = True, FileName = "WorkloadBB")
