import json

DVFSMasterPEPos = 0

# BB workload, running from 0 ms to 1 ms
BBWorkload = [None] * 36
BBWorkload[0] = "BB_MWD.HVS"
BBWorkload[1] = None
BBWorkload[2] = "BB_PIP.OpDisp"
BBWorkload[3] = "BB_PIP.InpMemA"
BBWorkload[4] = "BB_MWD.MEM1"
BBWorkload[5] = "BB_H264_30.Predictor"
BBWorkload[6] = "BB_MWD.MEM2"
BBWorkload[7] = "BB_MWD.Blend"
BBWorkload[8] = "BB_H264_30.IDCT"
BBWorkload[9] = "BB_H264_30.IQ"
BBWorkload[10] = "BB_MWD.NR"
BBWorkload[11] = "BB_H264_30.MotionEstimation"
BBWorkload[12] = "BB_MWD.SE"
BBWorkload[13] = "BB_H264_30.StreamOut"
BBWorkload[14] = "BB_H264_30.EntropyEncoder"
BBWorkload[15] = "BB_H264_30.Quantization"
BBWorkload[16] = "BB_MWD.HS"
BBWorkload[17] = "BB_H264_30.DCT"
BBWorkload[18] = "BB_MWD.IN"
BBWorkload[19] = "BB_H264_30.DeblockingFilter"
BBWorkload[20] = "BB_H264_30.SampleHold"
BBWorkload[21] = "BB_H264_30.VideoIn"
BBWorkload[22] = "BB_PIP.MEM"
BBWorkload[23] = "BB_H264_30.MVPadding"
BBWorkload[24] = "BB_PIP.HS"
BBWorkload[25] = "BB_PIP.VS"
BBWorkload[26] = "BB_PIP.JUG1"
BBWorkload[27] = "BB_PIP.InpMemB"
BBWorkload[28] = "BB_PIP.JUG2"
BBWorkload[29] = "BB_H264_30.MotionCompensation"
BBWorkload[30] = "BB_MWD.VS"
BBWorkload[31] = "BB_MWD.JUG1"
BBWorkload[32] = "BB_MWD.MEM3"
BBWorkload[33] = "BB_MWD.JUG2"
BBWorkload[34] = "BB_H264_30.YUVGenerator"
BBWorkload[35] = "BB_H264_30.ChromaResampler"

# MM workload, running from 1 ms to 2 ms
MMWorkload = [None] * 36
MMWorkload[0] = None
MMWorkload[1] = None
MMWorkload[2] = None
MMWorkload[3] = "MM_H264_60_B.IDCT"
MMWorkload[4] = "MM_H264_60_A.MotionCompensation"
MMWorkload[5] = "MM_H264_60_B.Predictor"
MMWorkload[6] = "MM_H264_60_A.DeblockingFilter"
MMWorkload[7] = "MM_H264_60_A.StreamOut"
MMWorkload[8] = None
MMWorkload[9] = "MM_H264_60_B.DeblockingFilter"
MMWorkload[10] = "MM_H264_60_A.ChromaResampler"
MMWorkload[11] = "MM_H264_60_B.DCT"
MMWorkload[12] = "MM_H264_60_A.SampleHold"
MMWorkload[13] = "MM_H264_60_A.EntropyEncoder"
MMWorkload[14] = "MM_H264_60_A.IDCT"
MMWorkload[15] = "MM_H264_60_B.SampleHold"
MMWorkload[16] = "MM_H264_60_A.YUVGenerator"
MMWorkload[17] = "MM_H264_60_B.MotionEstimation"
MMWorkload[18] = "MM_H264_60_A.VideoIn"
MMWorkload[19] = "MM_H264_60_A.Quantization"
MMWorkload[20] = "MM_H264_60_A.IQ"
MMWorkload[21] = "MM_H264_60_B.VideoIn"
MMWorkload[22] = None
MMWorkload[23] = "MM_H264_60_B.MVPadding"
MMWorkload[24] = "MM_H264_60_B.Quantization"
MMWorkload[25] = "MM_H264_60_B.IQ"
MMWorkload[26] = "MM_H264_60_B.StreamOut"
MMWorkload[27] = "MM_H264_60_B.EntropyEncoder"
MMWorkload[28] = None
MMWorkload[29] = "MM_H264_60_B.MotionCompensation"
MMWorkload[30] = "MM_H264_60_A.MVPadding"
MMWorkload[31] = "MM_H264_60_A.MotionEstimation"
MMWorkload[32] = "MM_H264_60_A.DCT"
MMWorkload[33] = "MM_H264_60_A.Predictor"
MMWorkload[34] = "MM_H264_60_B.YUVGenerator"
MMWorkload[35] = "MM_H264_60_B.ChromaResampler"

