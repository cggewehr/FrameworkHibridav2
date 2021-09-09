import os
import AppComposer

# Makes Workload object
WorkloadMM = AppComposer.Workload(WorkloadName = "WorkloadMM")

# Open Application JSON files
H264_60File = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/H264_60.json")

# Get Application files content
H264_60JSONContent = H264_60File.read()

# Build Workload MM Applications
BB_H264_60_A = AppComposer.Application()
BB_H264_60_A.fromJSON(H264_60JSONContent)
BB_H264_60_A.AppName = "MM_H264_60_A"

BB_H264_60_B = AppComposer.Application()
BB_H264_60_B.fromJSON(H264_60JSONContent)
BB_H264_60_B.AppName = "MM_H264_60_B"

# Add Applications to Workload
WorkloadMM.addApplication(BB_H264_60_A)
WorkloadMM.addApplication(BB_H264_60_B)

# Export WorkloadBB to JSON format
WorkloadMM.toJSON(SaveToFile = True, FileName = "WorkloadMM")
