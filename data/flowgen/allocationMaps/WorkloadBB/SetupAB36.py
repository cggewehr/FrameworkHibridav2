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
BBWorkload[10] = "BB_PIP.InpMemA"
BBWorkload[11] = "BB_H264_30.EntropyEncoder"
BBWorkload[12] = "BB_MWD.Blend"
BBWorkload[13] = "BB_H264_30.DeblockingFilter"
BBWorkload[14] = "BB_H264_30.SampleHold"
BBWorkload[15] = "BB_H264_30.MotionEstimation"
BBWorkload[16] = "BB_PIP.HS"
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
with open("SetupAB36.json", "w") as JSONFile:
    JSONFile.write(json.dumps(AllocMap, sort_keys = False, indent = 4))
