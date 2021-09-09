import os
import AppComposer

# Makes Workload object
WorkloadHH = AppComposer.Workload(WorkloadName = "WorkloadHH")

# Open Application JSON files
PIPFile = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/PIP.json")
MPEG4File = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/MPEG4.json")
H264_60File = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/H264_60.json")

# Get Application files content
PIPJSONContent = PIPFile.read()
MPEG4JSONContent = MPEG4File.read()
H264_60JSONContent = H264_60File.read()

# Build Workload HH (3 to 4 ms)
HH_PIP = AppComposer.Application()
HH_PIP.fromJSON(PIPJSONContent)
HH_PIP.AppName = "HH_PIP"

HH_H264_60 = AppComposer.Application()
HH_H264_60.fromJSON(H264_60JSONContent)
HH_H264_60.AppName = "HH_H264_60"

HH_MPEG4 = AppComposer.Application()
HH_MPEG4.fromJSON(MPEG4JSONContent)
HH_MPEG4.AppName = "HH_MPEG4"

# Add Applications to Workload
WorkloadHH.addApplication(HH_PIP)
WorkloadHH.addApplication(HH_H264_60)
WorkloadHH.addApplication(HH_MPEG4)

# Export Workload HH to JSON format
WorkloadHH.toJSON(SaveToFile = True, FileName = "WorkloadHH")

