import json

DVFSMasterPEPos = 0

# BB workload, running from 0 ms to 1 ms
BBWorkload = [None] * 36
BBWorkload[0] = "BB_H264_30.EntropyEncoder"
BBWorkload[1] = "BB_H264_30.StreamOut"
BBWorkload[2] = "BB_PIP.JUG1"
BBWorkload[3] = "BB_PIP.VS"
BBWorkload[4] = "BB_PIP.HS"
BBWorkload[5] = "BB_PIP.InpMemA"
BBWorkload[6] = "BB_H264_30.IQ"
BBWorkload[7] = "BB_H264_30.IDCT"
BBWorkload[8] = "BB_PIP.OpDisp"
BBWorkload[9] = "BB_PIP.MEM"
BBWorkload[10] = "BB_PIP.JUG2"
BBWorkload[11] = "BB_PIP.InpMemB"
BBWorkload[12] = "BB_H264_30.Quantization"
BBWorkload[13] = "BB_H264_30.SampleHold"
BBWorkload[14] = "BB_H264_30.DeblockingFilter"
BBWorkload[15] = "BB_MWD.MEM2"
BBWorkload[16] = "BB_MWD.NR"
BBWorkload[17] = "BB_MWD.MEM1"
BBWorkload[18] = "BB_H264_30.DCT"
BBWorkload[19] = "BB_H264_30.MotionCompensation"
BBWorkload[20] = "BB_H264_30.Predictor"
BBWorkload[21] = "BB_MWD.HVS"
BBWorkload[22] = "BB_MWD.IN"
BBWorkload[23] = "BB_MWD.HS"
BBWorkload[24] = "BB_H264_30.MVPadding"
BBWorkload[25] = "BB_H264_30.YUVGenerator"
BBWorkload[26] = "BB_H264_30.ChromaResampler"
BBWorkload[27] = "BB_MWD.JUG2"
BBWorkload[28] = "BB_MWD.MEM3"
BBWorkload[29] = "BB_MWD.VS"
BBWorkload[30] = "BB_H264_30.MotionEstimation"
BBWorkload[31] = "BB_H264_30.VideoIn"
BBWorkload[32] = None
BBWorkload[33] = "BB_MWD.Blend"
BBWorkload[34] = "BB_MWD.SE"
BBWorkload[35] = "BB_MWD.JUG1"

# MM workload, running from 1 ms to 2 ms
MMWorkload = [None] * 36
MMWorkload[0] = "MM_H264_60_A.EntropyEncoder"
MMWorkload[1] = "MM_H264_60_A.StreamOut"
MMWorkload[2] = None
MMWorkload[3] = None
MMWorkload[4] = "MM_H264_60_B.StreamOut"
MMWorkload[5] = "MM_H264_60_B.EntropyEncoder"
MMWorkload[6] = "MM_H264_60_A.IQ"
MMWorkload[7] = "MM_H264_60_A.IDCT"
MMWorkload[8] = None
MMWorkload[9] = None
MMWorkload[10] = "MM_H264_60_B.IDCT"
MMWorkload[11] = "MM_H264_60_B.IQ"
MMWorkload[12] = "MM_H264_60_A.Quantization"
MMWorkload[13] = "MM_H264_60_A.SampleHold"
MMWorkload[14] = "MM_H264_60_A.DeblockingFilter"
MMWorkload[15] = "MM_H264_60_B.DeblockingFilter"
MMWorkload[16] = "MM_H264_60_B.SampleHold"
MMWorkload[17] = "MM_H264_60_B.Quantization"
MMWorkload[18] = "MM_H264_60_A.DCT"
MMWorkload[19] = "MM_H264_60_A.MotionCompensation"
MMWorkload[20] = "MM_H264_60_A.Predictor"
MMWorkload[21] = "MM_H264_60_B.Predictor"
MMWorkload[22] = "MM_H264_60_B.MotionCompensation"
MMWorkload[23] = "MM_H264_60_B.DCT"
MMWorkload[24] = "MM_H264_60_A.MVPadding"
MMWorkload[25] = "MM_H264_60_A.YUVGenerator"
MMWorkload[26] = "MM_H264_60_A.ChromaResampler"
MMWorkload[27] = "MM_H264_60_B.ChromaResampler"
MMWorkload[28] = "MM_H264_60_B.YUVGenerator"
MMWorkload[29] = "MM_H264_60_B.MVPadding"
MMWorkload[30] = "MM_H264_60_A.MotionEstimation"
MMWorkload[31] = "MM_H264_60_A.VideoIn"
MMWorkload[32] = None
MMWorkload[33] = None
MMWorkload[34] = "MM_H264_60_B.VideoIn"
MMWorkload[35] = "MM_H264_60_B.MotionEstimation"

