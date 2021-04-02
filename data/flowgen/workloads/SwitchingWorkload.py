import os
import AppComposer

# Makes Workload object
SwitchingWorkload = AppComposer.Workload(WorkloadName = "SwitchingWorkload")

# Workload BB: MWD PIP H264-30 (0 to 1 ms)
# Workload MM: 2xH264-60 (1 to 2 ms)
# Workload AA: 2xMPEG4 VOPD (2 to 3 ms)
# Workload HH: PIP H264-60 MPEG4 (3 to 4 ms)

# TODO: Set StartTime and StopTime for every Application

# Open Application JSON files
PIPFile = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/PIP.json")
MWDFile = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/MWD.json")
VOPDFile = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/VOPD.json")
MPEG4File = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/MPEG4.json")
H264_60File = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/H264_60.json")
H264_30File = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/H264_30.json")

# Get Application files content
PIPJSONContent = PIPFile.read()
MWDJSONContent = MWDFile.read()
VOPDJSONContent = VOPDFile.read()
MPEG4JSONContent = MPEG4File.read()
H264_60JSONContent = H264_60File.read()
H264_30JSONContent = H264_30File.read()

# Build Workload BB (0 to 1 ms)
BB_PIP = AppComposer.Application()
BB_PIP.fromJSON(PIPJSONContent)
BB_PIP.AppName = "BB_PIP"

BB_MWD = AppComposer.Application()
BB_MWD.fromJSON(MWDJSONContent)
BB_MWD.AppName = "BB_MWD"

BB_H264_30 = AppComposer.Application()
BB_H264_30.fromJSON(H264_30JSONContent)
BB_H264_30.AppName = "BB_H264_30"

SwitchingWorkload.addApplication(BB_PIP)
SwitchingWorkload.addApplication(BB_MWD)
SwitchingWorkload.addApplication(BB_H264_30)

# Build Workload MM (1 to 2 ms)
MM_H264_60_A = AppComposer.Application()
MM_H264_60_A.fromJSON(H264_30JSONContent)
MM_H264_60_A.AppName = "MM_H264_60_A"

MM_H264_60_B = AppComposer.Application()
MM_H264_60_B.fromJSON(H264_30JSONContent)
MM_H264_60_B.AppName = "MM_H264_60_B"

SwitchingWorkload.addApplication(MM_H264_60_A)
SwitchingWorkload.addApplication(MM_H264_60_B)

# Build Workload AA (2 to 3 ms)
AA_MPEG4_A = AppComposer.Application()
AA_MPEG4_A.fromJSON(MPEG4JSONContent)
AA_MPEG4_A.AppName = "AA_MPEG4_A"

AA_MPEG4_B = AppComposer.Application()
AA_MPEG4_B.fromJSON(MPEG4JSONContent)
AA_MPEG4_B.AppName = "AA_MPEG4_B"

AA_VOPD = AppComposer.Application()
AA_VOPD.fromJSON(VOPDJSONContent)
AA_VOPD.AppName = "AA_VOPD"

SwitchingWorkload.addApplication(AA_MPEG4_A)
SwitchingWorkload.addApplication(AA_MPEG4_B)
SwitchingWorkload.addApplication(AA_VOPD)

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

SwitchingWorkload.addApplication(HH_PIP)
SwitchingWorkload.addApplication(HH_H264_60)
SwitchingWorkload.addApplication(HH_MPEG4)

# Close Application JSON files
PIPFile.close()
MWDFile.close()
VOPDFile.close()
MPEG4File.close()
H264_60File.close()
H264_30File.close()

# Exports Workload to json format
SwitchingWorkload.toJSON(SaveToFile = True, FileName = "SwitchingWorkload")