# AA workload, running from 2 ms to 3 ms
AAWorkload = [None] * 36
AAWorkload[0] = "AA_VOPD.ARM"
AAWorkload[1] = "AA_VOPD.StripeMem"
AAWorkload[2] = "AA_VOPD.UpSamp"
AAWorkload[3] = "AA_VOPD.AcdcPred"
AAWorkload[4] = "AA_MPEG4_A.RAST"
AAWorkload[5] = "AA_MPEG4_B.RISC"
AAWorkload[6] = "AA_MPEG4_A.ADSP"
AAWorkload[7] = "AA_VOPD.VLD"
AAWorkload[8] = "AA_VOPD.IDCT"
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
AAWorkload[28] = "AA_VOPD.IQuan"
AAWorkload[29] = "AA_MPEG4_B.RAST"
AAWorkload[30] = "AA_MPEG4_A.VU"
AAWorkload[31] = "AA_MPEG4_A.BAB"
AAWorkload[32] = "AA_MPEG4_A.IDCT"
AAWorkload[33] = "AA_MPEG4_A.RISC"
AAWorkload[34] = "AA_MPEG4_B.UpSamp"
AAWorkload[35] = "AA_MPEG4_B.SRAM2"

# HH workload, running from 3 ms to 4 ms
HHWorkload = [None] * 36
HHWorkload[0] = "HH_H264_60.IQ"
HHWorkload[1] = "HH_H264_60.IDCT"
HHWorkload[2] = "HH_PIP.OpDisp"
HHWorkload[3] = "HH_PIP.InpMemA"
HHWorkload[4] = "HH_H264_60.MotionCompensation"
HHWorkload[5] = "HH_MPEG4.RISC"
HHWorkload[6] = "HH_H264_60.Quantization"
HHWorkload[7] = "HH_H264_60.EntropyEncoder"
HHWorkload[8] = None
HHWorkload[9] = "HH_MPEG4.ADSP"
HHWorkload[10] = "HH_H264_60.ChromaResampler"
HHWorkload[11] = "HH_MPEG4.IDCT"
HHWorkload[12] = "HH_H264_60.SampleHold"
HHWorkload[13] = "HH_H264_60.StreamOut"
HHWorkload[14] = "HH_MPEG4.AU"
HHWorkload[15] = "HH_MPEG4.MedCPU"
HHWorkload[16] = "HH_H264_60.YUVGenerator"
HHWorkload[17] = "HH_MPEG4.BAB"
HHWorkload[18] = "HH_H264_60.VideoIn"
HHWorkload[19] = "HH_H264_60.DeblockingFilter"
HHWorkload[20] = "HH_MPEG4.SRAM1"
HHWorkload[21] = "HH_MPEG4.SDRAM"
HHWorkload[22] = "HH_PIP.MEM"
HHWorkload[23] = "HH_MPEG4.VU"
HHWorkload[24] = "HH_PIP.HS"
HHWorkload[25] = "HH_PIP.VS"
HHWorkload[26] = "HH_PIP.JUG1"
HHWorkload[27] = "HH_PIP.InpMemB"
HHWorkload[28] = "HH_PIP.JUG2"
HHWorkload[29] = "HH_MPEG4.RAST"
HHWorkload[30] = "HH_H264_60.MVPadding"
HHWorkload[31] = "HH_H264_60.MotionEstimation"
HHWorkload[32] = "HH_H264_60.DCT"
HHWorkload[33] = "HH_H264_60.Predictor"
HHWorkload[34] = "HH_MPEG4.UpSamp"
HHWorkload[35] = "HH_MPEG4.SRAM2"

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
with open("SetupAA36.json", "w") as JSONFile:
    JSONFile.write(json.dumps(AllocMap, sort_keys = False, indent = 4))
