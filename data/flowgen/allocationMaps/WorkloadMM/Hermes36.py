import json

DVFSMasterPEPos = 0

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
MMWorkload[13] = "MM_H264_60_A.Predictor"
MMWorkload[14] = "MM_H264_60_A.DeblockingFilter"
MMWorkload[15] = "MM_H264_60_B.DeblockingFilter"
MMWorkload[16] = "MM_H264_60_B.Predictor"
MMWorkload[17] = "MM_H264_60_B.Quantization"
MMWorkload[18] = "MM_H264_60_A.DCT"
MMWorkload[19] = "MM_H264_60_A.MotionCompensation"
MMWorkload[20] = "MM_H264_60_A.SampleHold"
MMWorkload[21] = "MM_H264_60_B.SampleHold"
MMWorkload[22] = "MM_H264_60_B.MotionCompensation"
MMWorkload[23] = "MM_H264_60_B.DCT"
MMWorkload[24] = "MM_H264_60_A.MotionEstimation"
MMWorkload[25] = "MM_H264_60_A.YUVGenerator"
MMWorkload[26] = "MM_H264_60_A.ChromaResampler"
MMWorkload[27] = "MM_H264_60_B.ChromaResampler"
MMWorkload[28] = "MM_H264_60_B.YUVGenerator"
MMWorkload[29] = "MM_H264_60_B.MotionEstimation"
MMWorkload[30] = "MM_H264_60_A.VideoIn"
MMWorkload[31] = "MM_H264_60_A.MVPadding"
MMWorkload[32] = None
MMWorkload[33] = None
MMWorkload[34] = "MM_H264_60_B.MVPadding"
MMWorkload[35] = "MM_H264_60_B.VideoIn"

# AllocMap[PEPos] = $App.$Thread
AllocMap = [None] * 36

# Merges workload specific allocations into one and adds DVFS source threads
for i in range(0, 36):
    AllocMap[i] = ["DVFSApp.Source" + str(i), MMWorkload[i]]
    
    # Removes all None values from list
    while True:
        try:
            AllocMap[i].remove(None)
        except ValueError:
            break
            
# Adds DVFS master thread (moves "DVFS.Sink" to the front)
AllocMap[DVFSMasterPEPos] = ["DVFSApp.Sink"] + AllocMap[DVFSMasterPEPos]

# Saves Alocation Map to JSON file
with open("Hermes36.json", "w") as JSONFile:
    JSONFile.write(json.dumps(AllocMap, sort_keys = False, indent = 4))
