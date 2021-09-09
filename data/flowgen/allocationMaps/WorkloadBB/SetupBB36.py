import json

DVFSMasterPEPos = 0

# BB workload, running from 0 ms to 1 ms
BBWorkload = [None] * 36
BBWorkload[0] = "BB_PIP.InpMemA"
BBWorkload[1] = "BB_PIP.HS"
BBWorkload[2] = None
BBWorkload[3] = "BB_H264_30.MVPadding"
BBWorkload[4] = "BB_H264_30.VideoIn"
BBWorkload[5] = "BB_H264_30.StreamOut"
BBWorkload[6] = "BB_PIP.JUG1"
BBWorkload[7] = "BB_PIP.VS"
BBWorkload[8] = "BB_H264_30.ChromaResampler"
BBWorkload[9] = "BB_H264_30.YUVGenerator"
BBWorkload[10] = "BB_H264_30.MotionEstimation"
BBWorkload[11] = "BB_H264_30.EntropyEncoder"
BBWorkload[12] = "BB_MWD.SE"
BBWorkload[13] = "BB_MWD.VS"
BBWorkload[14] = "BB_MWD.HS"
BBWorkload[15] = "BB_H264_30.MotionCompensation"
BBWorkload[16] = "BB_H264_30.DCT"
BBWorkload[17] = "BB_H264_30.Predictor"
BBWorkload[18] = "BB_MWD.MEM3"
BBWorkload[19] = "BB_MWD.JUG1"
BBWorkload[20] = "BB_MWD.IN"
BBWorkload[21] = "BB_H264_30.SampleHold"
BBWorkload[22] = "BB_H264_30.DeblockingFilter"
BBWorkload[23] = "BB_H264_30.IDCT"
BBWorkload[24] = "BB_MWD.JUG2"
BBWorkload[25] = "BB_MWD.HVS"
BBWorkload[26] = "BB_MWD.MEM2"
BBWorkload[27] = "BB_MWD.NR"
BBWorkload[28] = "BB_MWD.MEM1"
BBWorkload[29] = "BB_H264_30.IQ"
BBWorkload[30] = "BB_MWD.Blend"
BBWorkload[31] = "BB_PIP.InpMemB"
BBWorkload[32] = "BB_PIP.JUG2"
BBWorkload[33] = "BB_PIP.MEM"
BBWorkload[34] = "BB_PIP.OpDisp"
BBWorkload[35] = "BB_H264_30.Quantization"

# AllocMap[PEPos] = $App.$Thread
AllocMap = [None] * 36

# Merges workload specific allocations into one and adds DVFS source threads
for i in range(0, 36):
    AllocMap[i] = ["DVFSApp.Source" + str(i), BBWorkload[i]]
    
    # Removes all None values from list
    while True:
        try:
            AllocMap[i].remove(None)
        except ValueError:
            break
            
# Adds DVFS master thread (moves "DVFS.Sink" to the front)
AllocMap[DVFSMasterPEPos] = ["DVFSApp.Sink"] + AllocMap[DVFSMasterPEPos]

# Saves Alocation Map to JSON file
with open("SetupBB36.json", "w") as JSONFile:
    JSONFile.write(json.dumps(AllocMap, sort_keys = False, indent = 4))
