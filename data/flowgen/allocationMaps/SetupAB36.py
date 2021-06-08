import json

DVFSMasterPEPos = 0

# BB workload, running from 0 ms to 1 ms
BBWorkload = [None] * 36
BBWorkload[0] = "BB_MWD.JUG1"
BBWorkload[1] = "BB_MWD.VS"
BBWorkload[2] = "BB_MWD.IN"
BBWorkload[3] = "BB_MWD.MEM2"
BBWorkload[4] = "BB_PIP.VS"
BBWorkload[5] = "BB_H264_30.StreamOut"
BBWorkload[6] = "BB_MWD.SE"
BBWorkload[7] = "BB_MWD.MEM3"
BBWorkload[8] = "BB_MWD.JUG2"
BBWorkload[9] = "BB_MWD.HVS"
BBWorkload[10] = "BB_PIP.HS"
BBWorkload[11] = "BB_H264_30.EntropyEncoder"
BBWorkload[12] = "BB_MWD.Blend"
BBWorkload[13] = "BB_H264_30.DeblockingFilter"
BBWorkload[14] = "BB_H264_30.SampleHold"
BBWorkload[15] = "BB_H264_30.MotionEstimation"
BBWorkload[16] = "BB_PIP.InpMemA"
BBWorkload[17] = "BB_H264_30.IDCT"
BBWorkload[18] = "BB_H264_30.DCT"
BBWorkload[19] = "BB_H264_30.Predictor"
BBWorkload[20] = "BB_H264_30.VideoIn"
BBWorkload[21] = "BB_H264_30.MVPadding"
BBWorkload[22] = None
BBWorkload[23] = "BB_H264_30.IQ"
BBWorkload[24] = "BB_PIP.JUG1"
BBWorkload[25] = "BB_PIP.InpMemB"
BBWorkload[26] = "BB_PIP.JUG2"
BBWorkload[27] = "BB_PIP.MEM"
BBWorkload[28] = "BB_PIP.OpDisp"
BBWorkload[29] = "BB_H264_30.Quantization"
BBWorkload[30] = "BB_MWD.HS"
BBWorkload[31] = "BB_MWD.NR"
BBWorkload[32] = "BB_MWD.MEM1"
BBWorkload[33] = "BB_H264_30.YUVGenerator"
BBWorkload[34] = "BB_H264_30.ChromaResampler"
BBWorkload[35] = "BB_H264_30.MotionCompensation"

# MM workload, running from 1 ms to 2 ms
MMWorkload = [None] * 36
MMWorkload[0] = None
MMWorkload[1] = "MM_H264_60_B.MVPadding"
MMWorkload[2] = "MM_H264_60_B.VideoIn"
MMWorkload[3] = "MM_H264_60_B.Predictor"
MMWorkload[4] = "MM_H264_60_B.DCT"
MMWorkload[5] = "MM_H264_60_A.StreamOut"
MMWorkload[6] = None
MMWorkload[7] = "MM_H264_60_B.MotionEstimation"
MMWorkload[8] = "MM_H264_60_B.SampleHold"
MMWorkload[9] = "MM_H264_60_B.DeblockingFilter"
MMWorkload[10] = None
MMWorkload[11] = "MM_H264_60_A.EntropyEncoder"
MMWorkload[12] = None
MMWorkload[13] = "MM_H264_60_A.DeblockingFilter"
MMWorkload[14] = "MM_H264_60_A.SampleHold"
MMWorkload[15] = "MM_H264_60_A.MotionEstimation"
MMWorkload[16] = None
MMWorkload[17] = "MM_H264_60_A.IDCT"
MMWorkload[18] = "MM_H264_60_A.DCT"
MMWorkload[19] = "MM_H264_60_A.Predictor"
MMWorkload[20] = "MM_H264_60_A.VideoIn"
MMWorkload[21] = "MM_H264_60_A.MVPadding"
MMWorkload[22] = None
MMWorkload[23] = "MM_H264_60_A.IQ"
MMWorkload[24] = "MM_H264_60_B.Quantization"
MMWorkload[25] = "MM_H264_60_B.IQ"
MMWorkload[26] = "MM_H264_60_B.IDCT"
MMWorkload[27] = "MM_H264_60_B.EntropyEncoder"
MMWorkload[28] = "MM_H264_60_B.StreamOut"
MMWorkload[29] = "MM_H264_60_A.Quantization"
MMWorkload[30] = "MM_H264_60_B.YUVGenerator"
MMWorkload[31] = "MM_H264_60_B.ChromaResampler"
MMWorkload[32] = "MM_H264_60_B.MotionCompensation"
MMWorkload[33] = "MM_H264_60_A.YUVGenerator"
MMWorkload[34] = "MM_H264_60_A.ChromaResampler"
MMWorkload[35] = "MM_H264_60_A.MotionCompensation"