# AA workload, running from 2 ms to 3 ms
AAWorkload = [None] * 36
AAWorkload[0] = "AA_MPEG4_A.ADSP"
AAWorkload[1] = "AA_MPEG4_A.BAB"
AAWorkload[2] = "AA_MPEG4_A.RISC"
AAWorkload[3] = "AA_MPEG4_B.ADSP"
AAWorkload[4] = "AA_MPEG4_B.BAB"
AAWorkload[5] = "AA_MPEG4_B.RISC"
AAWorkload[6] = "AA_MPEG4_A.AU"
AAWorkload[7] = "AA_MPEG4_A.IDCT"
AAWorkload[8] = "AA_MPEG4_A.SRAM2"
AAWorkload[9] = "AA_MPEG4_B.AU"
AAWorkload[10] = "AA_MPEG4_B.IDCT"
AAWorkload[11] = "AA_MPEG4_B.SRAM2"
AAWorkload[12] = "AA_MPEG4_A.VU"
AAWorkload[13] = "AA_MPEG4_A.SDRAM"
AAWorkload[14] = "AA_MPEG4_A.UpSamp"
AAWorkload[15] = "AA_MPEG4_B.VU"
AAWorkload[16] = "AA_MPEG4_B.SDRAM"
AAWorkload[17] = "AA_MPEG4_B.UpSamp"
AAWorkload[18] = "AA_MPEG4_A.SRAM1"
AAWorkload[19] = "AA_MPEG4_A.RAST"
AAWorkload[20] = "AA_MPEG4_A.MedCPU"
AAWorkload[21] = "AA_MPEG4_B.SRAM1"
AAWorkload[22] = "AA_MPEG4_B.RAST"
AAWorkload[23] = "AA_MPEG4_B.MedCPU"
AAWorkload[24] = "AA_VOPD.ARM"
AAWorkload[25] = "AA_VOPD.VopRec"
AAWorkload[26] = "AA_VOPD.VopMem"
AAWorkload[27] = "AA_VOPD.StripeMem"
AAWorkload[28] = "AA_VOPD.InvScan"
AAWorkload[29] = "AA_VOPD.RunLeDec"
AAWorkload[30] = "AA_VOPD.Pad"
AAWorkload[31] = "AA_VOPD.UpSamp"
AAWorkload[32] = "AA_VOPD.IDCT"
AAWorkload[33] = "AA_VOPD.IQuan"
AAWorkload[34] = "AA_VOPD.AcdcPred"
AAWorkload[35] = "AA_VOPD.VLD"

# HH workload, running from 3 ms to 4 ms
HHWorkload = [None] * 36
HHWorkload[0] = "HH_H264_60.EntropyEncoder"
HHWorkload[1] = "HH_H264_60.StreamOut"
HHWorkload[2] = "HH_PIP.JUG1"
HHWorkload[3] = "HH_PIP.VS"
HHWorkload[4] = "HH_PIP.HS"
HHWorkload[5] = "HH_PIP.InpMemA"
HHWorkload[6] = "HH_H264_60.IQ"
HHWorkload[7] = "HH_H264_60.IDCT"
HHWorkload[8] = "HH_PIP.OpDisp"
HHWorkload[9] = "HH_PIP.MEM"
HHWorkload[10] = "HH_PIP.JUG2"
HHWorkload[11] = "HH_PIP.InpMemB"
HHWorkload[12] = "HH_H264_60.Quantization"
HHWorkload[13] = "HH_H264_60.SampleHold"
HHWorkload[14] = "HH_H264_60.DeblockingFilter"
HHWorkload[15] = "HH_MPEG4.ADSP"
HHWorkload[16] = "HH_MPEG4.BAB"
HHWorkload[17] = "HH_MPEG4.RISC"
HHWorkload[18] = "HH_H264_60.DCT"
HHWorkload[19] = "HH_H264_60.MotionCompensation"
HHWorkload[20] = "HH_H264_60.Predictor"
HHWorkload[21] = "HH_MPEG4.AU"
HHWorkload[22] = "HH_MPEG4.IDCT"
HHWorkload[23] = "HH_MPEG4.SRAM2"
HHWorkload[24] = "HH_H264_60.MVPadding"
HHWorkload[25] = "HH_H264_60.YUVGenerator"
HHWorkload[26] = "HH_H264_60.ChromaResampler"
HHWorkload[27] = "HH_MPEG4.VU"
HHWorkload[28] = "HH_MPEG4.SDRAM"
HHWorkload[29] = "HH_MPEG4.UpSamp"
HHWorkload[30] = "HH_H264_60.MotionEstimation"
HHWorkload[31] = "HH_H264_60.VideoIn"
HHWorkload[32] = None
HHWorkload[33] = "HH_MPEG4.SRAM1"
HHWorkload[34] = "HH_MPEG4.RAST"
HHWorkload[35] = "HH_MPEG4.MedCPU"

# AllocMap[PEPos] = $App.$Thread
AllocMap = [None] * 36

# Merges workload specific allocations into one and adds DVFS slave threads
for i in range(0, 36):
    AllocMap[i] = ["DVFSApp.Slave" + str(i), BBWorkload[i], MMWorkload[i], AAWorkload[i], HHWorkload[i]]
    
    # Removes all None values from list
    while True:
        try:
            AllocMap[i].remove(None)
        except ValueError:
            break
            
# Adds DVFS master thread (moves "DVFSMaster" to the front)
AllocMap[DVFSMasterPEPos] = ["DVFSApp.Master"] + AllocMap[DVFSMasterPEPos]

# Saves Alocation Map to JSON file
with open("Hermes36.json", "w") as JSONFile:
    JSONFile.write(json.dumps(AllocMap, sort_keys = False, indent = 4))
