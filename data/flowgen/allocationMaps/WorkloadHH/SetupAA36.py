import json

DVFSMasterPEPos = 0

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
    AllocMap[i] = ["DVFSApp.Source" + str(i), HHWorkload[i]]
    
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
