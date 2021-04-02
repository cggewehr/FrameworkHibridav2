import json

# AllocMap[PEPos] = $App.$Thread
AllocMap = [None] * 36

AllocMap[0] = ["BB_PIP.InpMemA", "MM_H264_60_A.MVPadding", "AA_MPEG4_A.IDCT", "HH_MPEG4.IDCT"]
AllocMap[1] = ["BB_PIP.HS", "MM_H264_60_A.MotionEstimation", "AA_MPEG4_A.SRAM2", "HH_MPEG4.SRAM2"]
AllocMap[2] = ["AA_MPEG4_A.RISC", "HH_MPEG4.RISC"]
AllocMap[3] = ["BB_H264_30.VideoIn", "MM_H264_60_B.SampleHold", "AA_MPEG4_B.IDCT", "HH_H264_60.VideoIn"]
AllocMap[4] = ["BB_H264_30.MVPadding", "MM_H264_60_B.DeblockingFilter", "AA_MPEG4_B.RISC", "HH_H264_60.MVPadding"]
AllocMap[5] = ["BB_H264_30.StreamOut", "AA_VOPD.ARM", "HH_H264_60.StreamOut"]
AllocMap[6] = ["BB_PIP.JUG1", "MM_H264_60_A.ChromaResampler", "HH_MPEG4.RAST", "HH_MPEG4.RAST"]
AllocMap[7] = ["BB_PIP.VS", "MM_H264_60_A.YUVGenerator", "AA_MPEG4_A.UpSample", "HH_MPEG4.UpSample"]
AllocMap[8] = ["BB_H264_30.ChromaResampler", "AA_MPEG4_B.RAST", "HH_H264_60.ChromaResampler"]
AllocMap[9] = ["BB_H264_30.YUVGenerator", "MM_H264_60_B.MotionCompensation", "AA_MPEG4_B.UpSample", "HH_H264_60.YUVGenerator"]
AllocMap[10] = ["BB_H264_30.MotionEstimation", "MM_H264_60_B.Predictor", "AA_MPEG4_B.SRAM2", "HH_H264_60.MotionEstimation"]
AllocMap[11] = ["BB_H264_30.EntropyEncoder", "MM_H264_60_B.StreamOut", "AA_MPEG4_B.BAB", "HH_H264_60.EntropyEncoder"]
AllocMap[12] = ["BB_MWD.SE", "MM_H264_60_A.DCT", "AA_MPEG4_A.AU", "HH_MPEG4.AU"]
AllocMap[13] = ["BB_MWD.VS", "MM_H264_60_A.VideoIn", "AA_MPEG4_A.SDRAM", "HH_MPEG4.SDRAM"]
AllocMap[14] = ["BB_MWD.HS", "AA_VOPD.StripeMem"]
AllocMap[15] = ["BB_H264_30.MotionCompensation", "MM_H264_60_B.VideoIn", "AA_MPEG4_B.SDRAM", "HH_H264_60.MotionCompensation"]
AllocMap[16] = ["BB_H264_30.DCT", "MM_H264_60_B.DCT", "AA_MPEG4_B.AU", "HH_H264_60.DCT"]
AllocMap[17] = ["BB_H264_30.SampleHold", "MM_H264_60_B.EntropyEncoder", "AA_MPEG4_B.SRAM1", "HH_H264_60.SampleHold"]
AllocMap[18] = ["BB_MWD.MEM3", "MM_H264_60_A.Predictor", "AA_VOPD.VLD", "HH_PIP.InpMemA"]
AllocMap[19] = ["BB_MWD.JUG1", "MM_H264_60_A.MotionCompensation", "AA_VOPD.AcdcPred", "HH_PIP.InpMemB"]
AllocMap[20] = ["BB_MWD.IN", "AA_VOPD.IQuan", "HH_PIP.JUG2"]
AllocMap[21] = ["BB_H264_30.Predictor", "MM_H264_60_B.YUVGenerator", "AA_VOPD.Pad", "HH_H264_60.Predictor"]
AllocMap[22] = ["BB_H264_30.DeblockingFilter", "MM_H264_60_B.ChromaResampler", "AA_VOPD.VopMem", "HH_H264_60.DeblockingFilter"]
AllocMap[23] = ["BB_H264_30.IDCT", "MM_H264_60_B.IDCT", "AA_MPEG4_B.MedCPU", "HH_H264_60.IDCT"]
AllocMap[24] = ["BB_MWD.JUG2", "MM_H264_60_A.DeblockingFilter", "AA_VOPD.RunLeDec", "HH_PIP.HS"]
AllocMap[25] = ["BB_MWD.HVS", "MM_H264_60_A.SampleHold", "AA_VOPD.InvScan", "HH_PIP.VS"]
AllocMap[26] = ["BB_MWD.MEM2", "AA_VOPD.IDCT", "HH_PIP.JUG1"]
AllocMap[27] = ["BB_MWD.NR", "MM_H264_60_B.MotionEstimation", "AA_VOPD.UpSample", "HH_PIP.MEM"]
AllocMap[28] = ["BB_MWD.MEM1", "MM_H264_60_B.MVPadding", "AA_VOPD.VopRed", "HH_PIP.OpDisp"]
AllocMap[29] = ["BB_H264_30.IQ", "MM_H264_60_B.IQ", "AA_MPEG4_B.ADSP", "HH_H264_60.IQ"]
AllocMap[30] = ["BB_MWD.Blend", "MM_H264_60_A.Quantization", "AA_MPEG4_A.VU", "HH_MPEG4.VU"]
AllocMap[31] = ["BB_PIP.InpMemB", "MM_H264_60_A.IQ", "AA_MPEG4_A.ADSP", "HH_MPEG4.ADSP"]
AllocMap[32] = ["BB_PIP.JUG2", "MM_H264_60_A.IDCT", "AA_MPEG4_A.MedCPU", "HH_MPEG4.MedCPU"]
AllocMap[33] = ["BB_PIP.MEM", "MM_H264_60_A.EntropyEncoder", "AA_MPEG4_A.SRAM1", "HH_MPEG4.SRAM1"]
AllocMap[34] = ["BB_PIP.OpDisp", "MM_H264_60_A.StreamOut", "AA_MPEG4_A.BAB", "HH_MPEG4.BAB"]
AllocMap[35] = ["BB_H264_30.Quantization", "MM_H264_60_B.Quantization", "AA_MPEG4_B.VU", "HH_H264_60.Quantization"]

AllocJSONString = json.dumps(AllocMap, sort_keys = False, indent = 4)

with open("SetupBB36.json", "w") as JSONFile:
    JSONFile.write(AllocJSONString)

