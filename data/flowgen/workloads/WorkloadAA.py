import os
import AppComposer

# Makes Workload object
WorkloadAA = AppComposer.Workload(WorkloadName = "WorkloadAA")

# Open Application JSON files
VOPDFile = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/VOPD.json")
MPEG4File = open(os.getenv("HIBRIDA_PATH") + "/data/flowgen/applications/MPEG4.json")

# Get Application files content
VOPDJSONContent = VOPDFile.read()
MPEG4JSONContent = MPEG4File.read()

# Build Workload AA
AA_MPEG4_A = AppComposer.Application()
AA_MPEG4_A.fromJSON(MPEG4JSONContent)
AA_MPEG4_A.AppName = "AA_MPEG4_A"

AA_MPEG4_B = AppComposer.Application()
AA_MPEG4_B.fromJSON(MPEG4JSONContent)
AA_MPEG4_B.AppName = "AA_MPEG4_B"

AA_VOPD = AppComposer.Application()
AA_VOPD.fromJSON(VOPDJSONContent)
AA_VOPD.AppName = "AA_VOPD"

# Add Applications to Workload
WorkloadAA.addApplication(AA_MPEG4_A)
WorkloadAA.addApplication(AA_MPEG4_B)
WorkloadAA.addApplication(AA_VOPD)

# Export Workload AA to JSON format
WorkloadAA.toJSON(SaveToFile = True, FileName = "WorkloadAA")
