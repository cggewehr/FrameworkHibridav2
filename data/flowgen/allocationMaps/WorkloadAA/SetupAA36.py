import json

DVFSMasterPEPos = 0

# AA workload, running from 2 ms to 3 ms
AAWorkload = [None] * 36
AAWorkload[0] = "AA_VOPD.StripeMem"
AAWorkload[1] = "AA_VOPD.AcdcPred"
AAWorkload[2] = "AA_VOPD.IQuan"
AAWorkload[3] = "AA_VOPD.IDCT"
AAWorkload[4] = "AA_MPEG4_A.RAST"
AAWorkload[5] = "AA_MPEG4_B.RISC"
AAWorkload[6] = "AA_MPEG4_A.ADSP"
AAWorkload[7] = "AA_VOPD.VLD"
AAWorkload[8] = "AA_VOPD.ARM"
AAWorkload[9] = "AA_MPEG4_B.ADSP"
AAWorkload[10] = "AA_MPEG4_A.SRAM2"
AAWorkload[11] = "AA_MPEG4_B.IDCT"
AAWorkload[12] = "AA_MPEG4_A.MedCPU"
AAWorkload[13] = "AA_MPEG4_A.AU"
AAWorkload[14] = "AA_MPEG4_B.AU"
AAWorkload[15] = "AA_MPEG4_B.MedCPU"
AAWorkload[16] = "AA_MPEG4_A.UpSamp"
AAWorkload[17] = "AA_MPEG4_B.BAB"
AAWorkload[18] = "AA_MPEG4_A.SDRAM"
AAWorkload[19] = "AA_MPEG4_A.SRAM1"
AAWorkload[20] = "AA_MPEG4_B.SRAM1"
AAWorkload[21] = "AA_MPEG4_B.SDRAM"
AAWorkload[22] = "AA_VOPD.Pad"
AAWorkload[23] = "AA_MPEG4_B.VU"
AAWorkload[24] = "AA_VOPD.InvScan"
AAWorkload[25] = "AA_VOPD.RunLeDec"
AAWorkload[26] = "AA_VOPD.VopMem"
AAWorkload[27] = "AA_VOPD.VopRec"
AAWorkload[28] = "AA_VOPD.UpSamp"
AAWorkload[29] = "AA_MPEG4_B.RAST"
AAWorkload[30] = "AA_MPEG4_A.VU"
AAWorkload[31] = "AA_MPEG4_A.BAB"
AAWorkload[32] = "AA_MPEG4_A.IDCT"
AAWorkload[33] = "AA_MPEG4_A.RISC"
AAWorkload[34] = "AA_MPEG4_B.UpSamp"
AAWorkload[35] = "AA_MPEG4_B.SRAM2"

# AllocMap[PEPos] = $App.$Thread
AllocMap = [None] * 36

# Merges workload specific allocations into one and adds DVFS source threads
for i in range(0, 36):
    AllocMap[i] = ["DVFSApp.Source" + str(i), AAWorkload[i]]
    
    # Removes all None values from list
    while True:
        try:
            AllocMap[i].remove(None)
        except ValueError:
            break
            
# Adds DVFS master thread (moves "DVFS.Sink" to the front)
AllocMap[DVFSMasterPEPos] = ["DVFSApp.Sink"] + AllocMap[DVFSMasterPEPos]

# Saves Alocation Map to JSON file
with open("SetupAA36.json", "w") as JSONFile:
    JSONFile.write(json.dumps(AllocMap, sort_keys = False, indent = 4))
