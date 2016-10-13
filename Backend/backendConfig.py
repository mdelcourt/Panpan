
class backendConfig:

  squareCol = [128,255,128]
  squareMinSize = 10

  bkgEstim  = "Average" #Can be Average or Peak
  nSigmaBkg = 3	#Number of sigma to cut bkg

  lumiThresh = 50
  nTrend = 3	#Number of consecutive pixels needed for trend


  peakMergeThresh  = 0.75 		#max prop of average peak size for peak merging
  peakAfterMergeThresh  = 1.50		#max prop size after merging

  useRoot = False #use ROOT library or not. If not, no ROOT images generated
  debug = True
  useNumpy = True