# AA workload, running from 2 ms to 3 ms
AAWorkload = [None] * 36
AAWorkload[0] = "AA_VOPD.VLD"
AAWorkload[1] = "AA_MPEG4_A.IDCT"
AAWorkload[2] = "AA_MPEG4_A.SDRAM"
AAWorkload[3] = "AA_MPEG4_A.RISC"
AAWorkload[4] = "AA_MPEG4_A.AU"
AAWorkload[5] = "AA_MPEG4_B.BAB"
AAWorkload[6] = "AA_VOPD.RunLeDec"
AAWorkload[7] = "AA_VOPD.StripeMem"
AAWorkload[8] = "AA_VOPD.IDCT"
AAWorkload[9] = "AA_VOPD.UpSamp"
AAWorkload[10] = "AA_VOPD.VopRec"
AAWorkload[11] = "AA_MPEG4_B.SRAM1"
AAWorkload[12] = "AA_VOPD.InvScan"
AAWorkload[13] = "AA_VOPD.AcdcPred"
AAWorkload[14] = "AA_VOPD.IQuan"
AAWorkload[15] = "AA_VOPD.Pad"
AAWorkload[16] = "AA_VOPD.VopMem"
AAWorkload[17] = "AA_MPEG4_B.MedCPU"
AAWorkload[18] = "AA_MPEG4_B.AU"
AAWorkload[19] = "AA_MPEG4_B.IDCT"
AAWorkload[20] = "AA_MPEG4_B.SDRAM"
AAWorkload[21] = "AA_MPEG4_B.RISC"
AAWorkload[22] = "AA_VOPD.ARM"
AAWorkload[23] = "AA_MPEG4_B.ADSP"
AAWorkload[24] = "AA_MPEG4_A.VU"
AAWorkload[25] = "AA_MPEG4_A.ADSP"
AAWorkload[26] = "AA_MPEG4_A.MedCPU"
AAWorkload[27] = "AA_MPEG4_A.SRAM1"
AAWorkload[28] = "AA_MPEG4_A.BAB"
AAWorkload[29] = "AA_MPEG4_B.VU"
AAWorkload[30] = "AA_MPEG4_A.UpSamp"
AAWorkload[31] = "AA_MPEG4_A.SRAM2"
AAWorkload[32] = "AA_MPEG4_A.RAST"
AAWorkload[33] = "AA_MPEG4_B.UpSamp"
AAWorkload[34] = "AA_MPEG4_B.SRAM2"
AAWorkload[35] = "AA_MPEG4_B.RAST"

# HH workload, running from 3 ms to 4 ms
HHWorkload = [None] * 36
HHWorkload[0] = "HH_PIP.InpMemA"
HHWorkload[1] = "HH_H264_60.MVPadding"
HHWorkload[2] = "HH_H264_60.VideoIn"
HHWorkload[3] = "HH_H264_60.Predictor"
HHWorkload[4] = "HH_H264_60.DCT"
HHWorkload[5] = "HH_MPEG4.BAB"
HHWorkload[6] = "HH_PIP.HS"
HHWorkload[7] = "HH_H264_60.MotionEstimation"
HHWorkload[8] = "HH_H264_60.SampleHold"
HHWorkload[9] = "HH_H264_60.DeblockingFilter"
HHWorkload[10] = "HH_PIP.OpDisp"
HHWorkload[11] = "HH_MPEG4.SRAM1"
HHWorkload[12] = "HH_PIP.InpMemB"
HHWorkload[13] = "HH_PIP.VS"
HHWorkload[14] = "HH_PIP.JUG2"
HHWorkload[15] = "HH_PIP.JUG1"
HHWorkload[16] = "HH_PIP.MEM"
HHWorkload[17] = "HH_MPEG4.MedCPU"
HHWorkload[18] = "HH_MPEG4.AU"
HHWorkload[19] = "HH_MPEG4.IDCT"
HHWorkload[20] = "HH_MPEG4.SDRAM"
HHWorkload[21] = "HH_MPEG4.RISC"
HHWorkload[22] = None
HHWorkload[23] = "HH_MPEG4.ADSP"
HHWorkload[24] = "HH_H264_60.Quantization"
HHWorkload[25] = "HH_H264_60.IQ"
HHWorkload[26] = "HH_H264_60.IDCT"
HHWorkload[27] = "HH_H264_60.EntropyEncoder"
HHWorkload[28] = "HH_H264_60.StreamOut"
HHWorkload[29] = "HH_MPEG4.VU"
HHWorkload[30] = "HH_H264_60.YUVGenerator"
HHWorkload[31] = "HH_H264_60.ChromaResampler"
HHWorkload[32] = "HH_H264_60.MotionCompensation"
HHWorkload[33] = "HH_MPEG4.UpSamp"
HHWorkload[34] = "HH_MPEG4.SRAM2"
HHWorkload[35] = "HH_MPEG4.RAST"

# AllocMap[PEPos] = $App.$Thread
AllocMap = [None] * 36

# Merges workload specific allocations into one and adds DVFS source threads
for i in range(0, 36):
    AllocMap[i] = ["DVFSApp.Source" + str(i), BBWorkload[i], MMWorkload[i], AAWorkload[i], HHWorkload[i]]
    
    # Removes all None values from list
    while True:
        try:
            AllocMap[i].remove(None)
        except ValueError:
            break
            
# Adds DVFS master thread (moves "DVFS.Sink" to the front)
AllocMap[DVFSMasterPEPos] = ["DVFSApp.Sink"] + AllocMap[DVFSMasterPEPos]

# Saves Alocation Map to JSON file
with open("SetupAB36.json", "w") as JSONFile:
    JSONFile.write(json.dumps(AllocMap, sort_keys = False, indent = 4))
