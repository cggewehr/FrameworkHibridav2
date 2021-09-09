import json

DVFSMasterPEPos = 0

# HH workload, running from 3 ms to 4 ms
HHWorkload = [None] * 36
HHWorkload[0] = "HH_PIP.InpMemB"
HHWorkload[1] = "HH_PIP.JUG2"
HHWorkload[2] = "HH_PIP.MEM"
HHWorkload[3] = "HH_PIP.OpDisp"
HHWorkload[4] = "HH_MPEG4.RAST"
HHWorkload[5] = "HH_H264_60.Predictor"
HHWorkload[6] = "HH_MPEG4.AU"
HHWorkload[7] = "HH_PIP.VS"
HHWorkload[8] = "HH_PIP.JUG1"
HHWorkload[9] = "HH_H264_60.IQ"
HHWorkload[10] = "HH_MPEG4.SRAM2"
HHWorkload[11] = "HH_H264_60.DCT"
HHWorkload[12] = "HH_MPEG4.MedCPU"
HHWorkload[13] = None
HHWorkload[14] = "HH_H264_60.DeblockingFilter"
HHWorkload[15] = "HH_H264_60.Quantization"
HHWorkload[16] = "HH_MPEG4.UpSamp"
HHWorkload[17] = "HH_H264_60.MotionEstimation"
HHWorkload[18] = "HH_MPEG4.SDRAM"
HHWorkload[19] = "HH_MPEG4.SRAM1"
HHWorkload[20] = "HH_H264_60.SampleHold"
HHWorkload[21] = "HH_H264_60.VideoIn"
HHWorkload[22] = "HH_H264_60.StreamOut"
HHWorkload[23] = "HH_H264_60.MVPadding"
HHWorkload[24] = "HH_MPEG4.ADSP"
HHWorkload[25] = "HH_PIP.InpMemA"
HHWorkload[26] = "HH_PIP.HS"
HHWorkload[27] = "HH_H264_60.IDCT"
HHWorkload[28] = "HH_H264_60.EntropyEncoder"
HHWorkload[29] = "HH_H264_60.MotionCompensation"
HHWorkload[30] = "HH_MPEG4.VU"
HHWorkload[31] = "HH_MPEG4.BAB"
HHWorkload[32] = "HH_MPEG4.IDCT"
HHWorkload[33] = "HH_MPEG4.RISC"
HHWorkload[34] = "HH_H264_60.YUVGenerator"
HHWorkload[35] = "HH_H264_60.ChromaResampler"

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
with open("SetupBA36.json", "w") as JSONFile:
    JSONFile.write(json.dumps(AllocMap, sort_keys = False, indent = 4))
